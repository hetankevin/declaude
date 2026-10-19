#!/usr/bin/env python3
"""Apply the preregistered development-only candidate qualification rule."""
import argparse,json,hashlib,statistics,collections
from pathlib import Path

CONFIGS=['haiku','sonnet-high','astra-medium','luna-medium']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cases',type=Path,required=True);ap.add_argument('--runs',type=Path,required=True);ap.add_argument('--pairs',type=Path,required=True);ap.add_argument('--candidate',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 cases=json.loads(a.cases.read_text())['cases'];assert len(cases)==20
 assert all(c['split']=='development' for c in cases),'Never select on holdout'
 grades={arm:[] for arm in ['v4',a.candidate]}
 for c in cases:
  for cfg in CONFIGS:
   for arm in grades:
    p=a.runs/c['id']/cfg/arm/'grading.json';g=json.loads(p.read_text())
    assert g['rubric_sha256']==hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()
    grades[arm].append(g)
 pairs=[]
 for c in cases:
  for cfg in CONFIGS:
   for j in ['grader-opus','astra-high']:
    r=json.loads((a.pairs/c['id']/cfg/j/'primary.json').read_text())
    assert r['candidate']==a.candidate and r['reference']=='v4'
    pairs.append(r)
 preference=statistics.mean({'win':1,'tie':.5,'loss':0}[r['outcome']] for r in pairs)
 fidelity={arm:statistics.mean(v['passed'] for g in gs for v in g['assertions'] if v['group']=='fidelity') for arm,gs in grades.items()}
 material={key:statistics.mean(r[key+'_material_error'] for r in pairs) for key in ['candidate','reference']}
 counts=collections.Counter(r['outcome'] for r in pairs)
 result={'candidate':a.candidate,'subsets':sorted({c['subset'] for c in cases}),'cases':len(cases),'configs':CONFIGS,'judgments':len(pairs),'preference':preference,'win_tie_loss':dict(counts),'fidelity':fidelity,'material_error':material,'qualifies':preference>.5 and fidelity[a.candidate]>=fidelity['v4'] and material['candidate']<=material['reference'],'dataset_sha256':hashlib.sha256(a.cases.read_bytes()).hexdigest(),'rule':'preference > .5; fidelity >= incumbent; material errors <= incumbent; ties retain incumbent'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
