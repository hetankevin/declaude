#!/usr/bin/env python3
"""Three known development cases, cached baselines, no retries or holdout reads."""
import argparse
import json
from pathlib import Path
import bench
import context_regrade as context
import grade_long_horizon as transport
import long_horizon as lh
import pairwise
import prose_repair as prior

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evals/results/prose-repair/v9-small'
WORK=ROOT/'.local/prose-repair/v9-small'
IDS=['large-dev-b-09','large-dev-a-12','large-dev-b-14']
WRITER={'model':'gpt-6-astra','effort':'high'}
JUDGE={'model':'gpt-6.1-sol','effort':'high'}
SPENT_SMOKE=92604


def freeze():
    lh.require(not OUT.exists(),'Already frozen')
    cases={c['id']:c for c in prior.development('tune')+prior.development('validation') if c['id'] in IDS}
    base=[r for r in prior.baselines(list(cases.values())) if r['config']=='astra-high']
    for c in cases.values():
        c['user_context']=context.CONTEXT['common']+'\n\n'+context.CONTEXT[c['category']]
        c['is_proof']=c['category']=='proof'
    jobs=[]
    for i,cid in enumerate(IDS):
        for order in (['primary','reversed'] if i==0 else ['primary']):
            pairs=[dict(case=cid,config='astra-high',candidate='v9-dev',reference=ref,judge='sol-high',order=order,label=f'P{j+1:02d}',a_side='right' if (i+j+(order=='reversed'))%2==0 else 'left') for j,ref in enumerate(['none','v4'])]
            jobs.append(dict(id=cid+'-'+order,case=cid,judge='sol-high',order=order,pairs=pairs))
    jobs.sort(key=lambda j:j['order']!='primary')
    source=ROOT/'evals/results/context-regrade'
    values={'cases.json':list(cases.values()),'baselines.json':base,'author-context.json':context.CONTEXT}
    for name,v in values.items():lh.public_safe(v);lh.write(OUT/name,v)
    for name,data in [('bundle.txt',bench.bundle(ROOT/'evals/versions/v9-dev')),('rubric.txt',(source/'rubric.txt').read_text())]:
        lh.public_safe(data);lh.write(OUT/name,data.encode())
    plan=dict(candidate='v9-dev',selection='Two previously observed Astra-high argument losses and one proof guard. Development debugging, not independent validation.',ids=IDS,writer=WRITER,judge=JUDGE,jobs=jobs,max_generations=3,max_judges=4,generation_total_token_guard=250000,earlier_smoke_tokens=SPENT_SMOKE,writer_reservation=25000,judge_token_guard=50000,judge_reservation=12500,retries=0,packing='Same fully inlined portable bundle format as saved baselines; this does not test selective reference loading.',release='Retain v4 if any final candidate loss to no skill, any proof loss to v4, any major material error, invalid/missing primary grades, or a manual substantive regression. Otherwise installation is provisional, limited by three selected development cases.',files={p.name:lh.hashed(p) for p in OUT.iterdir()},scripts={n:lh.hashed(ROOT/'tools'/n) for n in ['small_repair.py','grade_long_horizon.py','long_horizon.py','prose_repair.py','context_regrade.py','pairwise.py']})
    plan['plan_sha256']=pairwise.digest(plan)
    lh.write(OUT/'plan.json',plan)


def load():
    plan=lh.read(OUT/'plan.json')
    lh.require(plan['plan_sha256']==pairwise.digest({k:v for k,v in plan.items() if k!='plan_sha256'}),'Plan changed')
    for n,h in plan['files'].items():lh.require(lh.hashed(OUT/n)==h,'Frozen input changed')
    for n,h in plan['scripts'].items():lh.require(lh.hashed(ROOT/'tools'/n)==h,'Frozen script changed')
    cases={c['id']:c for c in lh.read(OUT/'cases.json')}
    texts={(r['case'],r['config'],r['arm']):r['response'] for r in lh.read(OUT/'baselines.json')}
    return plan,cases,texts,(OUT/'rubric.txt').read_text()


def spent(stage):
    n=t=0
    for p in (WORK/stage).glob('*/request.json'):
        n+=1;r=p.with_name('result.json')
        lh.require(r.exists(),'Ambiguous prior attempt: do not replay')
        data=lh.read(r);raw=p.with_name('cli.jsonl')
        lh.require(data['cli_sha256']==lh.hashed(raw),'Raw evidence changed')
        value=lh.parse_cli(raw.read_bytes())['reported_tokens']
        lh.require(value is not None,'Missing usage: no further calls')
        t+=value
    return n,t


def generations(plan,cases,texts,run=False):
    bundle=(OUT/'bundle.txt').read_text()
    for cid in IDS:
        d=WORK/'generation'/cid
        prompt=prior.generation_prompt(cases[cid],bundle)
        if not (d/'request.json').exists() and run:
            n,t=spent('generation')
            if n>=3 or t+SPENT_SMOKE+25000>250000:break
            transport.call(prompt,d,{'judge':WRITER})
            print('written '+cid,flush=True)
        if (d/'result.json').exists() and (d/'answer.txt').exists():
            result=lh.read(d/'result.json')
            lh.require(result['completed'] and not result['failed'] and result['exit_code']==0,'Unsuccessful writing')
            lh.require(lh.read(d/'request.json')['prompt']==prompt,'Generation prompt changed')
            texts[cid,'astra-high','v9-dev']=(d/'answer.txt').read_text()
    return texts


def run():
    plan,cases,texts,rubric=load()
    with pairwise.locked(WORK):
        generations(plan,cases,texts,True)
        for job in plan['jobs']:
            if (job['case'],'astra-high','v9-dev') not in texts:continue
            d=WORK/'judge'/job['id']
            prompt,_,_=prior.request(job,rubric,cases,texts)
            if not (d/'request.json').exists():
                n,t=spent('judge')
                if n>=4 or t+12500>50000:break
                raw=transport.call(prompt,d,{'judge':JUDGE})
            else:
                lh.require(lh.read(d/'request.json')['prompt']==prompt,'Grading prompt changed')
                if not (d/'answer.txt').exists():continue
                raw=(d/'answer.txt').read_text()
            try:
                records=prior.records_for(job,raw,1,rubric,cases,texts,plan)
                lh.write(d/'accepted.json',records)
                print(job['id']+': '+','.join(r['outcome'] for r in records),flush=True)
            except (ValueError,KeyError,TypeError) as e:
                lh.write(d/'invalid.json',{'error':str(e)})
                print(job['id']+': invalid, no retry',flush=True)
    report()


def report():
    plan,cases,texts,rubric=load();generations(plan,cases,texts)
    records=[];missing=[];raw_answers=[]
    for job in plan['jobs']:
        d=WORK/'judge'/job['id']
        if not (d/'accepted.json').exists():
            missing.append({'job':job['id'],'status':'invalid' if (d/'invalid.json').exists() else 'unrun'});continue
        raw=(d/'answer.txt').read_text()
        r=prior.records_for(job,raw,1,rubric,cases,texts,plan)
        lh.require(r==lh.read(d/'accepted.json'),'Verdict changed')
        records+=r;raw_answers.append({'job':job['id'],'answer':raw})
    wn,wt=spent('generation');jn,jt=spent('judge')
    usage={'writing_calls':wn,'writing_reported_tokens':wt,'earlier_file_smoke_calls':1,'earlier_file_smoke_reported_tokens':SPENT_SMOKE,'judge_calls':jn,'judge_reported_tokens':jt,'total_calls':wn+jn+1,'total_reported_tokens':wt+jt+SPENT_SMOKE,'missing_jobs':missing,'note':'CLI input plus output tokens, including cached inputs; not billing or account quota. No retries.'}
    rows=[{'case':cid,'config':cfg,'arm':arm,'response':s,'response_sha256':pairwise.text_hash(s)} for (cid,cfg,arm),s in sorted(texts.items())]
    for name,value in [('responses.json',rows),('observations.json',records),('judge-responses.json',raw_answers),('usage.json',usage)]:
        lh.public_safe(value);lh.write(OUT/name,value)
    lines=['# Small v9 development check','','Three selected cases: two known Astra-high argument failures and one proof guard. Saved no-skill and v4 baselines are reused. All new writing uses Astra high; the unchanged author-specific rubric is judged by Sol high. This is targeted development debugging, not OOS or general validation.','','| Case | Comparison | Primary | Reversed order |','|---|---|---|---|']
    for cid in IDS:
        for ref in ['none','v4']:
            rs=[r for r in records if r['case']==cid and r['reference']==ref]
            by={r['order']:r['outcome'] for r in rs}
            lines.append(f'| {cid} | {ref} | {by.get("primary","ungraded")} | {by.get("reversed","unrun")} |')
    lines+=['','| Comparison | Wins | Ties | Losses | Net advantage (pp) |','|---|---:|---:|---:|---:|']
    for ref in ['none','v4']:
        rs=[r for r in records if r['reference']==ref and r['order']=='primary']
        w,t,l=[sum(r['outcome']==k for r in rs) for k in ['win','tie','loss']]
        score=f'{100*(w-l)/len(rs):+.1f}' if rs else 'ungraded'
        lines.append(f'| {ref} | {w} | {t} | {l} | {score} |')
    lines+=['','Ties contribute zero; order audits are excluded. No confidence interval is meaningful from these three deliberately selected cases. Missing judgments are not ties. Baselines were generated earlier; matching model labels do not prove an unchanged backend. The full bundle is inlined as in the earlier benchmark, so this does not test the selective-loading change.','','The separate persistent file-editing pilot was stopped after its first turn used 92,604 reported tokens. Its session validator also encountered a newer transcript format. That completed draft is retained privately without replay, and supplies no comparative or long-horizon performance result. The two fresh six-turn cases and earlier 30-case holdout remain sealed/unrun.','',f'This pass used {usage["total_calls"]} benchmark calls and {usage["total_reported_tokens"]:,} reported tokens, including the stopped file-editing smoke. Cached input tokens may be included; this is not billing or account quota. No Claude calls and no retries.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(usage),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['freeze','run','report']);a=ap.parse_args();globals()[a.action]()
