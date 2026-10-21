#!/usr/bin/env python3
"""Budgeted 20-case restored-v9 check. Frozen development only, no retries."""
import argparse, collections, json, time
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path
import bench, context_regrade as context, cross_model_small as cross
import grade_long_horizon as transport, long_horizon as lh, pairwise, prose_repair as prior
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evals/results/prose-repair/v9-restored-20'
WORK=ROOT/'.local/prose-repair/v9-restored-20'
CAND='v9-restored-dev'
CONFIGS=('astra-high','sol-low','sonnet-high')
JUDGE={'model':'gpt-6.1-sol','effort':'high'}
RATES={'astra-high':(250,25,1250),'sol-low':(50,2.5,250),'sol-high':(50,2.5,250)}

def freeze():
    lh.require(not OUT.exists(),'Already frozen')
    cases=prior.development('validation')
    for c in cases:
        c['user_context']=context.CONTEXT['common']+'\n\n'+context.CONTEXT[c['category']]
        c['is_proof']=c['category']=='proof'
    ids={c['id'] for c in cases};bycase={c['id']:c for c in cases}
    baseline=[r for r in lh.read(ROOT/'evals/results/large-interim/responses.json') if r['case'] in ids and r['config'] in CONFIGS and r['arm'] in ('none','v4')]
    expected={(cid,cfg,arm) for cid in ids for cfg in CONFIGS for arm in ('none','v4')}
    lh.require(len(baseline)==120 and {(r['case'],r['config'],r['arm']) for r in baseline}==expected,'Missing baseline')
    v4hash=pairwise.text_hash(bench.bundle(ROOT/'evals/versions/v4'))
    for r in baseline:
        c=bycase[r['case']]
        lh.require(r['split']=='development' and r['subset']==c['subset'],'Split mismatch')
        lh.require(r['task_sha256']==pairwise.text_hash(c['task']),'Task mismatch')
        lh.require((r['model'],r['effort'])==bench.CONFIGS[r['config']][1:],'Model mismatch')
        lh.require(r['skill_sha256']==(v4hash if r['arm']=='v4' else None),'Bundle mismatch')
        lh.require(r['response'].strip(),'Empty baseline')
    rubric=(ROOT/'evals/results/context-regrade/rubric.txt').read_text()
    history=[r for r in lh.read(ROOT/'evals/results/context-regrade/v4-observations.json') if r['case'] in ids and r['config'] in CONFIGS and r['judge']=='sol-high' and r['order']=='primary']
    lh.require(len(history)==60,'Missing historical comparisons')
    texts={(r['case'],r['config'],r['arm']):r['response'] for r in baseline}
    for r in history:
        lh.require(r['rubric_sha256']==pairwise.text_hash(rubric) and r['context_sha256']==pairwise.text_hash(bycase[r['case']]['user_context']),'Historical judge inputs mismatch')
        for arm,h in r['response_sha256'].items():lh.require(pairwise.text_hash(texts[r['case'],r['config'],arm])==h,'Historical response mismatch')
        label=r['candidate_position'];source=pairwise.supplied_case(bycase[r['case']]);source['responses']={label:texts[r['case'],r['config'],'v4'],('B' if label=='A' else 'A'):texts[r['case'],r['config'],'none']}
        pairwise.validate_verdict(r['raw_judgment'],source)
    # Round-robin categories so an early budget stop does not cover just one kind of writing.
    groups={cat:[c for c in cases if c['category']==cat] for cat in prior.CATEGORIES}
    lh.require(all(len(v)==4 for v in groups.values()),'Category balance')
    ordered=[groups[cat][i] for i in range(4) for cat in prior.CATEGORIES]
    jobs=[]
    for i,c in enumerate(ordered):
        cid=c['id']
        for cfg in CONFIGS:jobs.append(dict(id=cid+'--'+cfg,stage='generation',case=cid,config=cfg))
        pairs=[]
        for cfg in CONFIGS:
            for ref in ('none','v4'):
                j=len(pairs);pairs.append(dict(case=cid,config=cfg,candidate=CAND,reference=ref,judge='sol-high',order='primary',a_side='right' if (i+j)%2==0 else 'left'))
        for b,chunk in enumerate((pairs[:4],pairs[4:])):
            for j,e in enumerate(chunk):e['label']=f'P{j+1:02d}'
            jobs.append(dict(id=cid+f'--batch{b+1}',stage='judge',case=cid,judge='sol-high',order='primary',pairs=chunk))
    bundle=bench.bundle(ROOT/'evals/versions'/CAND)
    for name,value in [('cases.json',cases),('baselines.json',baseline),('reused-observations.json',history)]:lh.public_safe(value);lh.write(OUT/name,value)
    for name,value in [('bundle.txt',bundle),('rubric.txt',rubric)]:lh.public_safe(value);lh.write(OUT/name,value.encode())
    plan=dict(candidate=CAND,configs={c:list(bench.CONFIGS[c]) for c in CONFIGS},judge=JUDGE,jobs=jobs,max_calls=100,max_generations=60,max_judges=40,max_claude_calls=20,max_workers=3,retries=0,token_guard=2500000,codex_credit_guard=300,writer_token_reservation=30000,judge_token_reservation=40000,credit_reservations={'astra-high':8,'sol-low':3,'sol-high':5},credit_rates=RATES,selection='Existing balanced validation subset of DEVELOPMENT, four cases per category. Previously inspected, not fresh validation or OOS.',packing='Fully inlined portable bundle, matching prior writing format. No selective-loading or long-horizon claim.',budget_note='Hard attempt caps; token/credit reservation guards can overshoot within active calls. At most three active calls. Unknown usage stops further scheduling. Claude separately capped at 20 calls. Coordinator usage excluded.',files={p.name:lh.hashed(p) for p in OUT.iterdir()},scripts={n:lh.hashed(ROOT/'tools'/n) for n in ['restored_check.py','bench.py','grade_long_horizon.py','long_horizon.py','pairwise.py','prose_repair.py','context_regrade.py','cross_model_small.py']})
    plan['plan_sha256']=pairwise.digest(plan);lh.write(OUT/'plan.json',plan)
    print('Frozen 20 development cases, 120 baselines, 100-call maximum.')

def load():
    p=lh.read(OUT/'plan.json');lh.require(p['plan_sha256']==pairwise.digest({k:v for k,v in p.items() if k!='plan_sha256'}),'Plan changed')
    for n,h in p['files'].items():lh.require(lh.hashed(OUT/n)==h,'Frozen input changed')
    for n,h in p['scripts'].items():lh.require(lh.hashed(ROOT/'tools'/n)==h,'Frozen code changed')
    lh.require(bench.bundle(ROOT/'evals/versions'/CAND)==(OUT/'bundle.txt').read_text(),'Candidate changed')
    return p,{c['id']:c for c in lh.read(OUT/'cases.json')}

def credits(usage,cfg):
    if cfg=='sonnet-high':return 0
    a,b,c=RATES[cfg];cached=usage.get('cached_input_tokens',0)
    return ((usage.get('input_tokens',0)-cached)*a+cached*b+usage.get('output_tokens',0)*c)/1e6

def directory(job):return WORK/job['stage']/job['id']
def reservation(job):return WORK/'reservations'/(job['id']+'.json')
def reserve(plan,job):
    cfg=job.get('config','sol-high')
    return (plan['writer_token_reservation'] if job['stage']=='generation' else plan['judge_token_reservation'],plan['credit_reservations'].get(cfg,0))

def ledger(plan):
    rows=[]
    for job in plan['jobs']:
        d=directory(job)
        if not (reservation(job)).exists():continue
        lh.require(lh.read(reservation(job))==dict(plan_sha256=plan['plan_sha256'],job=job),'Reservation mismatch')
        tok,cred=reserve(plan,job);r=lh.read(d/'result.json') if (d/'result.json').exists() else None
        known=r is not None and r.get('reported_tokens') is not None
        if r and r.get('cli_sha256'):
            raw=d/('cli.jsonl' if (d/'cli.jsonl').exists() else 'cli.json');lh.require(lh.hashed(raw)==r['cli_sha256'],'Raw evidence changed')
        rows.append(dict(id=job['id'],stage=job['stage'],config=job.get('config','sol-high'),finished=r is not None,known=known,completed=bool(r and r.get('completed')),reported_tokens=r.get('reported_tokens') if r else None,charged_tokens=r['reported_tokens'] if known else tok,codex_credits=credits(r.get('usage',{}),job.get('config','sol-high')) if known else cred,usage=r.get('usage',{}) if r else {},credit_is_reservation=not known))
    return rows

def allowed(plan,job,rows):
    if any(r['finished'] and not r['known'] for r in rows):return False
    tok,cred=reserve(plan,job)
    return (len(rows)<plan['max_calls'] and sum(r['stage']==job['stage'] for r in rows)<plan['max_generations' if job['stage']=='generation' else 'max_judges'] and (job.get('config')!='sonnet-high' or sum(r['config']=='sonnet-high' for r in rows)<plan['max_claude_calls']) and sum(r['charged_tokens'] for r in rows)+tok<=plan['token_guard'] and sum(r['codex_credits'] for r in rows)+cred<=plan['codex_credit_guard'])

def texts_for(plan,cases):
    texts={(r['case'],r['config'],r['arm']):r['response'] for r in lh.read(OUT/'baselines.json')};bundle=(OUT/'bundle.txt').read_text()
    for job in plan['jobs']:
        if job['stage']!='generation':continue
        d=directory(job)
        if not (d/'result.json').exists():continue
        r=lh.read(d/'result.json')
        if not r.get('completed') or not (d/'answer.txt').exists():continue
        lh.require(lh.read(d/'request.json')['prompt']==prior.generation_prompt(cases[job['case']],bundle),'Generation prompt changed')
        s=(d/'answer.txt').read_text();lh.require(s.strip(),'Empty answer')
        texts[job['case'],job['config'],CAND]=s
    return texts

def grades(job,raw,rubric,cases,texts,plan):
    # Validate every pair, preserving valid siblings if one verdict is malformed.
    prompt,supplied,pairs=prior.request(job,rubric,cases,texts);parsed,syntax=context.parse_batch(raw);pairwise.keys(parsed,pairs,'batch')
    records=[];errors=[]
    for e in job['pairs']:
        try:
            source=dict(supplied,responses=pairs[e['label']]);v,repairs=context.repair_evidence(parsed[e['label']],source);pairwise.validate_verdict(v,source)
            label='A' if e['a_side']=='right' else 'B'
            records.append(dict(case=e['case'],config=e['config'],candidate=CAND,reference=e['reference'],judge='sol-high',order='primary',pair_id=e['label'],candidate_position=label,raw_judgment=v,**pairwise.normalized(v,label),evidence_format_repairs=repairs,json_syntax_repairs=syntax,raw_sha256=pairwise.text_hash(raw),prompt_sha256=pairwise.text_hash(prompt),rubric_sha256=pairwise.text_hash(rubric),context_sha256=pairwise.text_hash(supplied['user_context']),plan_sha256=plan['plan_sha256'],response_sha256={arm:pairwise.text_hash(texts[e['case'],e['config'],arm]) for arm in (e['reference'],CAND)}))
        except (ValueError,KeyError,TypeError) as exc:errors.append(dict(pair=e['label'],error=str(exc)))
    return records,errors

def execute(job):
    plan,cases=load();d=directory(job)
    lh.require((reservation(job)).exists() and not (d/'request.json').exists(),'Never replay a started call')
    try:
        if job['stage']=='generation':
            prompt=prior.generation_prompt(cases[job['case']],(OUT/'bundle.txt').read_text());cfg=job['config']
            if cfg=='sonnet-high':cross.claude_call(prompt,d,cfg)
            else:transport.call(prompt,d,{'judge':dict(model=bench.CONFIGS[cfg][1],effort=bench.CONFIGS[cfg][2])})
        else:
            texts=texts_for(plan,cases);rubric=(OUT/'rubric.txt').read_text();prompt,_,_=prior.request(job,rubric,cases,texts)
            raw=transport.call(prompt,d,{'judge':JUDGE})
            try:
                records,errors=grades(job,raw,rubric,cases,texts,plan)
                lh.write(d/'accepted.json',records);lh.write(d/'invalid.json',errors)
            except (ValueError,KeyError,TypeError) as exc:lh.write(d/'invalid.json',[dict(error=str(exc))])
        return job['id']
    except Exception as exc:
        if not (d/'result.json').exists():lh.write(d/'result.json',dict(completed=False,reported_tokens=None,error=type(exc).__name__))
        lh.write(d/'failure.json',dict(error=type(exc).__name__))
        return job['id']+' failed; no retry'

def run():
    plan,cases=load()
    with pairwise.locked(WORK):
        lh.require(all(r['finished'] for r in ledger(plan)),'Unfinished reservation: inspect, never replay')
        with ProcessPoolExecutor(max_workers=plan['max_workers']) as pool:
            active={}
            while True:
                texts=texts_for(plan,cases);rows=ledger(plan)
                for job in plan['jobs']:
                    if len(active)>=plan['max_workers']:break
                    d=directory(job)
                    if (reservation(job)).exists():continue
                    if job['stage']=='judge' and not all((job['case'],e['config'],CAND) in texts for e in job['pairs']):continue
                    if not allowed(plan,job,rows):continue
                    lh.write(reservation(job),dict(plan_sha256=plan['plan_sha256'],job=job))
                    active[pool.submit(execute,job)]=job;rows=ledger(plan)
                if not active:break
                done,_=wait(active,timeout=5,return_when=FIRST_COMPLETED)
                for f in done:
                    job=active.pop(f)
                    try:message=f.result()
                    except Exception as exc:message=job['id']+' worker failure '+type(exc).__name__
                    rows=ledger(plan)
                    print(json.dumps(dict(job=message,calls_reserved=len(rows),finished=sum(r['finished'] for r in rows),known_tokens=sum(r['reported_tokens'] or 0 for r in rows),codex_credit_estimate=round(sum(r['codex_credits'] for r in rows),2))),flush=True)
        report()

def report():
    plan,cases=load();texts=texts_for(plan,cases);rubric=(OUT/'rubric.txt').read_text();records=[];answers=[];missing=[]
    for job in plan['jobs']:
        if job['stage']!='judge':continue
        d=directory(job)
        if not (d/'accepted.json').exists():missing.append(job['id']);continue
        raw=(d/'answer.txt').read_text();new,errors=grades(job,raw,rubric,cases,texts,plan)
        lh.require(new==lh.read(d/'accepted.json'),'Cached grade changed')
        lh.require(lh.read(d/'request.json')['prompt']==prior.request(job,rubric,cases,texts)[0],'Judge prompt mismatch')
        records+=new;answers.append(dict(job=job['id'],answer=raw,invalid=errors))
    expected={(cid,cfg,ref) for cid in cases for cfg in CONFIGS for ref in ('none','v4')};actual=[(r['case'],r['config'],r['reference']) for r in records]
    lh.require(len(actual)==len(set(actual)) and set(actual)<=expected,'Duplicate/unknown verdict')
    rows=ledger(plan);complete=set(actual)==expected
    usage=dict(calls=len(rows),writing_calls=sum(r['stage']=='generation' for r in rows),judge_calls=sum(r['stage']=='judge' for r in rows),claude_calls=sum(r['config']=='sonnet-high' for r in rows),known_reported_tokens=sum(r['reported_tokens'] or 0 for r in rows),unknown_attempts=sum(r['finished'] and not r['known'] for r in rows),codex_paid_credit_equivalent=sum(r['codex_credits'] for r in rows if r['known']),budget_charged_tokens=sum(r['charged_tokens'] for r in rows),budget_charged_codex_credits=sum(r['codex_credits'] for r in rows),attempts=rows,note='Paid-credit equivalent, not account debit or subscription percentage. Claude usage separate. Guards reserve active calls; overshoot can occur inside a call. Coordinator usage excluded.')
    coverage=dict(complete=complete,accepted=len(records),expected=120,outputs=sum(k[2]==CAND for k in texts),expected_outputs=60,missing_batches=missing,missing_pairs=[list(k) for k in sorted(expected-set(actual))])
    summary={}
    if complete:
        for ref in ('none','v4'):
            summary[ref]={}
            for cfg in (*CONFIGS,'all'):
                rs=[r for r in records if r['reference']==ref and (cfg=='all' or r['config']==cfg)]
                summary[ref][cfg]=dict(overall=prior.net_stats(rs),nonproof=prior.net_stats([r for r in rs if cases[r['case']]['category']!='proof']),categories={cat:prior.net_stats([r for r in rs if cases[r['case']]['category']==cat]) for cat in prior.CATEGORIES},dimensions={dim:prior.net_stats(rs,dim) for dim in pairwise.DIMENSIONS},candidate_error_flags=sum(r['candidate_material_error'] for r in rs),reference_error_flags=sum(r['reference_material_error'] for r in rs))
    outputs=[dict(case=c,config=cfg,arm=arm,response=s,response_sha256=pairwise.text_hash(s)) for (c,cfg,arm),s in sorted(texts.items())]
    for name,value in [('responses.json',outputs),('observations.json',records),('judge-responses.json',answers),('usage.json',usage),('coverage.json',coverage),('summary.json',summary)]:lh.public_safe(value);lh.write(OUT/name,value)
    lines=['# Restored v9: 20-case development check','','Existing balanced development subset, four cases each for ordinary prose, research, arguments, proofs and controls. Astra high, Sol low and Sonnet high, unchanged Sol-high author-specific blind judge. Saved no-skill/v4 baselines were source/model/bundle/hash checked. This is previously inspected development data, not fresh OOS validation. Fully inlined bundles do not test selective loading or long-horizon retention.','',f'Coverage: {coverage["outputs"]}/60 outputs; {len(records)}/120 primary comparisons. Missing or invalid grades are never ties.']
    if complete:
        lines+=['','| Generator / effort | Restored v9 vs none | Restored v9 vs v4 |','|---|---|---|']
        for cfg in (*CONFIGS,'all'):
            vals=[]
            for ref in ('none','v4'):
                s=summary[ref][cfg]['overall'];vals.append(f'{s["net_pp"]:+.1f} pp [{s["net_ci95_pp"][0]:+.1f}, {s["net_ci95_pp"][1]:+.1f}]; {s["wins"]}W/{s["ties"]}T/{s["losses"]}L')
            lines.append('| '+cfg+' | '+' | '.join(vals)+' |')
        lines+=['','Net advantage is win rate minus loss rate; ties contribute zero. Intervals bootstrap cases, not individual votes. One fallible judge, no new order audits or human calibration. Saved baselines retain a possible backend/time confound.','', '| Category | Model | vs none (pp) | vs v4 (pp) |','|---|---|---:|---:|']
        for cat in prior.CATEGORIES:
            for cfg in CONFIGS:lines.append(f'| {cat} | {cfg} | {summary["none"][cfg]["categories"][cat]["net_pp"]:+.1f} | {summary["v4"][cfg]["categories"][cat]["net_pp"]:+.1f} |')
    else:lines+=['','INCOMPLETE: no headline aggregate. Inspect missing_pairs in coverage.json and retained failure evidence. No automatic retries.']
    lines+=['',f'Usage: {usage["calls"]}/100 calls, {usage["known_reported_tokens"]:,} reported tokens, {usage["unknown_attempts"]} unknown attempts. Estimated Codex paid-credit equivalent: {usage["codex_paid_credit_equivalent"]:.2f}, plus Claude usage from {usage["claude_calls"]}/20 calls. Hard call cap and reservation guards: 2.5M tokens, 300 Codex credits. These are not subscription percentages or actual billed totals.','', 'Fresh holdouts remain untouched. Candidate and judge were frozen before execution. No skill installation or automatic promotion.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n');print(json.dumps(coverage),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','run','report']);a=p.parse_args();globals()[a.action]()
