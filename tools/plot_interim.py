#!/usr/bin/env python3
"""Render only the published interim snapshot; no model calls or live-run reads."""
import collections,json,statistics,math
from pathlib import Path
from plot_matrix import ORDER,METRICS,plot_matrix
from plot_pairwise import CATEGORIES,DIMENSIONS,plot_pairwise
from pairwise_report import SCORE
from report import value

ROOT=Path(__file__).resolve().parents[1]

def aggregate(rows,dimension=None):
 by=collections.defaultdict(list);counts=collections.Counter()
 for r in rows:
  result=r['outcome'] if dimension is None else r['dimensions'].get(dimension,'NA')
  if result in SCORE:by[r['case']].append(SCORE[result]);counts[result]+=1
 return dict(net_pp=200*statistics.mean(statistics.mean(v) for v in by.values())-100 if by else None,preference=statistics.mean(statistics.mean(v) for v in by.values()) if by else None,cases=len(by),judgments=sum(counts.values()),wins=counts['win'],ties=counts['tie'],losses=counts['loss'])

def configs_for(config):
 return ORDER[:6] if config=='claude-all' else ['astra-medium','astra-high','sol-low','luna-medium'] if config=='codex-all' else [c for c in ORDER if c not in ['claude-all','codex-all','all']] if config=='all' else [config]

def main():
 root=ROOT/'evals/results/large-interim';coverage=json.loads((root/'coverage.json').read_text());summary=json.loads((root/'summary.json').read_text())
 cases={c['id']:c for s in ['development','holdout'] for c in json.loads((ROOT/f'evals/large/{s}.json').read_text())['cases']}
 grades=[r for r in json.loads((root/'absolute-observations.json').read_text()) if r['case'] in coverage['balanced_absolute_cases']]
 for reference in ['none','v4']:
  out=root/'plots'/('v5a-vs-'+reference);out.mkdir(parents=True,exist_ok=True)
  records=[r for r in json.loads((root/f'pairwise-v5a-vs-{reference}.json').read_text()) if r['order']=='primary' and r['case'] in coverage['balanced_pairwise_cases']]
  pairgroups={};absgroups={}
  for split in ['development','holdout']:
   pairgroups[split]={};absgroups[split]={}
   for config in ORDER:
    cfgs=configs_for(config);rs=[r for r in records if r['config'] in cfgs and cases[r['case']]['split']==split]
    pairgroups[split][config]={'overall':aggregate(rs),'categories':{cat:aggregate([r for r in rs if cases[r['case']]['category']==cat]) for cat,_ in CATEGORIES if cat!='overall'},'dimensions':{dim:aggregate(rs,dim) for dim,_ in DIMENSIONS if dim!='overall'}}
    rr=[r for r in grades if r['config'] in cfgs and r['split']==split];cells={}
    for metric,_ in METRICS:
     arms={arm:[r for r in rr if r['arm']==arm] for arm in [reference,'v5a']}
     cells[metric]={arm:value(arms[arm],metric) for arm in arms}
     cells[metric]['case_count']=len({r['case'] for r in rr if metric in ['all','holistic','words'] or any(a['group']==metric for a in r['assertions'])})
    absgroups[split][config]=cells
   assert math.isclose(pairgroups[split]['all']['overall']['preference'],summary['pairwise'][split][reference]['all']['preference'],rel_tol=0,abs_tol=1e-12)
   for arm in [reference,'v5a']:
    for metric,_ in METRICS:assert absgroups[split]['all'][metric][arm]==summary['absolute'][split][arm][metric]
  (out/'pairwise-groups.json').write_text(json.dumps(pairgroups,indent=2)+'\n');(out/'absolute-groups.json').write_text(json.dumps(absgroups,indent=2)+'\n')
  plot_pairwise(pairgroups,out,show_counts=True)
  plot_matrix(absgroups,'v5a',out,reference=reference,show_counts=True)
  print('Rendered',out.relative_to(ROOT),flush=True)
if __name__=='__main__':main()
