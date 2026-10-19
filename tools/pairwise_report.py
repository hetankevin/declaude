#!/usr/bin/env python3
"""Summarize paired preferences without treating judges as independent tasks."""
import argparse,collections,json,random,statistics
from pathlib import Path

SCORE={'win':1.,'tie':.5,'loss':0.}
CONFIGS=['haiku','sonnet-low','sonnet-high','opus-low','opus-xhigh','fable','astra-medium','astra-high','sol-low','luna-medium']

def aggregate(rows,dimension=None,samples=3000):
 def outcome(r):return r['outcome'] if dimension is None else r['dimensions'].get(dimension,'NA')
 rs=[r for r in rows if outcome(r) in SCORE]
 if not rs:return None
 by=collections.defaultdict(list)
 for r in rs:by[r['case']].append(SCORE[outcome(r)])
 case_means={k:statistics.mean(v) for k,v in by.items()}
 ids=sorted(by);rng=random.Random(47132026)
 bs=sorted(statistics.mean(case_means[c] for c in rng.choices(ids,k=len(ids))) for _ in range(samples))
 counts=collections.Counter(outcome(r) for r in rs)
 return {'preference':statistics.mean(case_means.values()),'ci95':[bs[int(.025*samples)],bs[int(.975*samples)-1]],'cases':len(ids),'judgments':len(rs),'wins':counts['win'],'ties':counts['tie'],'losses':counts['loss']}

def report(records,cases,out):
 out.mkdir(parents=True,exist_ok=True)
 primary=[r for r in records if r['order']=='primary']
 dimensions=['meaning','naturalness','progression','voice','proof']
 summary={}
 for split in sorted({c['split'] for c in cases.values()}):
  summary[split]={}
  for cfg in CONFIGS+['claude-all','codex-all','all']:
   cfgs=CONFIGS[:6] if cfg=='claude-all' else CONFIGS[6:] if cfg=='codex-all' else CONFIGS if cfg=='all' else [cfg]
   rs=[r for r in primary if cases[r['case']]['split']==split and r['config'] in cfgs]
   summary[split][cfg]={'overall':aggregate(rs),'categories':{},'dimensions':{},'judges':{}}
   for cat in ['ordinary','research','argument','proof','control']:
    summary[split][cfg]['categories'][cat]=aggregate([r for r in rs if cases[r['case']]['category']==cat])
   for dim in dimensions:summary[split][cfg]['dimensions'][dim]=aggregate(rs,dim)
   for judge in sorted({r['judge'] for r in rs}):summary[split][cfg]['judges'][judge]=aggregate([r for r in rs if r['judge']==judge])
   summary[split][cfg]['material_errors']={arm:sum(r[arm+'_material_error'] for r in rs)/len(rs) if rs else None for arm in ['candidate','reference']}
 pairmap=collections.defaultdict(dict)
 for r in records:pairmap[(r['case'],r['config'],r['judge'])][r['order']]=r
 audits=[v for v in pairmap.values() if 'primary' in v and 'reversed' in v]
 auditsummary={'pairs':len(audits),'same_verdict':sum(v['primary']['outcome']==v['reversed']['outcome'] for v in audits),'opposite_non_tie':sum({v['primary']['outcome'],v['reversed']['outcome']}=={'win','loss'} for v in audits)}
 cross=collections.defaultdict(list)
 for r in primary:cross[(r['case'],r['config'])].append(r['outcome'])
 comparisons=[v for v in cross.values() if len(v)==2]
 disagreements={'pairs':len(comparisons),'same_verdict':sum(v[0]==v[1] for v in comparisons),'opposite_non_tie':sum(set(v)=={'win','loss'} for v in comparisons)}
 (out/'observations.json').write_text(json.dumps(records,indent=2)+'\n')
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 (out/'judge-checks.json').write_text(json.dumps({'order_audit':auditsummary,'cross_family':disagreements},indent=2)+'\n')
 lines=['# Blinded pairwise writing comparison','', 'Preference = wins + half of ties, divided by judgments, aggregated at case level. 50% means no average preference. Intervals resample cases; two judges and reversed-order audits do not add independent tasks.','', '| Split | Candidate preference [95% CI] | Win / tie / loss judgments | Cases |','|---|---:|---:|---:|']
 for split,groups in summary.items():
  m=groups['all']['overall']
  if m:lines.append(f"| {split} | {100*m['preference']:.1f}% [{100*m['ci95'][0]:.1f}, {100*m['ci95'][1]:.1f}] | {m['wins']} / {m['ties']} / {m['losses']} | {m['cases']} |")
 lines+=['','Primary judgments only determine performance. Reversed-order repeats are diagnostic.','',f"Order audit: {auditsummary['same_verdict']}/{auditsummary['pairs']} identical verdicts; {auditsummary['opposite_non_tie']} win/loss reversals.",f"Cross-family judges: {disagreements['same_verdict']}/{disagreements['pairs']} identical verdicts; {disagreements['opposite_non_tie']} direct win/loss disagreements."]
 (out/'report.md').write_text('\n'.join(lines)+'\n')
 return summary

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--inputs',nargs='+',type=Path,required=True);ap.add_argument('--cases',nargs='+',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--configs',default=','.join(CONFIGS));ap.add_argument('--seed',default='declaude-pairwise-v1');ap.add_argument('--order-audit',type=float,default=.2);a=ap.parse_args()
 cases={c['id']:c for p in a.cases for c in json.loads(p.read_text())['cases']}
 records=[]
 for p in a.inputs:
  if p.is_file():records+=json.loads(p.read_text())
  else:
   for q in sorted(p.glob('*/*/*/*.json')):
    r=json.loads(q.read_text())
    if isinstance(r,dict) and r.get('order') in ['primary','reversed']:records.append(r)
 keys=[(r['case'],r['config'],r['judge'],r['order']) for r in records]
 assert len(keys)==len(set(keys)),'Duplicate grades'
 assert records,'No observations'
 report(records,cases,a.out)
 print((a.out/'report.md').read_text())
if __name__=='__main__':main()
