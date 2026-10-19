#!/usr/bin/env python3
"""Export an explicitly incomplete snapshot without making model calls."""
import argparse,collections,datetime,hashlib,json,time
from pathlib import Path
import pairwise,pairwise_report,report

def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(value,indent=2)+'\n')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runs',type=Path,required=True);ap.add_argument('--pairs',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--cutoff',help='ISO timestamp for reproducing a saved snapshot');a=ap.parse_args()
 cutoff=datetime.datetime.fromisoformat(a.cutoff).timestamp() if a.cutoff else time.time()-3
 paths=[Path('evals/large')/(s+'.json') for s in ['development','holdout']]
 cases={c['id']:c for p in paths for c in json.loads(p.read_text())['cases']}
 matrix=json.loads(Path('evals/large/final-matrix.json').read_text());configs=list(matrix['configs']);arms=matrix['conditions']
 for p in paths:assert hashlib.sha256(p.read_bytes()).hexdigest()==matrix['dataset_sha256'][p.stem]
 responses=[];grades=[];texts={}
 for p in sorted(a.runs.glob('*/*/*/response.md')):
  if p.stat().st_mtime>cutoff:continue
  case,cfg,arm=p.parts[-4:-1];meta=json.loads(p.with_name('meta.json').read_text());text=p.read_bytes().decode('utf-8')
  assert case in cases and cfg in configs and arm in arms
  assert meta['task_sha256']==hashlib.sha256(cases[case]['task'].encode()).hexdigest()
  assert meta['skill_sha256']==matrix['skill_sha256_by_arm'][arm]
  assert (meta['model'],meta['effort'])==(matrix['configs'][cfg]['model'],matrix['configs'][cfg]['effort'])
  row=dict(case=case,config=cfg,arm=arm,split=cases[case]['split'],subset=cases[case].get('subset'),response=text,words=len(text.split()),**{k:meta[k] for k in ['model','effort','task_sha256','skill_sha256']})
  responses.append(row);texts[(case,cfg,arm)]=text
  q=p.with_name('grading.json')
  if q.exists() and q.stat().st_mtime<=cutoff:
   g=json.loads(q.read_text());assert [(x['group'],x['text']) for x in g['assertions']]==[(x['group'],x['text']) for x in cases[case]['assertions']]
   grades.append(dict(row,grading_source='interim-final-run',**{k:g[k] for k in ['score','assertions','note','grader','pool_sha256','rubric_sha256']}))
 report.verify_pools(grades,cases,a.runs)
 records={};complete={}
 rubric=Path('evals/graders/pairwise-v1.txt').read_text();assert pairwise.text_hash(rubric)==matrix['pairwise_grader_sha256']
 for reference in ['none','v4']:
  rs=[]
  for p in sorted((a.pairs/('v5a-vs-'+reference)).glob('*/*/*/*.json')):
   if p.stat().st_mtime>cutoff:continue
   r=json.loads(p.read_text())
   assert r['record_sha256']==pairwise.digest({k:v for k,v in r.items() if k!='record_sha256'})
   rs.append(r)
  records[reference]=rs;keys={(r['case'],r['config'],r['judge'],r['order']) for r in rs};assert len(keys)==len(rs)
  complete[reference]=set()
  for case in cases:
   expected=set()
   for cfg in configs:
    audit=int(pairwise.digest([matrix['pairwise_seed'],case,cfg,'audit']),16)/2**256<matrix['order_audit_fraction']
    for judge in matrix['pairwise_judges']:
     for order in (['primary','reversed'] if audit else ['primary']):expected.add((case,cfg,judge,order))
   if expected<=keys:complete[reference].add(case)
 common=complete['none']&complete['v4']
 for ref,rs in records.items():
  balanced=[r for r in rs if r['case'] in common]
  if common:pairwise_report.validate_records(balanced,{k:cases[k] for k in common},configs,matrix['pairwise_judges'],matrix['pairwise_seed'],matrix['order_audit_fraction'],'v5a',ref,rubric,texts)
  write(a.out/f'pairwise-v5a-vs-{ref}.json',rs)
 absolute_counts=collections.Counter(r['case'] for r in grades)
 absolute_complete={c for c,n in absolute_counts.items() if n==len(configs)*len(arms)}
 summary={'pairwise':{},'absolute':{}}
 lines=['# Interim larger benchmark','', '**Incomplete snapshot. This is not the final preregistered comparison.** Execution was paused. No new model calls were made to build this report.','',f"Snapshot cutoff: {datetime.datetime.fromtimestamp(cutoff,datetime.timezone.utc).isoformat()}.",'',f"Saved here: {len(responses)}/2400 writing outputs, {len(grades)}/2400 absolute scorecards, and {sum(map(len,records.values()))}/3820 pairwise judgments (including order audits).",'', 'Exact available outputs and grades are included, including unfinished cases. The tables below use only cases complete across all ten configurations: both comparisons and both judges, with planned order audits, for pairwise tables; all three arms for absolute tables. Missing work is never scored as zero. The two table types can cover different cases.','', 'Completed cases are an execution-order subset, not a random new sample. Holdout coverage is especially small. These numbers must not be used for further tuning, stable model rankings, or a claim about the full held-out set.','', '## Pairwise comparison','', 'Preference = wins + half of ties, divided by primary judgments. Each complete case has the same ten configurations and two judges. Audits are excluded from performance.','', '| Split | Complete cases / planned | Comparison | Win / tie / loss | Preference |','|---|---:|---|---:|---:|']
 for split in ['development','holdout']:
  summary['pairwise'][split]={}
  for ref,rs in records.items():
   base=[r for r in rs if r['order']=='primary' and r['case'] in common and cases[r['case']]['split']==split]
   entry={}
   for cfg in configs+['all']:
    rr=[r for r in base if cfg=='all' or r['config']==cfg];counts=collections.Counter(r['outcome'] for r in rr)
    entry[cfg]={'cases':len({r['case'] for r in rr}),'judgments':len(rr),'wins':counts['win'],'ties':counts['tie'],'losses':counts['loss'],'preference':sum(pairwise_report.SCORE[r['outcome']] for r in rr)/len(rr) if rr else None}
   summary['pairwise'][split][ref]=entry;e=entry['all'];pref='NA' if e['preference'] is None else f"{100*e['preference']:.2f}%"
   lines.append(f"| {split} | {e['cases']}/40 | v5a vs {ref} | {e['wins']} / {e['ties']} / {e['losses']} | {pref} |")
 lines+=['','## Absolute grades','','Assertion rates are assertion-weighted. Holistic scores are out of 5.','', '| Split | Complete cases / planned | Arm | Assertions | Fidelity | Holistic | Median words |','|---|---:|---|---:|---:|---:|---:|']
 for split in ['development','holdout']:
  summary['absolute'][split]={}
  for arm in arms:
   rr=[r for r in grades if r['case'] in absolute_complete and r['split']==split and r['arm']==arm]
   if not rr:continue
   v={k:report.value(rr,k) for k in ['all','fidelity','style','argument','proof','holistic','words']};v['cases']=len({r['case'] for r in rr});summary['absolute'][split][arm]=v
   lines.append(f"| {split} | {v['cases']}/40 | {arm} | {100*v['all']:.2f}% | {100*v['fidelity']:.2f}% | {v['holistic']:.3f} | {v['words']:.0f} |")
 lines+=['','## Files','','- [Available writing outputs](responses.json)','- [Available absolute scorecards](absolute-observations.json)','- [Pairwise judgments: v5a vs no skill](pairwise-v5a-vs-none.json)','- [Pairwise judgments: v5a vs v4](pairwise-v5a-vs-v4.json)','- [Summary, including model/effort breakdowns](summary.json)','- [Coverage and included case IDs](coverage.json)','','The selected revision remains v5a under the development-only rule. Neither these results nor later held-out results may change that selection or the frozen grader. Model judgments are not human validation. Raw CLI envelopes and personal source material are not published.']
 write(a.out/'responses.json',responses);write(a.out/'absolute-observations.json',grades);write(a.out/'summary.json',summary)
 write(a.out/'coverage.json',{'cutoff_utc':datetime.datetime.fromtimestamp(cutoff,datetime.timezone.utc).isoformat(),'incomplete':True,'responses':len(responses),'absolute_scorecards':len(grades),'pairwise_judgments':sum(map(len,records.values())),'balanced_pairwise_cases':sorted(common),'balanced_absolute_cases':sorted(absolute_complete),'per_case':{c:{'split':cases[c]['split'],'outputs':sum(r['case']==c for r in responses),'absolute_grades':absolute_counts[c],'pairwise':{ref:sum(r['case']==c for r in rs) for ref,rs in records.items()}} for c in cases}})
 (a.out/'report.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines[:31]))
if __name__=='__main__':main()
