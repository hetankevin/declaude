#!/usr/bin/env python3
"""Nine-call frozen cross-model development check; never opens a holdout."""
import argparse,json,time
from pathlib import Path
import bench,context_regrade as context,grade_long_horizon as transport
import long_horizon as lh,pairwise,prose_repair as prior,small_repair as small
ROOT=small.ROOT
OUT=ROOT/'evals/results/prose-repair/v9-cross-model'
WORK=ROOT/'.local/prose-repair/v9-cross-model'
CONFIGS=('sol-low','sonnet-high')


def freeze():
    lh.require(not OUT.exists(),'Already frozen')
    old,cases,_,rubric=small.load()
    ids=set(cases)
    baselines=[r for r in lh.read(ROOT/'evals/results/large-interim/responses.json') if r['case'] in ids and r['config'] in CONFIGS and r['arm'] in ('none','v4')]
    lh.require(len(baselines)==12,'Missing baselines')
    v4hash=pairwise.text_hash(bench.bundle(ROOT/'evals/versions/v4'))
    for r in baselines:
        lh.require(r['task_sha256']==pairwise.text_hash(cases[r['case']]['task']) and r['split']=='development','Baseline task mismatch')
        lh.require((r['model'],r['effort'])==bench.CONFIGS[r['config']][1:],'Model mismatch')
        lh.require(r['skill_sha256']==(v4hash if r['arm']=='v4' else None),'Baseline skill mismatch')
    astra=lh.read(small.OUT/'responses.json')
    reused=lh.read(small.OUT/'observations.json')
    historical=[r for r in lh.read(ROOT/'evals/results/context-regrade/v4-observations.json') if r['case'] in ids and r['config'] in (*CONFIGS,'astra-high') and r['judge']=='sol-high' and r['order']=='primary']
    lh.require(len(historical)==9 and len(reused)==6,'Historical grade coverage')
    texts={(r['case'],r['config'],r['arm']):r['response'] for r in baselines+astra}
    for r in historical+reused:
        lh.require(r['rubric_sha256']==pairwise.text_hash(rubric),'Historical rubric changed')
        lh.require(r['context_sha256']==pairwise.text_hash(cases[r['case']]['user_context']),'Historical author context changed')
        source=pairwise.supplied_case(cases[r['case']]);candidate=r['candidate_position'];ref='B' if candidate=='A' else 'A'
        source['responses']={candidate:texts[r['case'],r['config'],r['candidate']],ref:texts[r['case'],r['config'],r['reference']]}
        pairwise.validate_verdict(r['raw_judgment'],source)
        for arm,h in r['response_sha256'].items():lh.require(pairwise.text_hash(texts[r['case'],r['config'],arm])==h,'Historical output mismatch')
    jobs=[]
    for i,cid in enumerate(small.IDS):
        pairs=[]
        for cfg in CONFIGS:
            for ref in ['none','v4']:
                j=len(pairs)
                pairs.append(dict(case=cid,config=cfg,candidate='v9-dev',reference=ref,judge='sol-high',order='primary',label=f'P{j+1:02d}',a_side='right' if (i+j)%2==0 else 'left'))
        jobs.append(dict(id=cid,case=cid,judge='sol-high',order='primary',pairs=pairs))
    values={'cases.json':list(cases.values()),'baselines.json':baselines,'astra-responses.json':astra,'reused-observations.json':historical+reused}
    for n,v in values.items():lh.public_safe(v);lh.write(OUT/n,v)
    lh.write(OUT/'bundle.txt',(small.OUT/'bundle.txt').read_bytes());lh.write(OUT/'rubric.txt',rubric.encode())
    plan=dict(candidate='v9-dev',configs={c:list(bench.CONFIGS[c]) for c in CONFIGS},judge=small.JUDGE,jobs=jobs,max_calls=9,max_generations=6,max_judges=3,retries=0,soft_token_guard=250000,writer_reservation=30000,judge_reservation=40000,selection='Same three selected development cases as the Astra check, to compare model behavior. Two arguments and one proof; no fresh OOS evidence or broad family ranking.',packing='Same fully inlined portable bundle and generation prompt as historical baselines.',files={p.name:lh.hashed(p) for p in OUT.iterdir()},runner_sha256=lh.hashed(Path(__file__)))
    plan['plan_sha256']=pairwise.digest(plan);lh.write(OUT/'plan.json',plan)
    print('Frozen: six writing calls, three blind judge calls, no retries.')


def load():
    p=lh.read(OUT/'plan.json')
    lh.require(p['plan_sha256']==pairwise.digest({k:v for k,v in p.items() if k!='plan_sha256'}),'Plan changed')
    lh.require(p['runner_sha256']==lh.hashed(Path(__file__)),'Runner changed')
    for n,h in p['files'].items():lh.require(lh.hashed(OUT/n)==h,'Frozen input changed')
    cases={c['id']:c for c in lh.read(OUT/'cases.json')}
    texts={(r['case'],r['config'],r['arm']):r['response'] for r in lh.read(OUT/'baselines.json')+lh.read(OUT/'astra-responses.json')}
    return p,cases,texts,(OUT/'rubric.txt').read_text()


def tally():
    attempts=[]
    for request in sorted(WORK.glob('*/*/request.json')):
        d=request.parent;result=d/'result.json'
        lh.require(result.exists(),'Unfinished attempt: inspect, never replay')
        value=lh.read(result)
        raw=d/('cli.jsonl' if (d/'cli.jsonl').exists() else 'cli.json')
        if value.get('cli_sha256'):lh.require(lh.hashed(raw)==value['cli_sha256'],'Raw usage evidence changed')
        tokens=value.get('reported_tokens')
        attempts.append(dict(stage=d.parent.name,id=d.name,reported_tokens=tokens,usage=value.get('usage',{}),completed=value.get('completed',False)))
    charged=sum(r['reported_tokens'] if r['reported_tokens'] is not None else (40000 if r['stage']=='judge' else 30000) for r in attempts)
    return attempts,charged


def allowed(plan,stage):
    attempts,charged=tally();reserve=40000 if stage=='judge' else 30000
    return len(attempts)<9 and charged+reserve<=plan['soft_token_guard']


def claude_call(prompt,d,cfg):
    d.mkdir(parents=True,mode=0o700)
    lh.write(d/'request.json',dict(prompt=prompt,config=cfg,started=time.time()))
    try:
        with prior.capture_cli(d):answer,meta=bench.call(prompt,cfg,timeout=600)
        usage=meta['usage'];tokens=sum(usage.get(k,0) for k in ['input_tokens','output_tokens','cache_read_input_tokens','cache_creation_input_tokens'])
        lh.require(tokens>0,'Missing Claude usage')
        lh.write(d/'answer.txt',answer.encode())
        result=dict(completed=True,reported_tokens=tokens,usage=usage,cli_sha256=lh.hashed(d/'cli.json'))
        lh.write(d/'result.json',result)
    except Exception as exc:
        lh.write(d/'result.json',dict(completed=False,reported_tokens=None,error=type(exc).__name__,cli_sha256=lh.hashed(d/'cli.json') if (d/'cli.json').exists() else None))
        raise


def collect_texts(cases,texts):
    bundle=(OUT/'bundle.txt').read_text()
    for cid in small.IDS:
        for cfg in CONFIGS:
            d=WORK/'generation'/(cid+'--'+cfg)
            if not (d/'result.json').exists() or not lh.read(d/'result.json')['completed']:continue
            lh.require(lh.read(d/'request.json')['prompt']==prior.generation_prompt(cases[cid],bundle),'Writing prompt changed')
            texts[cid,cfg,'v9-dev']=(d/'answer.txt').read_text()
    return texts


def grade_records(job,raw,rubric,cases,texts):
    prompt,supplied,pairs=prior.request(job,rubric,cases,texts)
    parsed,syntax=context.parse_batch(raw)
    pairwise.keys(parsed,pairs,'batch')
    records=[];errors=[]
    for e in job['pairs']:
        try:
            source=dict(supplied,responses=pairs[e['label']])
            verdict,repairs=context.repair_evidence(parsed[e['label']],source)
            pairwise.validate_verdict(verdict,source)
            label='A' if e['a_side']=='right' else 'B'
            records.append(dict(case=e['case'],config=e['config'],candidate='v9-dev',reference=e['reference'],judge='sol-high',order='primary',pair_id=e['label'],candidate_position=label,raw_judgment=verdict,**pairwise.normalized(verdict,label),evidence_format_repairs=repairs,json_syntax_repairs=syntax,raw_sha256=pairwise.text_hash(raw),prompt_sha256=pairwise.text_hash(prompt),rubric_sha256=pairwise.text_hash(rubric),response_sha256={arm:pairwise.text_hash(texts[e['case'],e['config'],arm]) for arm in [e['reference'],'v9-dev']}))
        except (ValueError,KeyError,TypeError) as exc:errors.append(dict(pair=e['label'],error=str(exc)))
    return records,errors


def run():
    plan,cases,texts,rubric=load();bundle=(OUT/'bundle.txt').read_text()
    with pairwise.locked(WORK):
        for cid in small.IDS:
            for cfg in CONFIGS:
                d=WORK/'generation'/(cid+'--'+cfg)
                if (d/'request.json').exists():continue
                if not allowed(plan,'generation'):break
                prompt=prior.generation_prompt(cases[cid],bundle)
                if cfg.startswith('sonnet'):claude_call(prompt,d,cfg)
                else:transport.call(prompt,d,{'judge':{'model':bench.CONFIGS[cfg][1],'effort':bench.CONFIGS[cfg][2]}})
                print('written '+cid+' '+cfg,flush=True)
        collect_texts(cases,texts)
        for job in plan['jobs']:
            if not all((job['case'],c,'v9-dev') in texts for c in CONFIGS):continue
            d=WORK/'judge'/job['id']
            if (d/'request.json').exists():continue
            if not allowed(plan,'judge'):break
            prompt,_,_=prior.request(job,rubric,cases,texts)
            raw=transport.call(prompt,d,{'judge':small.JUDGE})
            try:
                records,errors=grade_records(job,raw,rubric,cases,texts)
                lh.write(d/'accepted.json',records);lh.write(d/'invalid.json',errors)
                print(job['id']+': '+','.join(r['config']+'/'+r['reference']+'='+r['outcome'] for r in records)+f'; invalid={len(errors)}',flush=True)
            except (ValueError,KeyError,TypeError) as exc:
                lh.write(d/'invalid.json',[{'error':str(exc)}]);print('invalid batch retained; no retry',flush=True)
    report()


def report():
    plan,cases,texts,rubric=load();collect_texts(cases,texts)
    new=[];answers=[];missing=[]
    for job in plan['jobs']:
        d=WORK/'judge'/job['id']
        if not (d/'accepted.json').exists():missing.append(job['id']);continue
        raw=(d/'answer.txt').read_text();records,errors=grade_records(job,raw,rubric,cases,texts)
        lh.require(records==lh.read(d/'accepted.json'),'Grades changed')
        new+=records;answers.append(dict(job=job['id'],answer=raw,invalid=errors))
    records=lh.read(OUT/'reused-observations.json')+new
    attempts,charged=tally()
    usage=dict(calls=len(attempts),writing_calls=sum(r['stage']=='generation' for r in attempts),judge_calls=sum(r['stage']=='judge' for r in attempts),known_reported_tokens=sum(r['reported_tokens'] or 0 for r in attempts),unknown_usage_attempts=sum(r['reported_tokens'] is None for r in attempts),soft_budget_charged_tokens=charged,attempts=attempts,note='Reported input/output plus cache tokens, not account quota or billing. Unknown calls charged one reservation for scheduling, not claimed as measured usage.')
    rows=[dict(case=c,config=cfg,arm=arm,response=s,response_sha256=pairwise.text_hash(s)) for (c,cfg,arm),s in sorted(texts.items())]
    for name,v in [('responses.json',rows),('observations.json',records),('judge-responses.json',answers),('usage.json',usage),('coverage.json',dict(new_primary=len(new),expected_new_primary=12,new_outputs=sum(k[1] in CONFIGS and k[2]=='v9-dev' for k in texts),expected_outputs=6,missing_batches=missing))]:lh.public_safe(v);lh.write(OUT/name,v)
    lines=['# V9 small cross-model check','','Same three selected development cases: two arguments and one proof. The skill, source tasks, author context, rubric and A/B order were frozen. Sol-high blind judging is used for all rows. Astra results and direct v4-vs-no-skill grades are reused from source-verified saved comparisons. These are selected development diagnostics, not fresh OOS evidence or a complete multi-model benchmark.','','| Model / effort | v9 vs no skill | v4 vs no skill | v9 vs v4 |','|---|---|---|---|']
    for cfg in ['astra-high',*CONFIGS]:
        cells=[]
        for cand,ref in [('v9-dev','none'),('v4','none'),('v9-dev','v4')]:
            rs=[r for r in records if r['config']==cfg and r['candidate']==cand and r['reference']==ref and r['order']=='primary'];w,t,l=[sum(r['outcome']==k for r in rs) for k in ['win','tie','loss']]
            cells.append(f'{w}W / {t}T / {l}L ({100*(w-l)/len(rs):+.1f} pp; n={len(rs)})' if rs else 'ungraded')
        lines.append('| '+cfg+' | '+' | '.join(cells)+' |')
    lines+=['','Ties contribute zero. No confidence intervals or broad family ranking are claimed from three cases. Saved baselines/grades were produced earlier; requested model labels do not prove an unchanged backend. No reversed-order audit was added in this economical pass.','', '| Case | Model / effort | Comparison | Outcome |','|---|---|---|---|']
    for r in sorted(records,key=lambda r:(r['case'],r['config'],r['candidate'],r['reference'])):lines.append(f'| {r["case"]} | {r["config"]} | {r["candidate"]} vs {r["reference"]} | {r["outcome"]} |')
    lines+=['',f'New work: {usage["writing_calls"]} writing calls and {usage["judge_calls"]} judge calls, {usage["known_reported_tokens"]:,} known reported tokens; {usage["unknown_usage_attempts"]} calls with unknown usage. The limit is nine calls with no automatic retries. The token guard is soft and includes cached input; this is not a credit or billing total.', '',f'Coverage: {len(new)}/12 new primary judgments. Missing or invalid judgments are not ties. Both fresh holdouts stay sealed. No long-horizon result, skill update, or installation change is produced by this check.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'new_judgments':len(new),'calls':usage['calls'],'known_tokens':usage['known_reported_tokens']}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','run','report']);a=p.parse_args();globals()[a.action]()
