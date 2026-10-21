#!/usr/bin/env python3
"""One transport recovery per sandbox-blocked attempt; frozen scientific inputs."""
import argparse
from pathlib import Path
import v10_check as v
from v10_check import lh,pairwise,r
FAILED=('large-dev-a-06--sonnet-high','large-dev-a-08--sol-low')
AMEND=v.OUT/'transport-amendment.json'
DIR=r.directory;RES=r.reservation;LEDGER=r.ledger;STATS=v.prior.net_stats

def freeze():
    v.setup();p,c=v.load();rows=LEDGER(p)
    assert len(rows)==2 and {x['id'] for x in rows}==set(FAILED) and all(x['finished'] and not x['completed'] for x in rows)
    files={str(f.relative_to(v.WORK)):lh.hashed(f) for name in FAILED for f in (v.WORK/'generation'/name).rglob('*') if f.is_file() and f.name in ('request.json','result.json','failure.json','cli.json','cli.jsonl','stderr.txt')}
    # Claude explicitly reports zero API time, empty model usage, and no login.
    raw=lh.read(v.WORK/'generation'/FAILED[0]/'cli.json')
    import json
    envelope=json.loads(raw['stdout'])
    assert envelope['duration_api_ms']==0 and not envelope['modelUsage'] and 'Not logged in' in envelope['result']
    rows[0 if rows[0]['id']==FAILED[0] else 1].update(known=True,reported_tokens=0,charged_tokens=0,codex_credits=0,credit_is_reservation=False)
    a=dict(original_plan_sha256=p['plan_sha256'],reason='Sandbox blocked Claude authentication and Codex workspace routing before any drafts. Auth verified outside sandbox. Retry each once with network access; no quality regeneration.',max_process_attempts=25,planned_model_calls=23,max_new_retries=2,failed_jobs=list(FAILED),old_attempts=rows,preserved=files,token_guard=700000,codex_credit_guard=90,unknown_usage_policy='Original Codex failure retains30k-token/3-credit reservation. Any new unknown failure stops. Claude explicitly reports zero API usage.',runner_sha256=lh.hashed(Path(__file__)))
    a['sha256']=pairwise.digest(a);lh.public_safe(a);lh.write(AMEND,a)

def load():
    p,c=v.load();a=lh.read(AMEND)
    assert a['sha256']==pairwise.digest({k:x for k,x in a.items() if k!='sha256'})
    assert a['runner_sha256']==lh.hashed(Path(__file__))
    for n,h in a['preserved'].items():lh.require(lh.hashed(v.WORK/n)==h,'Original failure changed')
    return p,c

def directory(j):return v.WORK/'network-retry'/j['id'] if j['id'] in FAILED else DIR(j)
def reservation(j):return v.WORK/'network-reservations'/(j['id']+'.json') if j['id'] in FAILED else RES(j)
def ledger(p):return [dict(x,id=x['id']+'--sandbox-failure') for x in lh.read(AMEND)['old_attempts']]+LEDGER(p)
def allowed(p,j,rows):
    if any(x['finished'] and not x['known'] and not x['id'].endswith('--sandbox-failure') for x in rows):return False
    tok,cred=r.reserve(p,j)
    return len(rows)<25 and sum(x['stage']==j['stage'] for x in rows)<(15 if j['stage']=='generation' else 10) and sum(x['charged_tokens'] for x in rows)+tok<=700000 and sum(x['codex_credits'] for x in rows)+cred<=90 and (j.get('config')!='sonnet-high' or sum(x['config']=='sonnet-high' for x in rows)<8)
def stats(rows,*args,**kwargs):return STATS(rows,*args,**kwargs) if rows else {'judgments':0,'wins':0,'ties':0,'losses':0,'net_pp':None}
def setup():
    v.setup();r.directory=directory;r.reservation=reservation;r.ledger=ledger;r.allowed=allowed;r.load=load;r.execute=execute;r.report=report;v.prior.net_stats=stats

def execute(j):setup();return v.ORIGINAL_EXEC(j)
def report():
    v.report()
    u=lh.read(v.OUT/'usage.json');u['process_attempt_cap']=25;u['planned_model_calls']=23;u['transport_retries']=2;lh.write(v.OUT/'usage.json',u)
    p=v.OUT/'report.md';s=p.read_text().replace('/23 attempts','/25 process attempts').replace('/7 Claude calls','/8 Claude attempts (one failed before API use)')
    s+='\nTransport amendment: two sandbox failures preserved, retried once with network access. 23 planned model calls, at most25 CLI process attempts. Original Codex failure charged30k tokens/3 credits for unknown usage; Claude reports zero API usage. Scientific inputs unchanged. Use python3 tools/v10_network.py report to reproduce.\n';p.write_text(s)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','run','report']);a=p.parse_args()
    if a.action=='freeze':freeze()
    else:
        setup()
        if a.action=='run':r.run()
        else:report()
