#!/usr/bin/env python3
"""Disclosed local-launch repair. Preserve the original freeze and all attempts.

The failed /usr/bin/env launcher exited127 before starting Node or a model.
Its invocation still counts toward the cap. Only that proven pre-model failure
is exempt from the unknown-usage stop; all real model failures still stop work.
"""
import argparse
import json
import os
import shutil
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path
import scholarly_full as suite
import long_horizon as lh
import pairwise

BASE_LOAD = suite.load
BASE_ENV = lh.environment
FAILED = 'large-dev-a-01--astra-medium--scholarly-20261103'
RETRY = FAILED + '--node-path-repair'
PLAN = suite.OUT / 'runtime-plan.json'


def verify_local_failure():
    d = suite.WORK / 'calls' / FAILED
    r = lh.read(d / 'result.json')
    lh.require(r['exit_code'] == 127 and not (d / 'cli.jsonl').read_bytes()
               and (d / 'stderr.txt').read_text().strip() == 'env: node: No such file or directory',
               'Not the exact verified pre-model launch failure')
    return {p.name: lh.hashed(p) for p in d.iterdir() if p.is_file()}


def freeze():
    lh.require(not PLAN.exists(), 'Runtime amendment already frozen')
    p, _ = BASE_LOAD()
    failed = next(j for j in p['jobs'] if j['id'] == FAILED)
    q = dict(p, parent_plan_sha256=p['plan_sha256'], jobs=p['jobs'] + [dict(failed, id=RETRY)],
             launch_repair=dict(failed_job=FAILED, replacement_job=RETRY, evidence=verify_local_failure(),
                                accounting='Original CLI launch counts as one attempt and zero model tokens: env exited127 before Node started. No successful output was regenerated.',
                                change='Prepend the installed Node executable directory to the isolated PATH. No auth, guidance, model, prompt, rubric or sandbox change.'),
             scripts=dict(p['scripts'], **{'scholarly_runtime.py': lh.hashed(Path(__file__))}))
    q['plan_sha256'] = pairwise.digest({k:v for k,v in q.items() if k != 'plan_sha256'})
    lh.write(PLAN, q)
    print('Frozen local launch repair; total planned CLI attempts:', len(q['jobs']))


def load():
    p, cases = BASE_LOAD(); q = lh.read(PLAN)
    lh.require(q['parent_plan_sha256'] == p['plan_sha256'], 'Parent plan changed')
    lh.require(q['plan_sha256'] == pairwise.digest({k:v for k,v in q.items() if k != 'plan_sha256'}), 'Runtime plan changed')
    lh.require(q['launch_repair']['evidence'] == verify_local_failure(), 'Failure evidence changed')
    for n,h in q['scripts'].items(): lh.require(lh.hashed(suite.ROOT/'tools'/n) == h, 'Code changed')
    lh.require((q['max_calls'],q['token_guard'],q['max_claude_calls']) == (1600,50000000,557), 'Approved caps changed')
    return q, cases


def environment(d):
    node = shutil.which('node')
    lh.require(node is not None, 'Installed Node unavailable')
    env = BASE_ENV(d)
    env['PATH'] = str(Path(node).parent) + os.pathsep + env['PATH']
    return env


def ledger(plan):
    rows=[]
    for job in plan['jobs']:
        if not suite.reservation(job).exists(): continue
        saved=lh.read(suite.reservation(job))
        lh.require(saved['plan_sha256'] in (plan['plan_sha256'],plan['parent_plan_sha256']) and saved['job']==job,'Reservation mismatch')
        d=suite.directory(job); r=lh.read(d/'result.json') if (d/'result.json').exists() else None
        known = r is not None and type(r.get('reported_tokens')) is int and r['reported_tokens'] >= 0
        if r and r.get('cli_sha256'):
            lh.require(lh.hashed(d/('cli.jsonl' if (d/'cli.jsonl').exists() else 'cli.json'))==r['cli_sha256'],'Raw evidence changed')
        pre_model=job['id']==FAILED
        if pre_model: verify_local_failure()
        tokens=0 if pre_model else r['reported_tokens'] if known else None
        rows.append(dict(id=job['id'],stage=job['stage'],claude=suite.is_claude(job),finished=r is not None,
                         known=known or pre_model,completed=bool(r and r.get('completed')),failed=(d/'failure.json').exists(),
                         verified_pre_model_failure=pre_model,reported_tokens=tokens,
                         charged_tokens=tokens if tokens is not None else plan['reservations'][job['stage']]))
    return rows


def allowed(plan,job,rows):
    return (not any(r['finished'] and (not r['known'] or not r['completed'] or r['failed']) and not r['verified_pre_model_failure'] for r in rows)
            and len(rows)<plan['max_calls']
            and (not suite.is_claude(job) or sum(r['claude'] for r in rows)<plan['max_claude_calls'])
            and sum(r['charged_tokens'] for r in rows)+plan['reservations'][job['stage']]<=plan['token_guard'])


def install_adapter():
    suite.load=load; suite.ledger=ledger; suite.allowed=allowed; lh.environment=environment


def worker(job):
    install_adapter()
    return suite.execute(job)


def run(smoke=False):
    install_adapter(); plan,cases=load()
    with pairwise.locked(suite.WORK):
        lh.require(all(r['finished'] for r in ledger(plan)), 'Unfinished reservation: inspect without replay')
        smoke_jobs=[next(j for j in plan['jobs'] if j['stage']=='generation' and j['config']==cfg and j['arm']==suite.CAND) for cfg in suite.CONFIGS]
        smoke_jobs=[next(j for j in plan['jobs'] if j['id']==RETRY) if j['id']==FAILED else j for j in smoke_jobs]
        smoke_ids={j['id'] for j in smoke_jobs}
        if not smoke:
            lh.require(smoke_ids <= {r['id'] for r in ledger(plan) if r['completed'] and not r['failed']}, 'Ten-config smoke incomplete')
        jobs=smoke_jobs if smoke else plan['jobs']
        workers=1 if smoke else plan['max_workers']
        with ProcessPoolExecutor(max_workers=workers) as pool:
            active={}
            while True:
                rows=ledger(plan); done={r['id'] for r in rows if r['completed'] and not r['failed']}
                texts=suite.texts_for(plan,cases)
                for job in jobs:
                    if len(active)>=workers: break
                    if suite.reservation(job).exists() or not suite.ready(job,texts,done) or not allowed(plan,job,rows): continue
                    lh.write(suite.reservation(job),dict(plan_sha256=plan['plan_sha256'],job=job))
                    active[pool.submit(worker,job)]=job; rows=ledger(plan)
                if not active: break
                finished,_=wait(active,timeout=5,return_when=FIRST_COMPLETED)
                for future in finished:
                    job=active.pop(future)
                    try: future.result()
                    except Exception as exc:
                        d=suite.directory(job)
                        if not (d/'result.json').exists(): lh.write(d/'result.json',dict(completed=False,reported_tokens=None))
                        lh.write(d/'failure.json',dict(error=repr(exc)))
                    rows=ledger(plan)
                    print(json.dumps(dict(job=job['id'],calls=len(rows),tokens=sum(r['reported_tokens'] or 0 for r in rows),
                                          model_failures=sum(r['finished'] and (r['failed'] or not r['completed']) and not r['verified_pre_model_failure'] for r in rows))),flush=True)
        suite.report()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','smoke','run','report']);a=p.parse_args()
    if a.action=='freeze': freeze()
    elif a.action=='report': install_adapter();suite.report()
    else: run(smoke=a.action=='smoke')
