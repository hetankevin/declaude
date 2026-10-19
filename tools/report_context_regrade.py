#!/usr/bin/env python3
"""Validate and summarize the frozen author-context regrade. No model calls."""
import argparse, collections, gzip, json, statistics
from pathlib import Path
import context_regrade as run
import pairwise
from pairwise_report import aggregate, CONFIGS

CATEGORIES=['ordinary','research','argument','proof','control']
DIMENSIONS=['meaning','naturalness','progression','voice','proof']

def require(ok, message):
    if not ok: raise ValueError(message)

def validate_batch(job, records, raw, attempt, rubric, cases, texts):
    prompt,supplied,pairs=run.request(job,rubric,cases,texts)
    require(len(records)==len(job['pairs']), 'Batch cardinality mismatch')
    require(len({r['pair_id'] for r in records})==len(records), 'Duplicate pair ID')
    by={r['pair_id']:r for r in records}
    parsed=pairwise.parse_answer(raw)
    require(set(parsed)==set(pairs)==set(by), 'Batch labels mismatch')
    for e in job['pairs']:
        r=by[e['label']]
        require(r['record_sha256']==pairwise.digest({k:v for k,v in r.items() if k!='record_sha256'}), 'Record hash mismatch')
        label='A' if e['a_side']=='right' else 'B'
        expected=dict(version='context-regrade-v1',batch=job['id'],case=e['case'],config=e['config'],candidate=e['candidate'],reference='none',judge=job['judge'],order=job['order'],candidate_position=label,attempt=attempt,pair_id=e['label'],response_sha256={arm:pairwise.text_hash(texts[e['case'],e['config'],arm]) for arm in ['none',e['candidate']]},prompt_sha256=pairwise.text_hash(prompt),rubric_sha256=pairwise.text_hash(rubric),context_sha256=pairwise.text_hash(supplied['user_context']),raw_sha256=pairwise.text_hash(raw))
        require(all(r.get(k)==v for k,v in expected.items()), 'Record identity or input hash mismatch')
        per=dict(supplied,responses=pairs[e['label']])
        verdict,repairs=pairwise.repair_math_delimiter_quotes(parsed[e['label']],per)
        verdict=pairwise.validate_verdict(verdict,per)
        require(verdict==r['raw_judgment'] and repairs==r['evidence_format_repairs'], 'Raw verdict mismatch')
        require(all(r.get(k)==v for k,v in pairwise.normalized(verdict,label).items()), 'Normalized verdict mismatch')

def read_records(allow_partial=False):
    plan,rubric,cases,texts=run.load()
    records=[]; raw_answers=[]; missing=[]; attempts=[]
    for job in plan['jobs']:
        d=run.WORK/job['id']; p=d/'records.json'
        for a in range(1,plan['max_attempts_per_batch']+1):
            s=d/f'attempt-{a}.json'
            if s.exists():
                status=json.loads(s.read_text())
                call=status.get('call',{})
                if call: require((call['model'],call['effort'])==run.JUDGES[job['judge']][1:], 'Wrong judge provider/model/effort')
                attempts.append(dict(batch=job['id'],judge=job['judge'],attempt=a,state=status['state'],invalid=(d/f'attempt-{a}.invalid.json').exists(),call=call,raw_sha256=status.get('raw_sha256')))
        if not p.exists():missing.append(job['id']);continue
        rs=json.loads(p.read_text()); at={r['attempt'] for r in rs}
        require(len(at)==1 and at<=set(range(1,plan['max_attempts_per_batch']+1)), 'Invalid attempt number')
        attempt=next(iter(at));raw=(d/f'attempt-{attempt}.txt').read_text()
        status=json.loads((d/f'attempt-{attempt}.json').read_text())
        require(status['state']=='answered' and status['raw_sha256']==pairwise.text_hash(raw),'Raw status mismatch')
        validate_batch(job,rs,raw,attempt,rubric,cases,texts)
        records.extend(rs);raw_answers.append(dict(batch=job['id'],attempt=attempt,text=raw))
    require(allow_partial or not missing, f'{len(missing)} batches missing; use --partial only for an explicitly provisional snapshot')
    keys=[(r['case'],r['config'],r['candidate'],r['judge'],r['order']) for r in records]
    require(len(keys)==len(set(keys)), 'Duplicate observations')
    return plan,cases,texts,records,raw_answers,attempts,missing

def read_published(folder):
    """Revalidate portable public evidence without private CLI directories."""
    plan,rubric,cases,texts=run.load()
    require(json.loads((folder/'coverage.json').read_text())['status']=='complete','Published snapshot is incomplete')
    records=[r for arm in plan['candidates'] for r in json.loads((folder/(arm+'-observations.json')).read_text())]
    raw=[json.loads(line) for line in gzip.decompress((folder/'judge-responses.jsonl.gz').read_bytes()).decode().splitlines()]
    byraw={r['batch']:r for r in raw};byrecords=collections.defaultdict(list)
    for r in records:byrecords[r['batch']].append(r)
    ids={j['id'] for j in plan['jobs']}
    require(len(byraw)==len(raw) and set(byraw)==set(byrecords)==ids,'Published batch matrix mismatch')
    for j in plan['jobs']:
        r=byraw[j['id']]
        require(1<=r['attempt']<=plan['max_attempts_per_batch'],'Published attempt out of range')
        validate_batch(j,byrecords[j['id']],r['text'],r['attempt'],rubric,cases,texts)
    attempts=json.loads((folder/'attempts.json').read_text())
    return plan,cases,texts,records,raw,attempts,[]

def balanced_cases(records,candidates=('v4','v5a')):
    keys={(r['case'],r['config'],r['candidate'],r['judge']) for r in records if r['order']=='primary'}
    return sorted(c for c in {r['case'] for r in records} if all((c,cfg,arm,j) in keys for cfg in CONFIGS for arm in candidates for j in run.JUDGES))

def summaries(records,cases):
    summary={}
    for split in ['development','holdout']:
        summary[split]={}
        for cfg in CONFIGS+['claude-all','codex-all','all']:
            configs=CONFIGS[:6] if cfg=='claude-all' else CONFIGS[6:] if cfg=='codex-all' else CONFIGS if cfg=='all' else [cfg]
            rs=[r for r in records if cases[r['case']]['split']==split and r['config'] in configs]
            summary[split][cfg]=dict(overall=aggregate(rs),categories={cat:aggregate([r for r in rs if cases[r['case']]['category']==cat]) for cat in CATEGORIES},dimensions={dim:aggregate(rs,dim) for dim in DIMENSIONS},judges={j:aggregate([r for r in rs if r['judge']==j]) for j in run.JUDGES},material_errors={arm:dict(flags=sum(r[arm+'_material_error'] for r in rs),judgments=len(rs)) for arm in ['candidate','reference']})
    return summary

def reliability(records):
    primary=[r for r in records if r['order']=='primary']
    cross=collections.defaultdict(dict); orders=collections.defaultdict(dict)
    for r in primary: cross[r['case'],r['config'],r['candidate']][r['judge']]=r
    for r in records: orders[r['case'],r['config'],r['candidate'],r['judge']][r['order']]=r
    def counts(pairs):
        return dict(pairs=len(pairs),same=sum(a['outcome']==b['outcome'] for a,b in pairs),opposite=sum({a['outcome'],b['outcome']}=={'win','loss'} for a,b in pairs),cases=len({a['case'] for a,b in pairs}))
    crosspairs=[tuple(v[j] for j in run.JUDGES) for v in cross.values() if set(v)==set(run.JUDGES)]
    orderpairs=[(v['primary'],v['reversed']) for v in orders.values() if set(v)=={'primary','reversed'}]
    return dict(cross_judge=counts(crosspairs),order=counts(orderpairs),order_by_judge={j:counts([(a,b) for a,b in orderpairs if a['judge']==j]) for j in run.JUDGES},by_candidate={arm:dict(cross_judge=counts([(a,b) for a,b in crosspairs if a['candidate']==arm]),order=counts([(a,b) for a,b in orderpairs if a['candidate']==arm])) for arm in ['v4','v5a','v6-dev','v7-dev']})

def old_new(records,cases):
    old=json.loads((run.ROOT/'evals/results/large-interim/pairwise-v5a-vs-none.json').read_text())
    old={(r['case'],r['config']):r for r in old if r['judge']=='astra-high' and r['order']=='primary'}
    new={(r['case'],r['config']):r for r in records if r['judge']=='astra-high' and r['order']=='primary' and r['candidate']=='v5a'}
    common=set(old)&set(new)
    # Matched coverage only; changing coverage cannot explain this difference.
    common_cases={c for c,cfg in common if all((c,x) in common for x in CONFIGS)}
    result={}
    for split in ['development','holdout']:
        keys=sorted(k for k in common if k[0] in common_cases and cases[k[0]]['split']==split)
        result[split]=dict(old=aggregate([old[k] for k in keys]),new=aggregate([new[k] for k in keys]),changed=sum(old[k]['outcome']!=new[k]['outcome'] for k in keys),pairs=len(keys),transitions=dict(collections.Counter(old[k]['outcome']+' -> '+new[k]['outcome'] for k in keys)))
    return result

def cell(m):
    if not m:return 'NA'
    lo,hi=m['net_ci95_pp']
    return f"{m['net_pp']:+.1f} [{lo:+.1f}, {hi:+.1f}]"

def render(plan,cases,records,attempts,missing,out,plot=False):
    out.mkdir(parents=True,exist_ok=True)
    common=balanced_cases(records)
    primary=[r for r in records if r['order']=='primary']
    main=[r for r in primary if r['case'] in common and r['candidate'] in ['v4','v5a']]
    coverage=dict(status='provisional' if missing else 'complete',batches_done=plan['batches']-len(missing),batches_expected=plan['batches'],missing_batches=missing,primary_judgments=len(primary),audit_judgments=sum(r['order']=='reversed' for r in records),balanced_cases={split:[c for c in common if cases[c]['split']==split] for split in ['development','holdout']},excluded_primary=[{k:r[k] for k in ['case','config','candidate','judge']} for r in primary if r['candidate'] in ['v4','v5a'] and r['case'] not in common],category_counts={split:dict(collections.Counter(cases[c]['category'] for c in common if cases[c]['split']==split)) for split in ['development','holdout']})
    arms={arm:summaries([r for r in main if r['candidate']==arm],cases) for arm in ['v4','v5a']}
    for arm,summary in arms.items():
        dest=out/(arm+'-vs-none');dest.mkdir(exist_ok=True);run.dump(dest/'summary.json',summary)
        if plot and main:
            from plot_pairwise import plot_pairwise
            plot_pairwise(summary,dest/'plots',show_counts=True)
    checks=reliability(records); matched=old_new(records,cases)
    usage=dict(calls_started=len(attempts),calls_answered=sum(a['state']=='answered' for a in attempts),transport_errors=sum(a['state']=='transport_error' for a in attempts),invalid_attempts=sum(a['invalid'] for a in attempts),calls_with_reported_tokens=sum('reported_tokens' in a['call'].get('usage',{}) for a in attempts),reported_tokens=sum(a['call'].get('usage',{}).get('reported_tokens',0) for a in attempts),by_judge={j:dict(calls=sum(a['judge']==j for a in attempts),reported_tokens=sum(a['call'].get('usage',{}).get('reported_tokens',0) for a in attempts if a['judge']==j)) for j in run.JUDGES},claude_calls=0,writing_generations=0)
    pilots={arm:dict(overall=aggregate([r for r in primary if r['candidate']==arm]),by_config={cfg:aggregate([r for r in primary if r['candidate']==arm and r['config']==cfg]) for cfg in CONFIGS},dimensions={dim:aggregate([r for r in primary if r['candidate']==arm],dim) for dim in DIMENSIONS}) for arm in ['v6-dev','v7-dev']}
    for name,obj in [('coverage',coverage),('judge-checks',checks),('matched-old-new',matched),('usage',usage),('attempts',attempts),('pilots',pilots)]:run.dump(out/(name+'.json'),obj)
    # Full source-grounded verdicts; no CLI envelopes, private paths or identities.
    for arm in plan['candidates']:
        run.dump(out/(arm+'-observations.json'),[r for r in records if r['candidate']==arm])
    lines=['# Author-specific regrade of saved writing','',f"Status: **{coverage['status']}**, {coverage['batches_done']}/{plan['batches']} batches. This report grades saved outputs only. No writing was regenerated and no Claude judge was called.",'','Two blind Codex judges (Astra high and Sol high) apply the frozen author-specific rubric and category-relevant context. The target is the requested author\'s writing goal, including argument progression, connected prose, appropriate scope, and explicit proof steps. This is model-based assessment against stated preferences, not validation against independent human choices.','', 'Net advantage is **win rate minus loss rate**, in percentage points. Ties contribute zero. Primary results average cases equally; intervals bootstrap cases, not judge votes or configurations. Reversed-order audits never contribute to performance.','', 'The development set contains tuning and validation cases used during skill development. The original holdout is regraded retrospectively: prior outcomes informed the grader discussion, so this is not a new untouched test of the revised evaluation procedure.','', '| Skill vs no skill | Split | Net advantage, pp [95% case CI] | Win / tie / loss judgments | Cases |','|---|---|---:|---:|---:|']
    for arm,s in arms.items():
        for split,g in s.items():
            m=g['all']['overall']
            if m:lines.append(f"| {arm} | {split} | {cell(m)} | {m['wins']} / {m['ties']} / {m['losses']} | {m['cases']} |")
    lines+=['','Main tables use the same complete cases for both versions, all ten generation configurations, and both judges. Incomplete cases are listed in coverage.json rather than scored as ties. The six-output development pilots are separate.','', '## Writing categories','', '| Skill | Split | Ordinary | Research | Argument | Proof | Control |','|---|---|---:|---:|---:|---:|---:|']
    for arm,s in arms.items():
        for split,g in s.items():lines.append('| '+ ' | '.join([arm,split]+[cell(g['all']['categories'][cat]) for cat in CATEGORIES])+' |')
    lines+=['','Category counts per split: '+json.dumps(coverage['category_counts'])+'.','','## Dimensions','','| Skill | Split | Meaning | Naturalness | Progression | Voice | Proof |','|---|---|---:|---:|---:|---:|---:|']
    for arm,s in arms.items():
        for split,g in s.items():lines.append('| '+' | '.join([arm,split]+[cell(g['all']['dimensions'][d]) for d in DIMENSIONS])+' |')
    lines+=['','## Judges and reliability','','| Skill | Split | Astra high | Sol high |','|---|---|---:|---:|']
    for arm,s in arms.items():
        for split,g in s.items():lines.append('| '+' | '.join([arm,split]+[cell(g['all']['judges'][j]) for j in run.JUDGES])+' |')
    for name,c in [('Cross-judge',checks['cross_judge']),('Reversed-order',checks['order'])]:lines+=['',f"{name}: {c['same']}/{c['pairs']} identical overall verdicts; {c['opposite']} direct win/loss disagreements, across {c['cases']} distinct cases. Counts include configurations and versions and are not independent tasks."]
    lines+=['','Both judges belong to the OpenAI model family. Agreement does not establish human preference alignment or remove shared-model bias. Batching can affect judgments; pairs are anonymous, same-task, and independently graded, but batch composition is not randomized across repetitions.','','## Matched historical comparison','','Astra high is common to the old and new runs. The following uses only matching v5a/no-skill responses and complete configurations. The rubric, supplied author context, prompt batching, and A/B ordering changed together; this cannot identify the causal effect of any one of those changes.','','| Split | Old Astra judgment | New Astra judgment | Changed / pairs |','|---|---:|---:|---:|']
    for split,m in matched.items():lines.append(f"| {split} | {cell(m['old'])} | {cell(m['new'])} | {m['changed']} / {m['pairs']} |")
    lines+=['','## Small development pilots','','| Candidate vs no skill | Net advantage, pp [95% case CI] | Win / tie / loss | Cases |','|---|---:|---:|---:|']
    for arm,p in pilots.items():
        m=p['overall']
        if m:lines.append(f"| {arm} | {cell(m)} | {m['wins']} / {m['ties']} / {m['losses']} | {m['cases']} |")
    lines+=['','These pilots have only six saved case/configuration outputs each and do not share the full matrix. They were developed after inspecting earlier results and cannot establish generalization. Packaged/installed v4 is unchanged.','','## Evidence and execution','',f"{usage['calls_started']} Codex judge attempts; {usage['calls_answered']} returned answers; {usage['invalid_attempts']} schema/evidence-invalid attempts; {usage['transport_errors']} transport errors. CLI-reported token total: {usage['reported_tokens']:,} from {usage['calls_with_reported_tokens']} attempts. Failed calls without token reports are not estimated as zero. No account-percentage or billing-total claim is made.",'','plan.json binds the source datasets, exact saved writing, rubric, context, judge identities, ordering and retry limit. Observation files retain full verdicts, exact evidence quotes, source/prompt/response/raw hashes and any uniquely source-verified math-delimiter repair. Validation reconstructs each blinded prompt and rechecks every verdict against the actual source. judge-responses.jsonl.gz contains the accepted raw text for independent revalidation; attempts.json accounts for unsuccessful attempts, whose raw answers remain local. Original grades and response files are retained unchanged.','','Reproduce without model calls: `MPLCONFIGDIR=/tmp/declaude-mpl .local/venv/bin/python tools/report_context_regrade.py --published --plot`. This verifies the portable public evidence and requires every frozen batch. Omit `--published` to read original local CLI artifacts. `--partial --out <folder>` writes an explicitly provisional local snapshot and never treats missing votes as ties.']
    (out/'report.md').write_text('\n'.join(lines)+'\n')
    return coverage,arms

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--partial',action='store_true');p.add_argument('--published',action='store_true');p.add_argument('--out',type=Path,default=run.PUBLIC);p.add_argument('--plot',action='store_true');a=p.parse_args()
    if a.partial and a.published:p.error('Published evidence must be complete')
    if a.partial and a.out.resolve()==run.PUBLIC.resolve():p.error('Partial snapshots require a separate --out')
    plan,cases,texts,records,raw,attempts,missing=read_published(run.PUBLIC) if a.published else read_records(a.partial)
    coverage,arms=render(plan,cases,records,attempts,missing,a.out,a.plot)
    payload=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in raw).encode()
    (a.out/'judge-responses.jsonl.gz').write_bytes(gzip.compress(payload,mtime=0))
    print(json.dumps({k:coverage[k] for k in ['status','batches_done','primary_judgments','audit_judgments','category_counts']},indent=2))
    for arm,s in arms.items():
        for split,g in s.items():print(arm,split,cell(g['all']['overall']))

if __name__=='__main__':main()
