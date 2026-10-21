#!/usr/bin/env python3
"""One user-authorized capacity retry plus the 34 unrun jobs; reuse frozen inputs."""
import argparse,json
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
from pathlib import Path
import restored_check as r
from restored_check import lh,pairwise
FAILED='large-dev-b-14--astra-high'
AMEND=r.OUT/'continuation-plan.json'
ORIG_DIRECTORY=r.directory
ORIG_RESERVATION=r.reservation
ORIG_LEDGER=r.ledger

def freeze():
    lh.require(not AMEND.exists(),'Already authorized/frozen')
    p,_=r.load();rows=ORIG_LEDGER(p)
    lh.require(len(rows)==66 and all(x['finished'] for x in rows),'Original stop changed')
    failed=[x for x in rows if not x['completed']]
    lh.require(len(failed)==1 and failed[0]['id']==FAILED and not failed[0]['known'],'Unexpected failure')
    files={}
    for j in p['jobs']:
        d=ORIG_DIRECTORY(j)
        for name in ('request.json','result.json','answer.txt','accepted.json','invalid.json','cli.jsonl','cli.json','stderr.txt','failure.json'):
            q=d/name
            if q.exists():files[f'{j["stage"]}/{j["id"]}/{name}']=lh.hashed(q)
    remaining=[j['id'] for j in p['jobs'] if not ORIG_RESERVATION(j).exists()]
    lh.require(len(remaining)==34,'Remaining job count changed')
    a=dict(original_plan_sha256=p['plan_sha256'],authorization='User approved 101 total calls, retrying the capacity-failed Astra generation and completing the remaining cases, reusing all completed work and leaving fresh holdouts untouched.',failed_job=FAILED,remaining_jobs=remaining,max_calls=101,max_generations=61,max_judges=40,max_new_calls=35,original_calls=66,token_guard=p['token_guard'],codex_credit_guard=p['codex_credit_guard'],original_failed_attempt=failed[0],preserved_files=files,runner_sha256=lh.hashed(Path(__file__)),finisher_sha256=lh.hashed(r.ROOT/'tools/finish_restored_check.py'),unknown_usage_policy='Only the already-known capacity failure is exempted from the stop rule; retain its 30000-token/8-credit reservation, never report it as zero usage. Any new unknown usage stops scheduling. One replacement attempt only.')
    a['sha256']=pairwise.digest(a);lh.public_safe(a);lh.write(AMEND,a)
    print('Frozen continuation: 35 new calls maximum, 101 total.')

def load():
    p,c=r.load();a=lh.read(AMEND)
    lh.require(a['sha256']==pairwise.digest({k:v for k,v in a.items() if k!='sha256'}),'Amendment changed')
    lh.require(a['original_plan_sha256']==p['plan_sha256'],'Original plan mismatch')
    lh.require(a['runner_sha256']==lh.hashed(Path(__file__)) and a['finisher_sha256']==lh.hashed(r.ROOT/'tools/finish_restored_check.py'),'Continuation code changed')
    for name,h in a['preserved_files'].items():lh.require(lh.hashed(r.WORK/name)==h,'Completed evidence changed')
    return p,c,a

def directory(j):return r.WORK/'retry-generation'/j['id'] if j['id']==FAILED else ORIG_DIRECTORY(j)
def reservation(j):return r.WORK/'retry-reservations'/(j['id']+'.json') if j['id']==FAILED else ORIG_RESERVATION(j)
def ledger(p):
    rows=ORIG_LEDGER(p)
    old=dict(lh.read(AMEND)['original_failed_attempt'],id=FAILED+'--original-capacity-failure')
    return [old]+rows

def setup():
    r.directory=directory;r.reservation=reservation;r.ledger=ledger

def allowed(p,j,rows):
    # The user-authorized old capacity failure remains charged at its reservation.
    if any(x['finished'] and not x['known'] and x['id']!=FAILED+'--original-capacity-failure' for x in rows):return False
    tok,cred=r.reserve(p,j)
    return (len(rows)<101 and sum(x['stage']==j['stage'] for x in rows)<(61 if j['stage']=='generation' else 40) and sum(x['charged_tokens'] for x in rows)+tok<=p['token_guard'] and sum(x['codex_credits'] for x in rows)+cred<=p['codex_credit_guard'] and (j.get('config')!='sonnet-high' or sum(x['config']=='sonnet-high' for x in rows)<20))

def execute(j):
    load();setup();return r.execute(j)

def run():
    p,c,a=load();setup()
    with pairwise.locked(r.WORK):
        lh.require(all(x['finished'] for x in ledger(p)),'Unfinished attempt: do not replay')
        retry=next(j for j in p['jobs'] if j['id']==FAILED)
        # Try the explicitly requested Astra replacement before spending on the rest.
        if not reservation(retry).exists():
            lh.require(allowed(p,retry,ledger(p)),'Budget reached')
            lh.write(reservation(retry),dict(plan_sha256=p['plan_sha256'],job=retry))
            print(execute(retry),flush=True)
        with ProcessPoolExecutor(max_workers=p['max_workers']) as pool:
            active={}
            while True:
                texts=r.texts_for(p,c);rows=ledger(p)
                for j in p['jobs']:
                    if len(active)>=p['max_workers']:break
                    if reservation(j).exists():continue
                    lh.require(j['id'] in a['remaining_jobs'],'Unexpected new job')
                    if j['stage']=='judge' and not all((j['case'],e['config'],r.CAND) in texts for e in j['pairs']):continue
                    if not allowed(p,j,rows):continue
                    lh.write(reservation(j),dict(plan_sha256=p['plan_sha256'],job=j));active[pool.submit(execute,j)]=j;rows=ledger(p)
                if not active:break
                done,_=wait(active,timeout=5,return_when=FIRST_COMPLETED)
                for f in done:
                    j=active.pop(f);message=f.result();rows=ledger(p)
                    print(json.dumps(dict(job=message,calls=len(rows),finished=sum(x['finished'] for x in rows),known_tokens=sum(x['reported_tokens'] or 0 for x in rows))),flush=True)
    report()

def report():
    p,c,a=load();setup();r.report()
    usage=lh.read(r.OUT/'usage.json');usage.update(call_cap=101,continuation_calls=usage['calls']-66,authorized_retries=1,continuation_plan_sha256=a['sha256']);lh.write(r.OUT/'usage.json',usage)
    import finish_restored_check as f
    f.finish()
    # The original report and quote validator refer to the preserved plan; this note records the authorized execution amendment.
    path=r.OUT/'report.md';s=path.read_text();s+='\nExecution amendment: one user-authorized Astra capacity retry, 101 total attempts maximum. The original failed attempt and all completed evidence were preserved. The 2.5M-token and 300-credit scheduling guards include a 30,000-token/8-credit reservation for its unreported usage. See continuation-plan.json.\n';path.write_text(s)
    print(json.dumps({k:usage[k] for k in ('calls','continuation_calls','known_reported_tokens','codex_paid_credit_equivalent','unknown_attempts')}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','run','report']);args=p.parse_args();globals()[args.action]()
