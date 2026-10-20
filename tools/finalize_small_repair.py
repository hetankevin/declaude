#!/usr/bin/env python3
"""Revalidate and publish saved drafts/grades only; never launches a model."""
import json
import long_horizon as lh
import pairwise
import prose_repair as prior
import small_repair as small


def main():
    plan,cases,texts,rubric=small.load()
    small.generations(plan,cases,texts,run=False)
    records=[];answers=[];jobs=[];attempts=[]
    completion=small.WORK/'completion-20261020'
    for stage,root in [('generation',small.WORK/'generation'),('judge',small.WORK/'judge'),('judge-completion',completion)]:
        for p in sorted(root.glob('*/request.json')):
            result=lh.read(p.with_name('result.json'))
            lh.require(lh.hashed(p.with_name('cli.jsonl'))==result['cli_sha256'],'CLI changed')
            parsed=lh.parse_cli(p.with_name('cli.jsonl').read_bytes())
            lh.require(parsed['reported_tokens']==result['reported_tokens'],'Usage changed')
            attempts.append(dict(stage=stage,id=p.parent.name,completed=parsed['completed'],reported_tokens=parsed['reported_tokens'],usage=parsed['usage'],transport_failed=not parsed['completed']))
    for job in plan['jobs']:
        old=small.WORK/'judge'/job['id'];new=completion/job['id']
        prompt,_,_=prior.request(job,rubric,cases,texts)
        for d in [old,new]:
            if (d/'request.json').exists():lh.require(lh.read(d/'request.json')['prompt']==prompt,'Prompt changed')
        accepted=[d for d in [old,new] if (d/'accepted.json').exists()]
        lh.require(len(accepted)<=1,'Duplicate accepted comparison')
        if accepted:
            d=accepted[0];raw=(d/'answer.txt').read_text()
            rs=prior.records_for(job,raw,1,rubric,cases,texts,plan)
            lh.require(rs==lh.read(d/'accepted.json'),'Grades changed')
            records+=rs;answers.append(dict(job=job['id'],answer=raw))
            jobs.append(dict(id=job['id'],order=job['order'],status='accepted',source='completion' if d==new else 'original'))
        else:
            status='invalid' if any((d/'invalid.json').exists() for d in [old,new]) else 'transport_failed' if any((d/'result.json').exists() for d in [old,new]) else 'unrun'
            jobs.append(dict(id=job['id'],order=job['order'],status=status))
    rows=[dict(case=cid,config=cfg,arm=arm,response=s,response_sha256=pairwise.text_hash(s)) for (cid,cfg,arm),s in sorted(texts.items())]
    # Frozen published writing bytes are never rewritten during grading completion.
    lh.require(rows==lh.read(small.OUT/'responses.json'),'Saved drafts differ')
    extra=[r for r in attempts if r['stage']=='judge-completion']
    usage=dict(calls_including_file_smoke=len(attempts)+1,reported_tokens_known_subtotal=sum(r['reported_tokens'] or 0 for r in attempts)+small.SPENT_SMOKE,unreported_attempts=sum(r['reported_tokens'] is None for r in attempts),earlier_file_smoke_reported_tokens=small.SPENT_SMOKE,attempts=attempts,claude_calls=0,completion=dict(new_judge_calls=len(extra),new_generation_calls=0,reported_tokens_known_subtotal=sum(r['reported_tokens'] or 0 for r in extra),unreported_attempts=sum(r['reported_tokens'] is None for r in extra)),note='Input plus output tokens, including cached input. Failed-call usage is unknown, not zero. Coordinator/helper usage is separate. No billing or account-percentage inference.')
    primary=[r for r in records if r['order']=='primary']
    failures=[]
    if len(primary)!=6:failures.append('Missing primary grades')
    for r in primary:
        if r['reference']=='none' and r['outcome']=='loss':failures.append(r['case']+': loss to no skill')
        if r['reference']=='v4' and cases[r['case']]['is_proof'] and r['outcome']=='loss':failures.append(r['case']+': proof loss to v4')
        if r['raw_judgment']['material_errors'][r['candidate_position']]['severity']=='major':failures.append(r['case']+': major material error')
    decision=dict(candidate='v9-dev',installed='v4',promoted=False,primary_grading_complete=len(primary)==6,failures=sorted(set(failures)),reason='Retain v4: '+ '; '.join(sorted(set(failures))) if failures else 'Primary grade checks pass on three selected development cases. This task completed grading only; no installation change.',proof_reference_unchanged=True,research_voice_reference_unchanged=True,holdouts='Both fresh holdouts remain sealed and unrun.',status='primary grading complete' if len(primary)==6 else 'incomplete')
    for name,value in [('observations.json',records),('judge-responses.json',answers),('coverage.json',jobs),('usage.json',usage),('release-decision.json',decision)]:
        lh.public_safe(value);lh.write(small.OUT/name,value)
    labels={'large-dev-b-09':'Museum recommendation','large-dev-a-12':'Reporting-policy argument','large-dev-b-14':'Finite-population proof'}
    lines=['# Small v9 development check','',f'{len(primary)}/6 primary pairwise judgments accepted across three selected Astra-high development drafts. The original museum comparison is reused. The authorized completion grades saved drafts only, with the same Sol-high judge, author-specific rubric, context and anonymous A/B order. No text was regenerated or edited.','', '| Selected development case | vs no skill | vs v4 |','|---|---|---|']
    for cid in small.IDS:
        outcomes={r['reference']:r['outcome'] for r in primary if r['case']==cid}
        lines.append(f'| {labels[cid]} | {outcomes.get("none","ungraded")} | {outcomes.get("v4","ungraded")} |')
    lines+=['','| Comparison | Wins | Ties | Losses | Net advantage (pp) |','|---|---:|---:|---:|---:|']
    for ref in ['none','v4']:
        group=[r for r in primary if r['reference']==ref];counts=[sum(r['outcome']==x for r in group) for x in ['win','tie','loss']]
        w,t,l=counts;net=f'{100*(w-l)/len(group):+.1f}' if group else 'ungraded'
        lines.append(f'| {ref} | {w} | {t} | {l} | {net} |')
    lines+=['','Ties contribute zero. These are three deliberately selected development cases, not a fresh test or stable population estimate. One fallible judge was used. The reversed-order audit is omitted to save usage; it is not counted as a tie. Saved baselines were generated earlier, so matching model labels do not prove an unchanged backend.','', '## Decision','',decision['reason']+'. Packaged and installed v4 remain unchanged. No further calls are queued.','', '## Decisive comparisons','']
    for r in primary:
        if r['case']=='large-dev-b-09':continue
        lines.append(f'**{labels[r["case"]]} versus {r["reference"]}: {r["outcome"]}. '+r['raw_judgment']['dimensions']['overall']['reason'])
        lines.append('')
    lines+=['## Scope and usage','', 'The full bundle was inlined, matching the prior benchmark format. Selective reference loading was not tested. The [artifact review](artifact-review.md) is coordinator inspection, not an independent human grade. Proof and research-voice references remain byte-identical to v4.','', 'The separate file-editing pilot stopped after one no-skill turn and a transcript-format validation failure. There is no matched long-horizon result. The fresh two-case six-turn holdout and earlier 30-case holdout remain sealed/unrun.','',f'The grading completion used {len(extra)} new judge calls and zero writing calls, reporting {usage["completion"]["reported_tokens_known_subtotal"]:,} tokens. The full small pass now has {usage["calls_including_file_smoke"]} benchmark calls and a known subtotal of {usage["reported_tokens_known_subtotal"]:,} reported tokens. The earlier failed judge call has unknown usage and is retained. These counts include cached inputs and are not billing or account quota. No automatic retry or order audit was run in the completion.','', 'Reproduce without model calls: `python3 tools/finalize_small_repair.py`. Original frozen plans, completed grades and failed-attempt evidence are preserved.']
    (small.OUT/'report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'completion':usage['completion'],'accepted_primary':len(primary),'decision':decision['reason']}))

if __name__=='__main__':main()
