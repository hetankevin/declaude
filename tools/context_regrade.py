#!/usr/bin/env python3
"""Frozen, Codex-only regrading of saved responses. Never generates writing."""
import argparse,collections,concurrent.futures,hashlib,json,random,time
from pathlib import Path
import bench,pairwise

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'evals/results/context-regrade'
WORK=ROOT/'.local/context-regrade'
JUDGES={'astra-high':('codex','gpt-6-astra','high'),'sol-high':('codex','gpt-6.1-sol','high')}
SEED='declaude-context-regrade-1'
CONTEXT={
 'common':"The author asked for prose that follows their established writing preferences, not generic polished AI prose. Their recurring directions are to keep the big picture, explain why each construction is needed, and make the reasoning readable in order. They distinguish removing rhetorical repetition from compressing useful explanation. They want fidelity to the requested contribution and artifact form. Current task-specific instructions and audience take precedence. Do not infer personality, diagnoses, or private background.",
 'ordinary':"For this ordinary document, judge whether the intended reader can understand and use it. Preserve its register, purposeful details, and appropriate organization. The author's research-writing preferences do not require imposing a research introduction on a notice. Useful headings and related paragraph groups are allowed only as the request permits.",
 'research':"The author repeatedly asks why a construction is needed before its mechanics and contributions are announced. They prefer connected technical prose that introduces an object with its purpose, shows the relevant obstacle, and explains what the result enables. Preserve precise scope and meaningful qualifications without repeated defensive commentary. Do not import facts from a tone sample.",
 'argument':"The author wants the reasons and objections to form an argument the reader can follow, not a catalogue of claims or slogans. Keep real tradeoffs and limitations. Do not make the claim stronger to create a more satisfying story. Respect the supplied register and proposed conclusion.",
 'proof':"The author's explicit direction is to use displaystyle mathematics with the steps laid out cleanly, without skipping steps. They dislike long paragraphs of inline mathematics that conceal the derivation and do not want proof steps skipped to meet a length target. Explain why the operations follow, retain the actual mathematical objects and assumptions, and keep short symbol references inline. Preserve the task's required proof strategy.",
 'control':"This task bounds the editing scope. The author wants established voice, deliberate humor, and already-effective passages preserved. Changing good writing merely to demonstrate effort is not a benefit. Apply exactly the changes requested, and retain distinct scientifically or practically meaningful qualifications."
}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):pairwise.save_json(p,v)

def inputs():
 cases={c['id']:c for split in ['development','holdout'] for c in json.loads((ROOT/f'evals/large/{split}.json').read_text())['cases']}
 rows=json.loads((ROOT/'evals/results/large-interim/responses.json').read_text())
 texts={(r['case'],r['config'],r['arm']):r['response'] for r in rows}
 for folder,arm in [('dev-repair-1','v6-dev'),('dev-repair-2','v7-dev')]:
  for r in json.loads((ROOT/f'evals/results/{folder}/responses.json').read_text()):texts[r['case'],r['config'],arm]=r['candidate']
 for c in cases.values():
  c['user_context']=CONTEXT['common']+'\n\n'+CONTEXT[c['category']]
  c['is_proof']=c['category']=='proof'
 return cases,texts

def make_jobs(cases,texts):
 pairs=sorted((cid,cfg,arm) for cid,cfg,arm in texts if arm!='none' and (cid,cfg,'none') in texts)
 grouped=collections.defaultdict(list)
 for cid,cfg,arm in pairs:grouped[cid].append((cid,cfg,arm))
 jobs=[]
 for judge in JUDGES:
  for cid,ps in sorted(grouped.items()):
   ordered=sorted(ps,key=lambda p:pairwise.digest([SEED,judge,p,'position']))
   base={p:('left','right')[i%2] for i,p in enumerate(ordered)}
   for order in ['primary','reversed']:
    selected=[p for p in ordered if order=='primary' or int(pairwise.digest([SEED,p,'audit']),16)/2**256<.1]
    # Same case in each batch; grouping is frozen and opaque to the judge.
    for start in range(0,len(selected),6):
     chunk=selected[start:start+6]
     entries=[]
     for i,p in enumerate(chunk):
      side=base[p] if order=='primary' else ('right' if base[p]=='left' else 'left')
      entries.append(dict(case=p[0],config=p[1],candidate=p[2],reference='none',a_side=side,label=f'P{i+1:02}'))
     job=dict(judge=judge,case=cid,order=order,pairs=entries)
     job['id']=pairwise.digest(job)[:24];jobs.append(job)
 jobs.sort(key=lambda j:pairwise.digest([SEED,j['id'],'queue']))
 return jobs

def freeze():
 if (PUBLIC/'plan.json').exists():raise RuntimeError('Plan exists; do not overwrite')
 PUBLIC.mkdir(parents=True,exist_ok=True)
 # This is the already-prepared rubric, not a rubric tuned on regrade results.
 source=ROOT/'evals/graders/pairwise-v2-draft.txt';rubric=PUBLIC/'rubric.txt';rubric.write_bytes(source.read_bytes())
 cases,texts=inputs();jobs=make_jobs(cases,texts)
 files=['evals/large/development.json','evals/large/holdout.json','evals/results/large-interim/responses.json','evals/results/dev-repair-1/responses.json','evals/results/dev-repair-2/responses.json']
 plan=dict(version=1,seed=SEED,judges=JUDGES,reference='none',candidates=['v4','v5a','v6-dev','v7-dev'],rubric_sha256=sha(rubric),context_sha256=pairwise.digest(CONTEXT),source_sha256={f:sha(ROOT/f) for f in files},pairs=sum(len(j['pairs']) for j in jobs if j['order']=='primary')//2,primary_judgments=sum(len(j['pairs']) for j in jobs if j['order']=='primary'),audit_judgments=sum(len(j['pairs']) for j in jobs if j['order']=='reversed'),batches=len(jobs),max_attempts_per_batch=2,batch_size=6,decision='Descriptive regrade of frozen responses. No skill or grader tuning during execution. Existing scores are retained. Primary comparisons use cases complete across all ten configurations and both judges; incomplete coverage is reported separately. Audits never enter performance.',limitations='The original holdout is a retrospective regrade, not a fresh validation of the revised judge. Both judges are Codex models. The rubric reflects explicit user preferences but has not been validated against independent human labels. Model choices remain fallible.',jobs=jobs)
 dump(PUBLIC/'plan.json',plan);dump(PUBLIC/'author-context.json',CONTEXT)
 print(json.dumps({k:plan[k] for k in ['pairs','primary_judgments','audit_judgments','batches']},indent=2))

def load():
 plan=json.loads((PUBLIC/'plan.json').read_text())
 assert plan['judges']=={k:list(v) for k,v in JUDGES.items()}
 for f,h in plan['source_sha256'].items():assert sha(ROOT/f)==h,(f,'changed')
 assert pairwise.digest(CONTEXT)==plan['context_sha256']
 rubric=(PUBLIC/'rubric.txt').read_text();assert pairwise.text_hash(rubric)==plan['rubric_sha256']
 cases,texts=inputs();assert make_jobs(cases,texts)==plan['jobs']
 return plan,rubric,cases,texts

def request(job,rubric,cases,texts):
 supplied=pairwise.supplied_case(cases[job['case']]);pairs={}
 for e in job['pairs']:
  t={'left':texts[e['case'],e['config'],'none'],'right':texts[e['case'],e['config'],e['candidate']]}
  pairs[e['label']]={'A':t[e['a_side']],'B':t['right' if e['a_side']=='left' else 'left']}
 # Exact A/B rubric applies independently within each anonymous pair.
 payload=dict(supplied,pairs=pairs)
 prompt=rubric+'\n\nBATCH OUTPUT ADAPTER: The input contains several independent anonymous A/B pairs for ONE task. Apply the entire rubric separately to each pair. Do not rank across pairs. Instead of one verdict object, return a JSON object mapping each pair ID to its full verdict object in the schema above. The pair IDs are arbitrary and reveal no model or condition. Each verdict quotes its own A/B texts. No pair may be omitted.\n\nINPUT_JSON:\n'+pairwise.canonical(payload)
 return prompt,supplied,pairs

def run_job(job,rubric,cases,texts,attempts):
 directory=WORK/job['id'];directory.mkdir(parents=True,exist_ok=True)
 prompt,supplied,pairs=request(job,rubric,cases,texts)
 fingerprint=pairwise.digest(dict(job=job,prompt=prompt))
 with pairwise.locked(directory):
  dump(directory/'request.json',dict(job=job,prompt=prompt,fingerprint=fingerprint))
  if (directory/'records.json').exists():return job['id'],'cached'
  for attempt in range(1,attempts+1):
   rawpath=directory/f'attempt-{attempt}.txt';statuspath=directory/f'attempt-{attempt}.json'
   if rawpath.exists():raw=rawpath.read_text()
   elif statuspath.exists():continue  # Failed/interrupted attempts are never silently repeated.
   else:
    dump(statuspath,dict(state='calling',judge=job['judge'],started=time.time()))
    try:
     assert bench.CONFIGS[job['judge']][0]=='codex'
     raw,meta=bench.call(prompt,job['judge'],timeout=1800)
     pairwise.atomic_write(rawpath,raw)
     dump(statuspath,dict(state='answered',call=meta,raw_sha256=pairwise.text_hash(raw)))
    except Exception as exc:
     dump(statuspath,dict(state='transport_error',error=repr(exc)))
     continue
   try:
    parsed=pairwise.parse_answer(raw)
    if set(parsed)!=set(pairs):raise pairwise.SchemaError('Missing or extra pair labels')
    records=[]
    for e in job['pairs']:
     per=dict(supplied,responses=pairs[e['label']])
     verdict,repairs=pairwise.repair_math_delimiter_quotes(parsed[e['label']],per)
     verdict=pairwise.validate_verdict(verdict,per)
     candidate_label='A' if e['a_side']=='right' else 'B'
     record=dict(version='context-regrade-v1',batch=job['id'],case=e['case'],config=e['config'],candidate=e['candidate'],reference='none',judge=job['judge'],order=job['order'],candidate_position=candidate_label,raw_judgment=verdict,**pairwise.normalized(verdict,candidate_label),response_sha256={arm:pairwise.text_hash(texts[e['case'],e['config'],arm]) for arm in ['none',e['candidate']]},prompt_sha256=pairwise.text_hash(prompt),rubric_sha256=pairwise.text_hash(rubric),context_sha256=pairwise.text_hash(supplied['user_context']),raw_sha256=pairwise.text_hash(raw),attempt=attempt,pair_id=e['label'],evidence_format_repairs=repairs)
     record['record_sha256']=pairwise.digest(record);records.append(record)
    dump(directory/'records.json',records)
    return job['id'],'done'
   except Exception as exc:
    dump(directory/f'attempt-{attempt}.invalid.json',dict(error=repr(exc)))
  return job['id'],'failed'

def run(workers,limit=None):
 plan,rubric,cases,texts=load();bench.CONFIGS.update(JUDGES)
 # Provider guard also protects against future accidental changes to callers.
 original=bench.call
 def codex_only(prompt,config,**kwargs):
  if config not in JUDGES or bench.CONFIGS[config][0]!='codex':raise RuntimeError('Only frozen Codex judges are allowed')
  return original(prompt,config,**kwargs)
 bench.call=codex_only
 jobs=plan['jobs'][:limit] if limit else plan['jobs']
 WORK.mkdir(parents=True,exist_ok=True);completed=collections.Counter()
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  futures={pool.submit(run_job,j,rubric,cases,texts,plan['max_attempts_per_batch']):j for j in jobs}
  for f in concurrent.futures.as_completed(futures):
   try:ident,state=f.result()
   except Exception as exc:
    ident=futures[f]['id'];state='failed';dump(WORK/(ident+'-exception.json'),dict(error=repr(exc)))
   completed[state]+=1
   print(sum(completed.values()),'/',len(jobs),dict(completed),ident,flush=True)
 dump(WORK/'last-run.json',dict(jobs=len(jobs),results=completed))
 if completed['failed']:raise SystemExit('Some batches failed; preserve available records and inspect errors before retrying')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['freeze','run']);p.add_argument('--workers',type=int,default=16);p.add_argument('--limit',type=int);a=p.parse_args()
 if a.action=='freeze':freeze()
 else:run(a.workers,a.limit)
if __name__=='__main__':main()
