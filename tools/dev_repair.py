#!/usr/bin/env python3
"""Run the frozen six-pair development diagnostic, with a persistent 12-call cap.

Codex only. Reuses saved reference responses. No schema/transport retries, holdout,
Claude, or absolute grader calls. Reruns reuse successful artifacts and cannot
repeat a failed request. Private CLI envelopes stay under .local/.
"""
import argparse, concurrent.futures, hashlib, json, time
from pathlib import Path
import bench, pairwise

ROOT=Path(__file__).resolve().parents[1]

def main(pilot='dev-repair-1'):
 if pilot not in ('dev-repair-1','dev-repair-2'):raise ValueError('Unknown authorized pilot')
 public=ROOT/'evals/results'/pilot; work=ROOT/'.local'/pilot
 plan=json.loads((public/'plan.json').read_text())
 assert plan['provider']=='codex' and plan['call_cap']==12 and len(plan['pairs'])==6
 skill=bench.bundle(ROOT/'evals/versions'/plan['candidate'])
 assert pairwise.text_hash(skill)==plan['skill_sha256']
 assert pairwise.text_hash(pairwise.RUBRIC.read_text())==plan['rubric_sha256']
 if 'proof_sha256' in plan:
  for filename,key in [('proofs.md','proof_sha256'),('paper-voice.md','paper_voice_sha256')]:
   assert pairwise.text_hash((ROOT/'evals/versions'/plan['candidate']/'references'/filename).read_text())==plan[key]
 cases={c['id']:c for c in json.loads((ROOT/'evals/large/development.json').read_text())['cases']}
 # Only the six frozen development references enter generation or judging.
 refs={(r['case'],r['config']):r for r in json.loads((ROOT/'evals/results/large-interim/responses.json').read_text()) if r['arm']==plan['reference'] and r['split']=='development'}
 for p in plan['pairs']:
  c=cases[p['case']]; assert c['subset']=='tune'
  assert pairwise.text_hash(c['task'])==p['task_sha256']
  assert pairwise.text_hash(refs[(p['case'],p['config'])]['response'])==p['reference_sha256']
  assert bench.CONFIGS[p['config']][0]=='codex'
 original=bench.call
 def capped_call(prompt,config,timeout=900):
  if bench.CONFIGS[config][0]!='codex':raise RuntimeError('Claude calls forbidden')
  key=pairwise.digest([prompt,config])
  with pairwise.locked(work/'budget-lock'):
   file=work/'calls.json'; ledger=json.loads(file.read_text()) if file.exists() else []
   if len(ledger)>=12:raise RuntimeError('12-call cap reached')
   if any(r['request']==key for r in ledger):raise RuntimeError('No retries: request already attempted')
   ledger.append(dict(request=key,config=config,started=time.time(),state='started'))
   pairwise.save_json(file,ledger)
  try:
   result=original(prompt,config,timeout=timeout); status=dict(state='answered',usage=result[1].get('usage',{}))
  except Exception:
   status=dict(state='failed');raise
  finally:
   with pairwise.locked(work/'budget-lock'):
    ledger=json.loads(file.read_text());next(r for r in ledger if r['request']==key).update(status);pairwise.save_json(file,ledger)
  return result
 bench.call=capped_call;pairwise.MAX_SCHEMA_ATTEMPTS=1
 def one(p):
  cid,cfg=p['case'],p['config'];c=cases[cid]
  try:
   print(bench.run_one(c,cfg,plan['candidate'],skill,work/'runs'),flush=True)
   response=(work/'runs'/cid/cfg/plan['candidate']/'response.md').read_text()
   record=pairwise.grade_pair(c,refs[(cid,cfg)]['response'],response,plan['judge'],out=work/'pairs',config=cfg,left_id=plan['reference'],right_id=plan['candidate'],seed=plan['seed'])
   print(cid,cfg,record['outcome'],flush=True)
   return dict(case=cid,config=cfg,state='complete')
  except Exception as exc:
   # Raw exception may include local paths or CLI details; retain privately.
   pairwise.save_json(work/(cid+'-error.json'),dict(error=repr(exc)))
   print(cid,cfg,'incomplete; details private',flush=True)
   return dict(case=cid,config=cfg,state='incomplete')
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  outcomes=list(pool.map(one,plan['pairs']))
 pairwise.save_json(work/'status.json',outcomes)
 print('Finished;',len(json.loads((work/'calls.json').read_text())),'Codex calls; zero Claude calls',flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pilot',choices=['dev-repair-1','dev-repair-2'],required=True)
 main(parser.parse_args().pilot)
