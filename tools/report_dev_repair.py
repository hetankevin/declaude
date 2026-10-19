#!/usr/bin/env python3
"""Publish the bounded dev pilot from saved evidence, with no model calls."""
import argparse,collections,json
from pathlib import Path
import bench,pairwise,pairwise_report

ROOT=Path(__file__).resolve().parents[1]
def main(pilot='dev-repair-1'):
 if pilot not in ('dev-repair-1','dev-repair-2'):raise ValueError('Unknown pilot')
 out=ROOT/'evals/results'/pilot;local=ROOT/'.local'/pilot
 plan=json.loads((out/'plan.json').read_text())
 ledger=json.loads((local/'calls.json').read_text())
 assert len(ledger)<=plan['call_cap'] and all(bench.CONFIGS[x['config']][0]=='codex' for x in ledger)
 assert not any(x['state']=='started' for x in ledger),'Wait for all attempted calls to end'
 assert pairwise.text_hash(bench.bundle(ROOT/'evals/versions'/plan['candidate']))==plan['skill_sha256']
 cases={c['id']:c for c in json.loads((ROOT/'evals/large/development.json').read_text())['cases']}
 references={(r['case'],r['config']):r for r in json.loads((ROOT/'evals/results/large-interim/responses.json').read_text()) if r['split']=='development' and r['arm']==plan['reference']}
 rubric=pairwise.RUBRIC.read_text();assert pairwise.text_hash(rubric)==plan['rubric_sha256']
 observations=[];responses=[];missing=[]
 for p in plan['pairs']:
  cid,cfg=p['case'],p['config'];c=cases[cid];assert c['subset']=='tune'
  assert pairwise.text_hash(c['task'])==p['task_sha256']
  ref=references[cid,cfg]['response'];assert pairwise.text_hash(ref)==p['reference_sha256']
  candidate=local/'runs'/cid/cfg/plan['candidate']/'response.md'
  grade=local/'pairs'/cid/cfg/plan['judge']/'primary.json'
  if not candidate.exists():missing.append(dict(case=cid,config=cfg,stage='generation'));continue
  text=candidate.read_text();meta=json.loads(candidate.with_name('meta.json').read_text())
  assert meta['skill_sha256']==plan['skill_sha256'] and meta['task_sha256']==p['task_sha256']
  responses.append(dict(case=cid,config=cfg,reference=ref,candidate=text,reference_sha256=pairwise.text_hash(ref),candidate_sha256=pairwise.text_hash(text)))
  if not grade.exists():missing.append(dict(case=cid,config=cfg,stage='grading'));continue
  r=json.loads(grade.read_text())
  assert r['record_sha256']==pairwise.digest({k:v for k,v in r.items() if k!='record_sha256'})
  assert (r['case'],r['config'],r['judge'],r['candidate'],r['reference'])==(cid,cfg,plan['judge'],plan['candidate'],plan['reference'])
  assert r['metadata']['seed']==plan['seed'] and r['metadata']['reverse'] is False
  texts={'left':ref,'right':text};assert r['response_sha256']=={k:pairwise.text_hash(v) for k,v in texts.items()}
  supplied=pairwise.supplied_case(c);supplied['responses']={label:texts[side] for label,side in r['metadata']['order'].items()}
  assert r['prompt_sha256']==pairwise.text_hash(rubric+'\n\nINPUT_JSON:\n'+pairwise.canonical(supplied))
  assert r['raw_sha256']==pairwise.text_hash((local/'pairs'/r['raw_path']).read_text())
  verdict=pairwise.validate_verdict(r['raw_judgment'],supplied)
  assert all(r[k]==v for k,v in pairwise.normalized(verdict,r['candidate_position']).items())
  observations.append(r)
 summary={'calls':len(ledger),'claude_calls':0,'completed_pairs':len(observations),'planned_pairs':6,'missing':missing,'overall':pairwise_report.aggregate(observations),'dimensions':{d:pairwise_report.aggregate(observations,d) for d in pairwise.DIMENSIONS if d!='overall'},'candidate_material_flags':sum(r['candidate_material_error'] for r in observations),'reference_material_flags':sum(r['reference_material_error'] for r in observations),'reported_tokens':sum(r.get('usage',{}).get('reported_tokens',0) for r in ledger),'tokens_available_for_calls':sum('reported_tokens' in r.get('usage',{}) for r in ledger)}
 if pilot=='dev-repair-2':
  summary['grading_status']='Original pairwise-v1; provisional, not validated against personal preferences'
  for filename,key in [('proofs.md','proof_sha256'),('paper-voice.md','paper_voice_sha256')]:
   assert pairwise.text_hash((ROOT/'evals/versions'/plan['candidate']/'references'/filename).read_text())==plan[key]
  summary['proof_guidance_unchanged']=True
  summary['promoted']=False
 for name,data in [('observations',observations),('responses',responses),('summary',summary)]:pairwise.save_json(out/(name+'.json'),data)
 lines=['# Small development repair','', 'This diagnostic compares v6-dev with saved v5a outputs on six development/tune tasks. The revision prioritizes document organization and keeps operational conditions together. It also changes the translation guidance to discourage compression that sacrifices explanation.','', f"Budget: **{len(ledger)}/12 Codex calls, zero Claude calls**. Six generation slots use Sol low or Luna medium. Six blind grading slots use Astra high with the frozen pairwise rubric. No retries, order audits, new baseline generations, or holdout calls.",'', 'Positive percentage points favor v6-dev. Net advantage is win rate minus loss rate; ties contribute zero and remain in the denominator.','', '| Dimension | Win / tie / loss | Net advantage (pp) |','|---|---:|---:|']
 for label,m in [('Overall',summary['overall'])]+list(summary['dimensions'].items()):
  if m:lines.append(f"| {label} | {m['wins']} / {m['ties']} / {m['losses']} | {m['net_pp']:+.1f} |")
 lines+=['','| Development case | Generator | Outcome | Organization |','|---|---|---|---|']
 for r in observations:lines.append(f"| {r['case']} | {r['config']} | {r['outcome']} | {r['dimensions']['progression']} |")
 lines+=['',f"Material-error flags: {summary['candidate_material_flags']} candidate, {summary['reference_material_flags']} reference. Missing pairs: {len(missing)}. Missing results are not ties.",'', 'These tasks were deliberately selected for diagnosis, not random sampling: three practical documents, one research summary, one proof, and one already-polished control. Model and task effects are confounded. One same-family judge and one generation per condition cannot establish a reliable ranking. Existing baseline outputs were reused, so stochastic generation differences remain.','', 'The repair was motivated by previously examined holdout feedback. This is development work; the old holdout is no longer fresh evidence for this new revision. Its cases were not used in these calls. The original experiment and its selected candidate remain unchanged.','', '## Decision','', 'Do not promote v6-dev: the pilot has one win, three ties, and two losses, with no advantage on progression or overall quality. The handover improved its grouping, while the access notice grouped access details less cleanly and the research summary ended less effectively. Meaning tied in every comparison; the proof and polished control tied overall. These are small diagnostic observations, not causal estimates.', '', 'A narrower v6b-dev draft retains all v5a instructions and references and adds one paragraph limited to organizing practical documents. It is **untested and not installed**. The packaged and installed release remains v4. No more calls were made. See [follow-up status](followup.json).', '', '[Frozen plan](plan.json) · [Paired outputs](responses.json) · [Blinded judgments](observations.json) · [Summary](summary.json)']
 if pilot=='dev-repair-2':
  lines[2]='This diagnostic compares v7-dev with saved no-skill outputs on six development/tune tasks. Prose instructions were shortened and reframed as targeted edits rather than a mandatory rewrite. The proof and research-voice reference files are byte-identical to v5a.'
  lines=[line.replace('Sol low or Luna medium','Astra medium, Sol low, or Luna medium').replace('Positive percentage points favor v6-dev.','Positive percentage points favor v7-dev.').replace('three practical documents, one research summary, one proof, and one already-polished control','two practical documents, one research summary, one argument, one proof, and one already-polished control') for line in lines]
  cut=lines.index('## Decision')
  lines=lines[:cut]+['## Decision','', 'Not promoted. The original judge gives one win, four ties, and one loss (0 pp overall); progression ties in all six comparisons. The non-ties are fidelity findings: the baseline imported an unsupported premise from a tone-only sample, while the candidate strengthened a tentative concession in another task. Proof and polished control tie. These diagnoses are plausible, but the scores do not establish that the judge matches the author’s writing preferences.', '', 'The user questioned the evaluator during this run. All twelve calls had already started when scheduling was paused; the two in-flight judgments were saved without adding calls. No personal-alignment regrading has occurred. Read the [judge alignment audit](../judge-audit/report.md) before using these scores to choose a skill. The prepared contextual rubric is a draft, and the installed release remains v4.', '', '[Frozen plan](plan.json) · [Paired outputs](responses.json) · [Original blinded judgments](observations.json) · [Summary](summary.json)']
 (out/'report.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pilot',choices=['dev-repair-1','dev-repair-2'],required=True)
 main(parser.parse_args().pilot)
