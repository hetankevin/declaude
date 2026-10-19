#!/usr/bin/env python3
"""Summarize paired preferences without treating judges as independent tasks."""
import argparse,collections,hashlib,json,math,random,statistics
from pathlib import Path

SCORE={'win':1.,'tie':.5,'loss':0.}
CONFIGS=['haiku','sonnet-low','sonnet-high','opus-low','opus-xhigh','fable','astra-medium','astra-high','sol-low','luna-medium']

def validate_records(records,cases,configs,judges,seed,audit,candidate,reference,rubric,responses):
 """Fail closed before publication. responses maps (case, config, arm) to text.

 Reconstruct requests from frozen cases and exact responses, not self-reported
 hashes alone. This reads/validates grades but never invokes a model or repairs.
 """
 import pairwise
 def require(ok,message):
  if not ok:raise ValueError(message)
 require(math.isfinite(audit) and 0<=audit<=1,'Invalid audit fraction')
 require(candidate!=reference,'Candidate and reference must differ')
 require(bool(cases) and bool(configs) and len(configs)==len(set(configs)),'Invalid cases/configs')
 require(set(configs)<=set(CONFIGS),'Unsupported configurations')
 require(len(judges)==2 and set(judges)=={'grader-opus','astra-high'},'Expected both frozen judge families')
 expected=set()
 for case in cases:
  for cfg in configs:
   audited=int(pairwise.digest([seed,case,cfg,'audit']),16)/2**256<audit
   for judge in judges:
    for order in (['primary','reversed'] if audited else ['primary']):expected.add((case,cfg,judge,order))
 keys=[(r['case'],r['config'],r['judge'],r['order']) for r in records]
 require(len(keys)==len(set(keys)),'Duplicate grades')
 actual=set(keys)
 require(actual==expected,f'Incomplete or unexpected matrix: {len(expected-actual)} missing, {len(actual-expected)} extra judgments')
 for r in records:
  require(r.get('record_sha256')==pairwise.digest({k:v for k,v in r.items() if k!='record_sha256'}),'Record hash mismatch')
  require((r.get('candidate'),r.get('reference'))==(candidate,reference),'Mixed or unexpected comparison')
  case,cfg,judge=r['case'],r['config'],r['judge']
  reverse=r['order']=='reversed'
  base=('left','right')[int(pairwise.digest([seed,case,cfg,judge,'side']),16)%2]
  side=('right' if base=='left' else 'left') if reverse else base
  other='right' if side=='left' else 'left'
  label='A' if side=='right' else 'B'
  provider,model,effort=pairwise.bench.CONFIGS[judge]
  metadata=dict(case=case,config=cfg,judge=judge,provider=provider,model=model,effort=effort,
                left_id=reference,right_id=candidate,candidate_side='right',seed=seed,
                reverse=reverse,base_a_side=base,order={'A':side,'B':other})
  require(r.get('metadata')==metadata,'Seed, order, or judge metadata mismatch')
  require(r.get('candidate_position')==label,'Candidate position mismatch')
  texts={'left':responses[(case,cfg,reference)],'right':responses[(case,cfg,candidate)]}
  supplied=pairwise.supplied_case(cases[case]);supplied['responses']={'A':texts[side],'B':texts[other]}
  prompt=rubric+'\n\nINPUT_JSON:\n'+pairwise.canonical(supplied)
  require(r.get('rubric_sha256')==pairwise.text_hash(rubric),'Pairwise rubric hash mismatch')
  require(r.get('prompt_sha256')==pairwise.text_hash(prompt),'Task/prompt hash mismatch')
  require(r.get('response_sha256')=={k:pairwise.text_hash(v) for k,v in texts.items()},'Response hash mismatch')
  require(r.get('version')==pairwise.VERSION,'Unsupported pairwise record version')
  request=dict(version=r['version'],rubric=rubric,prompt=prompt,responses=texts,metadata=metadata)
  require(r.get('fingerprint')==pairwise.digest(request),'Request fingerprint mismatch')
  verdict=pairwise.validate_verdict(r['raw_judgment'],supplied)
  require(all(r.get(k)==v for k,v in pairwise.normalized(verdict,label).items()),'Normalized verdict mismatch')

def validate_manifest(matrix,paths,cases,configs,seed,candidate,reference,runs,rubric):
 """Bind strict input to the manifest and generation artifacts, without skill reads."""
 def require(ok,message):
  if not ok:raise ValueError(message)
 require(set(configs)==set(matrix['configs']),'Configurations differ from manifest')
 require(seed==matrix['pairwise_seed'],'Seed differs from manifest')
 require(candidate==matrix['selected'] and reference in matrix['conditions'],'Comparison differs from manifest')
 require(hashlib.sha256(rubric.encode()).hexdigest()==matrix['pairwise_grader_sha256'],'Frozen pairwise rubric mismatch')
 expected=collections.Counter(matrix['dataset_sha256'].values())
 require(collections.Counter(hashlib.sha256(p.read_bytes()).hexdigest() for p in paths)==expected,'Dataset hashes differ from manifest')
 counts=collections.Counter(c['split'] for c in cases.values())
 require(set(counts)==set(matrix['dataset_sha256']) and all(n==matrix['cases_per_split'] for n in counts.values()),'Split counts differ from manifest')
 responses={}
 for case,c in cases.items():
  for cfg in configs:
   for arm in (reference,candidate):
    # Validate path components before reading artifacts.
    for part in (case,cfg,arm):
     require(isinstance(part,str) and part not in ('','.','..') and '/' not in part and '\\' not in part,'Unsafe artifact identity')
    path=runs/case/cfg/arm
    meta=json.loads((path/'meta.json').read_text())
    wanted=dict(case=case,config=cfg,arm=arm,model=matrix['configs'][cfg]['model'],effort=matrix['configs'][cfg]['effort'],task_sha256=hashlib.sha256(c['task'].encode()).hexdigest(),skill_sha256=matrix['skill_sha256_by_arm'][arm])
    require(all(k in meta and meta[k]==v for k,v in wanted.items()),'Generation metadata mismatch')
    responses[(case,cfg,arm)]=(path/'response.md').read_bytes().decode('utf-8')
 return responses

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

def order_diagnostics(records,cases):
 """Counts are descriptive: each pair is one case/config/judge in both orders."""
 pairmap=collections.defaultdict(dict)
 for r in records:pairmap[(r['case'],r['config'],r['judge'])][r['order']]=r
 audits=[v for v in pairmap.values() if 'primary' in v and 'reversed' in v]
 def counts(items):
  return dict(pairs=len(items),cases=len({v['primary']['case'] for v in items}),
              case_config_pairs=len({(v['primary']['case'],v['primary']['config']) for v in items}),
              same_verdict=sum(v['primary']['outcome']==v['reversed']['outcome'] for v in items),
              opposite_non_tie=sum({v['primary']['outcome'],v['reversed']['outcome']}=={'win','loss'} for v in items))
 judges=sorted({r['judge'] for r in records})
 result=counts(audits)
 result['by_judge']={j:counts([v for v in audits if v['primary']['judge']==j]) for j in judges}
 result['by_split']={}
 for split in sorted({c['split'] for c in cases.values()}):
  items=[v for v in audits if cases[v['primary']['case']]['split']==split]
  result['by_split'][split]=counts(items)
  result['by_split'][split]['by_judge']={j:counts([v for v in items if v['primary']['judge']==j]) for j in judges}
 return result


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
 auditsummary=order_diagnostics(records,cases)
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
 lines+=['',f"Order audits cover {auditsummary['cases']} unique cases and {auditsummary['case_config_pairs']} case/configuration pairs. Audit pair counts include judges and are not independent task counts.",'', '| Split | Judge | Unique cases | Case/config pairs | Order pairs | Same verdict | Win/loss reversals |','|---|---|---:|---:|---:|---:|---:|']
 for split,checks in auditsummary['by_split'].items():
  for judge,check in [('all',checks)]+list(checks['by_judge'].items()):
   lines.append(f"| {split} | {judge} | {check['cases']} | {check['case_config_pairs']} | {check['pairs']} | {check['same_verdict']} | {check['opposite_non_tie']} |")
 (out/'report.md').write_text('\n'.join(lines)+'\n')
 return summary

def main(argv=None):
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--inputs',nargs='+',type=Path,required=True);ap.add_argument('--cases',nargs='+',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--configs',default=','.join(CONFIGS),help='Expected configurations in strict mode');ap.add_argument('--seed',default='declaude-pairwise-v1');ap.add_argument('--order-audit',type=float,default=.2)
 ap.add_argument('--strict',action='store_true',help='Validate full frozen matrix and provenance before writing; legacy mode preserves historical summaries')
 ap.add_argument('--matrix',type=Path);ap.add_argument('--runs',type=Path,help='Read-only generation root for strict response verification')
 ap.add_argument('--candidate');ap.add_argument('--reference');a=ap.parse_args(argv)
 if a.strict and not all((a.matrix,a.runs,a.candidate,a.reference)):ap.error('--strict requires --matrix, --runs, --candidate and --reference')
 if not a.strict and any((a.matrix,a.runs,a.candidate,a.reference)):ap.error('--matrix/--runs/--candidate/--reference require --strict')
 case_rows=[c for p in a.cases for c in json.loads(p.read_text())['cases']]
 cases={c['id']:c for c in case_rows}
 if a.strict and len(cases)!=len(case_rows):raise ValueError('Duplicate case IDs')
 records=[]
 for p in a.inputs:
  if p.is_file():records+=json.loads(p.read_text())
  else:
   for q in sorted(p.glob('*/*/*/*.json')):
    r=json.loads(q.read_text())
    if a.strict or isinstance(r,dict) and r.get('order') in ['primary','reversed']:records.append(r)
 if a.strict:
  matrix=json.loads(a.matrix.read_text());configs=a.configs.split(',')
  if a.order_audit!=matrix.get('order_audit_fraction',.2):raise ValueError('Audit fraction differs from manifest')
  rubric=(Path(__file__).resolve().parents[1]/'evals/graders/pairwise-v1.txt').read_text(encoding='utf-8')
  responses=validate_manifest(matrix,a.cases,cases,configs,a.seed,a.candidate,a.reference,a.runs,rubric)
  validate_records(records,cases,configs,matrix.get('pairwise_judges',['grader-opus','astra-high']),a.seed,a.order_audit,a.candidate,a.reference,rubric,responses)
 keys=[(r['case'],r['config'],r['judge'],r['order']) for r in records]
 assert len(keys)==len(set(keys)),'Duplicate grades'
 assert records,'No observations'
 report(records,cases,a.out)
 print((a.out/'report.md').read_text())
if __name__=='__main__':main()
