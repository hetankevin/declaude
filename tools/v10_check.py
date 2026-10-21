#!/usr/bin/env python3
"""Frozen 23-call targeted dev check. Reuses old drafts; never opens holdouts."""
import argparse
from pathlib import Path
import restored_check as r
from restored_check import lh, pairwise, prior, bench, context
from finalize_restored_results import repair_optional_source
ROOT=r.ROOT
OUT=ROOT/'evals/results/prose-repair/v10-targeted'
WORK=ROOT/'.local/prose-repair/v10-targeted'
OLD=ROOT/'evals/results/prose-repair/v9-restored-20'
CAND='v10-dev'
SELECT={
 'sol-low':['large-dev-a-10','large-dev-a-12','large-dev-b-06','large-dev-b-14','large-dev-b-20','large-dev-a-08'],
 'sonnet-high':['large-dev-a-06','large-dev-a-14','large-dev-b-02','large-dev-b-16','large-dev-b-14','large-dev-a-10','large-dev-b-06']}
REFS=('none','v4','v9-restored-dev')
ORIGINAL_EXEC=r.execute

def setup():
    r.OUT=OUT;r.WORK=WORK;r.CAND=CAND;r.CONFIGS=tuple(SELECT)
    r.load=load;r.grades=grades;r.execute=execute;r.report=report

def freeze():
    lh.require(not OUT.exists(),'Already frozen')
    selected={(cid,cfg) for cfg,ids in SELECT.items() for cid in ids}
    ids={cid for cid,cfg in selected}
    cases=[c for c in lh.read(OLD/'cases.json') if c['id'] in ids]
    oldrows=lh.read(OLD/'responses.json')
    baselines=[x for x in oldrows if (x['case'],x['config']) in selected and x['arm'] in REFS]
    lh.require(len(baselines)==39,'Missing saved baselines')
    for x in baselines:lh.require(x['response_sha256']==pairwise.text_hash(x['response']),'Response changed')
    historical=[x for x in lh.read(OLD/'observations.json') if (x['case'],x['config']) in selected]
    for x in historical:
        for arm,h in x['response_sha256'].items():
            row=next(y for y in baselines if (y['case'],y['config'],y['arm'])==(x['case'],x['config'],arm))
            lh.require(row['response_sha256']==h,'Saved judged output mismatch')
    bundle=bench.bundle(ROOT/'evals/versions'/CAND)
    jobs=[];counter=0
    for c in cases:
        cid=c['id'];cfgs=[cfg for cfg in SELECT if (cid,cfg) in selected]
        for cfg in cfgs:jobs.append(dict(id=cid+'--'+cfg,stage='generation',case=cid,config=cfg))
        pairs=[]
        for cfg in cfgs:
            for ref in REFS:
                pairs.append(dict(case=cid,config=cfg,candidate=CAND,reference=ref,judge='sol-high',order='primary',label=f'P{len(pairs)+1:02d}',a_side='right' if counter%2==0 else 'left'));counter+=1
        jobs.append(dict(id=cid+'--batch',stage='judge',case=cid,judge='sol-high',order='primary',pairs=pairs))
    assert len(jobs)==23 and counter==39
    for name,value in [('cases.json',cases),('baselines.json',baselines),('historical-observations.json',historical)]:lh.public_safe(value);lh.write(OUT/name,value)
    lh.write(OUT/'bundle.txt',bundle.encode());lh.write(OUT/'rubric.txt',(OLD/'rubric.txt').read_bytes())
    scripts=['v10_check.py','restored_check.py','bench.py','grade_long_horizon.py','long_horizon.py','pairwise.py','prose_repair.py','context_regrade.py','cross_model_small.py','finalize_restored_results.py','finish_restored_check.py']
    plan=dict(candidate=CAND,configs={cfg:list(bench.CONFIGS[cfg]) for cfg in SELECT},judge=r.JUDGE,jobs=jobs,max_calls=23,max_generations=13,max_judges=10,max_claude_calls=7,max_workers=2,retries=0,token_guard=700000,codex_credit_guard=90,writer_token_reservation=30000,judge_token_reservation=50000,credit_reservations={'sol-low':3,'sol-high':6},credit_rates=r.RATES,selection=SELECT,selection_reason='Targeted development repair: all five Sol losses and all four Sonnet losses vs v4, Sol scoring-order win, and three Sonnet fidelity wins. Unequal selected samples; no population or family ranking. No holdout access.',validation='Original strict evidence validator plus predeclared source-verified initial-case repair and optional source quote removal. Reasons/preferences unchanged. Qualified verdicts flagged and excluded in sensitivity. No retries.',packing='Unchanged fully inlined generation format and frozen author-specific Sol-high judge. All three comparator arms reused, no extra order audits.',files={p.name:lh.hashed(p) for p in OUT.iterdir()},scripts={n:lh.hashed(ROOT/'tools'/n) for n in scripts},source_artifacts={n:lh.hashed(OLD/n) for n in ['responses.json','observations.json','cases.json','rubric.txt']})
    plan['plan_sha256']=pairwise.digest(plan);lh.write(OUT/'plan.json',plan)
    print('Frozen:13 drafts,10 judge batches,39 pairs,23 calls.700k token/90 credit guards.')

def load():
    p=lh.read(OUT/'plan.json');lh.require(p['plan_sha256']==pairwise.digest({k:v for k,v in p.items() if k!='plan_sha256'}),'Plan changed')
    for n,h in p['files'].items():lh.require(lh.hashed(OUT/n)==h,'Frozen input changed')
    for n,h in p['scripts'].items():lh.require(lh.hashed(ROOT/'tools'/n)==h,'Frozen code changed')
    for n,h in p['source_artifacts'].items():lh.require(lh.hashed(OLD/n)==h,'Saved source evidence changed')
    lh.require(bench.bundle(ROOT/'evals/versions'/CAND)==(OUT/'bundle.txt').read_text(),'Candidate changed')
    return p,{c['id']:c for c in lh.read(OUT/'cases.json')}

def grades(job,raw,rubric,cases,texts,plan):
    prompt,supplied,pairs=prior.request(job,rubric,cases,texts)
    parsed,syntax=context.parse_batch(raw);pairwise.keys(parsed,pairs,'batch')
    records=[];errors=[]
    for e in job['pairs']:
        try:
            source=dict(supplied,responses=pairs[e['label']]);v,fmt=context.repair_evidence(parsed[e['label']],source)
            v,fixes=repair_optional_source(v,source);pairwise.validate_verdict(v,source)
            label='A' if e['a_side']=='right' else 'B'
            records.append(dict(case=e['case'],config=e['config'],candidate=CAND,reference=e['reference'],judge='sol-high',order='primary',pair_id=e['label'],candidate_position=label,raw_judgment=v,**pairwise.normalized(v,label),evidence_format_repairs=fmt,source_quote_repairs=fixes,optional_source_quote_qualified=any(x.get('kind')=='optional_source_quote_removed' for x in fixes),json_syntax_repairs=syntax,raw_sha256=pairwise.text_hash(raw),prompt_sha256=pairwise.text_hash(prompt),rubric_sha256=pairwise.text_hash(rubric),context_sha256=pairwise.text_hash(supplied['user_context']),plan_sha256=plan['plan_sha256'],response_sha256={arm:pairwise.text_hash(texts[e['case'],e['config'],arm]) for arm in (e['reference'],CAND)}))
        except (ValueError,KeyError,TypeError) as exc:errors.append(dict(pair=e['label'],error=str(exc)))
    return records,errors

def execute(job):
    setup();return ORIGINAL_EXEC(job)

def report():
    plan,cases=load();texts=r.texts_for(plan,cases);rubric=(OUT/'rubric.txt').read_text();records=[];answers=[];missing=[]
    for job in plan['jobs']:
        if job['stage']!='judge':continue
        d=r.directory(job)
        if not (d/'accepted.json').exists():missing.append(job['id']);continue
        raw=(d/'answer.txt').read_text();new,errors=grades(job,raw,rubric,cases,texts,plan)
        lh.require(new==lh.read(d/'accepted.json'),'Cached grade changed')
        lh.require(lh.read(d/'request.json')['prompt']==prior.request(job,rubric,cases,texts)[0],'Judge prompt changed')
        records+=new;answers.append(dict(job=job['id'],answer=raw,invalid=errors))
    expected={(cid,cfg,ref) for cfg,ids in SELECT.items() for cid in ids for ref in REFS};actual={(x['case'],x['config'],x['reference']) for x in records}
    lh.require(len(actual)==len(records) and actual<=expected,'Duplicate verdict')
    ledger=r.ledger(plan)
    usage=dict(calls=len(ledger),writing_calls=sum(x['stage']=='generation' for x in ledger),judge_calls=sum(x['stage']=='judge' for x in ledger),claude_calls=sum(x['config']=='sonnet-high' for x in ledger),known_reported_tokens=sum(x['reported_tokens'] or 0 for x in ledger),unknown_attempts=sum(x['finished'] and not x['known'] for x in ledger),codex_paid_credit_equivalent=sum(x['codex_credits'] for x in ledger if x['known']),charged_tokens=sum(x['charged_tokens'] for x in ledger),charged_credits=sum(x['codex_credits'] for x in ledger),attempts=ledger,note='Estimated paid-credit equivalents, not subscription usage or billed debits. Claude separately capped. Coordinator excluded.')
    coverage=dict(complete=actual==expected,accepted=len(records),expected=39,outputs=sum(k[2]==CAND for k in texts),expected_outputs=13,missing_batches=missing,missing_pairs=sorted(expected-actual))
    summary={ref:{cfg:prior.net_stats([x for x in records if x['reference']==ref and x['config']==cfg]) for cfg in SELECT} for ref in REFS}
    sensitivity={ref:{cfg:prior.net_stats([x for x in records if x['reference']==ref and x['config']==cfg and not x['optional_source_quote_qualified']]) for cfg in SELECT} for ref in REFS}
    outputs=[dict(case=cid,config=cfg,arm=arm,response=s,response_sha256=pairwise.text_hash(s)) for (cid,cfg,arm),s in sorted(texts.items())]
    for n,v in [('responses.json',outputs),('observations.json',records),('judge-responses.json',answers),('usage.json',usage),('coverage.json',coverage),('summary.json',summary),('quote-sensitivity.json',sensitivity)]:lh.public_safe(v);lh.write(OUT/n,v)
    lines=['# V10 targeted development repair','','Six selected Sol-low cases and seven selected Sonnet-high cases. Selection targets known v9 regressions plus fidelity and explanation-order wins. The samples differ across models. This is a tuning diagnostic, not fresh OOS evidence or a model-family ranking. One frozen author-specific Sol-high judge with anonymous alternating A/B positions, no new order audits. All comparator drafts are reused.','',f'Coverage: {coverage["outputs"]}/13 drafts; {len(records)}/39 comparisons. Missing grades are never ties.','', '| Model | vs none | vs v4 | vs restored v9 |','|---|---|---|---|']
    for cfg in SELECT:
        cells=[]
        for ref in REFS:
            s=summary[ref][cfg];cells.append(f'{s["wins"]}W/{s["ties"]}T/{s["losses"]}L; {s["net_pp"]:+.1f} pp' if s['judgments'] else 'ungraded')
        lines.append('| '+cfg+' | '+' | '.join(cells)+' |')
    lines+=['','Win rate minus loss rate in percentage points; ties zero. Small selected samples, no general superiority claim. Inspect actual cases and fidelity flags before promotion.','','| Case | Model | Reference | Outcome | Candidate error |','|---|---|---|---|---|']
    for x in records:lines.append(f'| {x["case"]} | {x["config"]} | {x["reference"]} | {x["outcome"]} | {x["candidate_material_error"]} |')
    lines+=['',f'Usage: {usage["calls"]}/23 attempts, {usage["known_reported_tokens"]:,} reported tokens, {usage["unknown_attempts"]} unknown attempts, {usage["codex_paid_credit_equivalent"]:.2f} estimated Codex credits plus {usage["claude_calls"]}/7 Claude calls. Guards:700k tokens/90 Codex credits with reservations; no automatic retries. Estimates are not account debits.', '',f'Evidence qualification: {sum(x["optional_source_quote_qualified"] for x in records)} optional-source-quote qualified verdicts, disclosed with raw evidence and exclusion sensitivity. Required factual/proof/response evidence remains strict.','', 'Fresh holdouts untouched. Proof and all supporting reference files byte-identical to restored v9. Candidate frozen before execution; installed release remains v4. Reproduce without calls: python3 tools/v10_check.py report.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n');print(coverage,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','run','report']);a=p.parse_args();setup()
    if a.action=='freeze':freeze()
    elif a.action=='run':r.run()
    else:report()
