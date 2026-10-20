#!/usr/bin/env python3
"""Read-only reconstruction after a transport stop; never launches a model."""
import json
from pathlib import Path
import long_horizon as lh
import pairwise
import prose_repair as prior
import small_repair as small


def main():
    plan,cases,texts,rubric=small.load()
    small.generations(plan,cases,texts)
    records=[];answers=[];jobs=[];attempts=[]
    for stage in ['generation','judge']:
        for p in sorted((small.WORK/stage).glob('*/request.json')):
            result=lh.read(p.with_name('result.json'))
            lh.require(lh.hashed(p.with_name('cli.jsonl'))==result['cli_sha256'],'CLI changed')
            parsed=lh.parse_cli(p.with_name('cli.jsonl').read_bytes())
            lh.require(parsed['reported_tokens']==result['reported_tokens'],'Usage changed')
            attempts.append(dict(stage=stage,id=p.parent.name,completed=parsed['completed'],reported_tokens=parsed['reported_tokens'],usage=parsed['usage'],transport_failed=not parsed['completed']))
    for job in plan['jobs']:
        d=small.WORK/'judge'/job['id']
        prompt,supplied,pairs=prior.request(job,rubric,cases,texts)
        if (d/'request.json').exists():lh.require(lh.read(d/'request.json')['prompt']==prompt,'Prompt changed')
        if (d/'accepted.json').exists():
            raw=(d/'answer.txt').read_text()
            rs=prior.records_for(job,raw,1,rubric,cases,texts,plan)
            lh.require(rs==lh.read(d/'accepted.json'),'Grades changed')
            records+=rs;answers.append(dict(job=job['id'],answer=raw))
            jobs.append(dict(id=job['id'],status='accepted'))
        else:
            status='transport_failed' if (d/'result.json').exists() else 'unrun'
            jobs.append(dict(id=job['id'],status=status))
    rows=[dict(case=cid,config=cfg,arm=arm,response=s,response_sha256=pairwise.text_hash(s)) for (cid,cfg,arm),s in sorted(texts.items())]
    usage=dict(calls_including_file_smoke=len(attempts)+1,reported_tokens_known_subtotal=sum(r['reported_tokens'] or 0 for r in attempts)+small.SPENT_SMOKE,unreported_attempts=sum(r['reported_tokens'] is None for r in attempts),earlier_file_smoke_reported_tokens=small.SPENT_SMOKE,attempts=attempts,claude_calls=0,note='Input plus output tokens, including cached input. Failed-call usage is unknown, not zero. Coordinator/helper usage is separate. No billing or account-percentage inference.')
    decision=dict(candidate='v9-dev',installed='v4',promoted=False,reason='Missing primary grades after transport timeout. Frozen release conditions are not met. No further model calls scheduled.',proof_reference_unchanged=True,research_voice_reference_unchanged=True,holdouts='Both fresh holdouts remain sealed and unrun.',status='incomplete; candidate saved, general Codex prose repair unresolved')
    for name,value in [('responses.json',rows),('observations.json',records),('judge-responses.json',answers),('coverage.json',jobs),('usage.json',usage),('release-decision.json',decision)]:
        lh.public_safe(value);lh.write(small.OUT/name,value)
    lines=['# Small v9 development check — incomplete','',
      'V9 simplifies the prose instructions, separates argument editing from rhetorical compression, and preserves proof and research-voice reference files byte-for-byte. Three new Astra-high drafts are saved. A Sol-high transport timeout stopped grading after the first case. V4 remains packaged and installed; the general Codex prose repair is unresolved.','',
      '| Selected development case | vs no skill | vs v4 |','|---|---|---|',
      '| Museum recommendation | tie | win |','| Reporting-policy argument | ungraded | ungraded |','| Finite-population proof | ungraded | ungraded |','',
      'The two accepted judgments concern one case only. They use the unchanged author-specific rubric and anonymous A/B texts. There is no aggregate improvement claim, order check, or new OOS result. Missing judgments are not ties. These cases were selected from known development weaknesses, and saved baselines were generated earlier.','',
      'The full bundle is inlined, matching the prior benchmark format. This does not test selective reference loading. The [manual artifact review](artifact-review.md) finds the proof valid and the argument changes mixed; it is not an independent blind grade.','',
      'The separate persistent file-editing pilot stopped after its first no-skill turn used 92,604 reported tokens. Its validator also encountered a newer transcript format. That completed draft is retained privately without replay. No matched or long-horizon result exists. The new two-case six-turn holdout and the earlier 30-case holdout remain sealed/unrun and privately backed up.','',
      f'This pass made {usage["calls_including_file_smoke"]} benchmark calls: one file-editing smoke, three isolated rewrites, and two grading calls. The known subtotal is {usage["reported_tokens_known_subtotal"]:,} CLI-reported tokens, including cached input; the failed grading call reported no usage. This is not a complete token total, billing estimate, or account-quota measurement. No Claude calls, replacement generations, or application-level retries were made. The failed call attempted internal transport reconnection. No jobs remain running.','',
      'The original frozen plans and raw failed evidence are retained. This report uses a read-only finalizer because the original runner deliberately stops on missing successful usage. Reproduce without model calls: `python3 tools/finalize_small_repair.py`. Do not resume the benchmark automatically.']
    (small.OUT/'report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'calls':usage['calls_including_file_smoke'],'known_tokens':usage['reported_tokens_known_subtotal'],'unknown_usage_calls':usage['unreported_attempts'],'accepted_judgments':len(records),'promoted':False}))

if __name__=='__main__':main()
