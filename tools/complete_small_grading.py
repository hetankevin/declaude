#!/usr/bin/env python3
"""Authorized two-call completion of saved drafts; no generation entrypoint."""
import argparse
import json
import long_horizon as lh
import pairwise
import prose_repair as prior
import small_repair as small
import grade_long_horizon as transport

WORK=small.WORK/'completion-20261020'
MANIFEST=small.OUT/'grading-completion.json'
IDS=('large-dev-a-12-primary','large-dev-b-14-primary')


def inputs():
    plan,cases,texts,rubric=small.load()
    small.generations(plan,cases,texts,run=False)
    jobs=[j for j in plan['jobs'] if j['id'] in IDS]
    lh.require(len(jobs)==2 and all(j['order']=='primary' for j in jobs),'Wrong scope')
    payloads={j['id']:prior.request(j,rubric,cases,texts)[0] for j in jobs}
    immutable={'responses.json':lh.hashed(small.OUT/'responses.json'),'bundle.txt':lh.hashed(small.OUT/'bundle.txt'),'rubric.txt':lh.hashed(small.OUT/'rubric.txt'),'cases.json':lh.hashed(small.OUT/'cases.json'),'original_plan.json':lh.hashed(small.OUT/'plan.json')}
    manifest=dict(date='2026-10-20',authorization='Finish grading saved drafts cheaply; regenerate nothing.',judge=small.JUDGE,max_new_calls=2,retries=0,soft_token_guard=50000,reservation_tokens=25000,jobs=list(IDS),prompt_sha256={k:pairwise.text_hash(v) for k,v in payloads.items()},frozen=immutable,skip='Completed museum comparison and reversed-order audit. Both holdouts remain sealed.',old_failed_attempt='Retained unchanged. This explicitly authorized completion uses separate attempt directories.')
    return plan,cases,texts,rubric,jobs,payloads,manifest


def freeze():
    *_,manifest=inputs()
    lh.require(not MANIFEST.exists(),'Completion already frozen')
    lh.write(MANIFEST,manifest)
    print('Two judge calls frozen; zero writing calls.')


def run():
    plan,cases,texts,rubric,jobs,prompts,manifest=inputs()
    lh.require(lh.read(MANIFEST)==manifest,'Frozen completion inputs changed')
    with pairwise.locked(WORK):
        for job in jobs:
            d=WORK/job['id']
            if (d/'request.json').exists():
                lh.require(lh.read(d/'request.json')['prompt']==prompts[job['id']],'Cached prompt changed')
                lh.require((d/'result.json').exists(),'Unfinished attempt; do not replay')
                continue
            started=list(WORK.glob('*/request.json'))
            used=0
            for p in started:
                r=lh.read(p.with_name('result.json'))
                lh.require(r['reported_tokens'] is not None,'Missing usage; stop')
                lh.require(lh.hashed(p.with_name('cli.jsonl'))==r['cli_sha256'],'Usage evidence changed')
                used+=r['reported_tokens']
            if len(started)>=2 or used+25000>50000:break
            raw=transport.call(prompts[job['id']],d,{'judge':small.JUDGE})
            try:
                records=prior.records_for(job,raw,1,rubric,cases,texts,plan)
                lh.write(d/'accepted.json',records)
                print(job['id']+': '+','.join(r['outcome'] for r in records),flush=True)
            except (ValueError,KeyError,TypeError) as exc:
                lh.write(d/'invalid.json',{'error':str(exc)})
                print(job['id']+': invalid, retained without retry',flush=True)
    lh.require(inputs()[-1]==manifest,'Writing artifacts changed during grading')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['freeze','run']);a=parser.parse_args();globals()[a.action]()
