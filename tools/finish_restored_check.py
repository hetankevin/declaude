#!/usr/bin/env python3
"""Read-only grading completion: source-verified initial-letter quote repair; no model calls."""
import copy,json,re
from pathlib import Path
import restored_check as r
from restored_check import lh,pairwise,prior,context

def repair_initial_case(verdict,source):
    v=copy.deepcopy(verdict);changes=[]
    pools={'source':source['task']+('\n\nUser context:\n'+source['user_context'] if source.get('user_context') else ''),**source['responses']}
    items=[('material_errors.'+k,x) for k,x in v['material_errors'].items()]+[('dimensions.'+k,x) for k,x in v['dimensions'].items()]
    for where,item in items:
        for label,quotes in item['quotes'].items():
            for i,q in enumerate(quotes):
                if not isinstance(q,str) or not q or q in pools[label]:continue
                spans=[m.group() for m in re.finditer(re.escape(q),pools[label],flags=re.IGNORECASE) if m.group()[1:]==q[1:] and m.group()[0].lower()==q[0].lower()]
                if len(spans)==1:
                    quotes[i]=spans[0];changes.append(dict(field=where+'.quotes.'+label,index=i,before=q,after=spans[0]))
    return v,changes

def finish():
    plan,cases=r.load();rows=r.ledger(plan)
    lh.require(rows and len(rows)<=100 and all(x['finished'] for x in rows),'Wait for active calls to finish')
    texts=r.texts_for(plan,cases);rubric=(r.OUT/'rubric.txt').read_text();records=[];repairs=[];missing=[]
    for job in plan['jobs']:
        if job['stage']!='judge':continue
        d=r.directory(job)
        if not (d/'accepted.json').exists():continue
        raw=(d/'answer.txt').read_text()
        valid,errors=r.grades(job,raw,rubric,cases,texts,plan)
        lh.require(valid==lh.read(d/'accepted.json'),'Original validation changed')
        records+=valid;got={x['pair_id'] for x in valid}
        parsed,_=context.parse_batch(raw);prompt,supplied,pairs=prior.request(job,rubric,cases,texts)
        for e in job['pairs']:
            if e['label'] in got:continue
            source=dict(supplied,responses=pairs[e['label']]);before,existing=context.repair_evidence(parsed[e['label']],source)
            after,changes=repair_initial_case(before,source)
            if not changes:missing.append((job['id'],e['label']));continue
            try:pairwise.validate_verdict(after,source)
            except (ValueError,KeyError,TypeError):missing.append((job['id'],e['label']));continue
            # Removing quotations must make the before/after objects byte-equivalent.
            def without_quotes(v):
                v=copy.deepcopy(v)
                for group in ('material_errors','dimensions'):
                    for item in v[group].values():item.pop('quotes')
                return v
            lh.require(without_quotes(before)==without_quotes(after),'Attempt to change verdict or reasoning')
            amended=dict(parsed);amended[e['label']]=after
            repaired_raw=json.dumps(amended,ensure_ascii=False)
            accepted,_=r.grades(job,repaired_raw,rubric,cases,texts,plan)
            new=next(x for x in accepted if x['pair_id']==e['label'])
            new['validation_input_sha256']=new['raw_sha256'];new['raw_sha256']=pairwise.text_hash(raw)
            new['initial_case_quote_repairs']=changes
            new['evidence_format_repairs']=existing+new['evidence_format_repairs']
            records.append(new);repairs.append(dict(job=job['id'],pair=e['label'],changes=changes,original_raw_sha256=pairwise.text_hash(raw),validation_input_sha256=pairwise.text_hash(repaired_raw)))
    lh.require(not missing,'Unresolved invalid judgments: no format-completed report')
    expected={(cid,cfg,ref) for cid in cases for cfg in r.CONFIGS for ref in ('none','v4')}
    actual=[(x['case'],x['config'],x['reference']) for x in records]
    lh.require(len(actual)==len(set(actual)) and set(actual)<=expected,'Duplicate/unknown pairs')
    complete=set(actual)==expected
    summary={}
    for ref in (('none','v4') if complete else ()):
        summary[ref]={}
        for cfg in (*r.CONFIGS,'all'):
            rs=[x for x in records if x['reference']==ref and (cfg=='all' or x['config']==cfg)]
            summary[ref][cfg]=dict(overall=prior.net_stats(rs),nonproof=prior.net_stats([x for x in rs if cases[x['case']]['category']!='proof']),categories={cat:prior.net_stats([x for x in rs if cases[x['case']]['category']==cat]) for cat in prior.CATEGORIES},dimensions={dim:prior.net_stats(rs,dim) for dim in pairwise.DIMENSIONS},candidate_error_flags=sum(x['candidate_material_error'] for x in rs),reference_error_flags=sum(x['reference_material_error'] for x in rs))
    coverage=lh.read(r.OUT/'coverage.json');coverage.update(complete=complete,raw_validator_accepted=len(records)-len(repairs),accepted=len(records),format_repaired=len(repairs),missing_pairs=[list(k) for k in sorted(expected-set(actual))])
    if complete:coverage['missing_batches']=[]
    manifest=dict(rule='Only the first character of an evidence quote may change case, and only if exactly one matching span exists in the supplied source. All other characters, reasons, severity flags, and preferences remain unchanged. Other invalid evidence remains invalid.',repairs=repairs,new_model_calls=0,script_sha256=lh.hashed(Path(__file__)),plan_sha256=plan['plan_sha256'])
    for name,v in [('observations.json',records),('summary.json',summary),('coverage.json',coverage),('quote-format-repairs.json',manifest)]:lh.public_safe(v);lh.write(r.OUT/name,v)
    def fmt(s):return f'{s["net_pp"]:+.1f} pp [{s["net_ci95_pp"][0]:+.1f}, {s["net_ci95_pp"][1]:+.1f}]; {s["wins"]}W/{s["ties"]}T/{s["losses"]}L'
    usage=lh.read(r.OUT/'usage.json')
    lines=['# Restored v9: 20-case development check','','Complete: 60 candidate drafts and 120 primary pairwise verdicts, reusing 120 exact saved no-skill/v4 baselines. Four cases each of ordinary prose, research, argument, proof, and already-good controls. These are the previously inspected development validation subset, not fresh OOS evidence. Fully inlined bundles do not test selective reference loading or long-horizon retention.','','| Generator / effort | Restored v9 vs none | Restored v9 vs v4 |','|---|---|---|']
    for cfg in ((*r.CONFIGS,'all') if complete else ()):lines.append('| '+cfg+' | '+fmt(summary['none'][cfg]['overall'])+' | '+fmt(summary['v4'][cfg]['overall'])+' |')
    lines+=['','Win rate minus loss rate, in percentage points; ties contribute zero. Intervals bootstrap cases, not individual model votes. One frozen Sol-high author-specific blind judge, balanced anonymous A/B placement, no extra order audits. Historical baselines retain a possible backend/time confound.','', '| Category | Model | vs none (pp) | vs v4 (pp) |','|---|---|---:|---:|']
    for cat in (prior.CATEGORIES if complete else ()):
        for cfg in r.CONFIGS:lines.append(f'| {cat} | {cfg} | {summary["none"][cfg]["categories"][cat]["net_pp"]:+.1f} | {summary["v4"][cfg]["categories"][cat]["net_pp"]:+.1f} |')
    lines+=['',f'Validation: {len(records)-len(repairs)} verdicts passed the original validator. {len(repairs)} passed after the documented source-verified initial-letter capitalization repair. Raw answers remain unchanged; no preference, reason, or severity was altered. See quote-format-repairs.json. This is a disclosed post-freeze formatting amendment, not an additional model judgment. Reproduce: first run `python3 tools/restored_check.py report`, then `python3 tools/finish_restored_check.py`, then the plot script.', '',f'Usage: {usage["calls"]}/100 calls ({usage["writing_calls"]} writing, {usage["judge_calls"]} grading), {usage["known_reported_tokens"]:,} reported tokens, {usage["unknown_attempts"]} unknown attempts. Codex paid-credit equivalent at Standard rates: {usage["codex_paid_credit_equivalent"]:.2f}, plus Claude usage from {usage["claude_calls"]}/20 calls. Hard call cap100; scheduling guards2.5M tokens/300 Codex credits. These are not measured account debits or subscription percentages. No retries or additional calls for formatting repair.','', 'Fresh holdouts remain sealed and unrun. No skill installation or automatic promotion. Case-level judgments, evidence, hashes and error flags are available in the accompanying JSON artifacts.']
    if not complete:
        fully=[cid for cid in cases if all((cid,cfg,ref) in set(actual) for cfg in r.CONFIGS for ref in ('none','v4'))]
        end=lines[-3:]
        lines=['# Restored v9: incomplete development check','',f'Stopped after {usage["calls"]}/100 calls: Astra reported model capacity and returned no usage. The frozen unknown-usage guard stopped scheduling. {coverage["outputs"]}/60 drafts and {len(records)}/120 verdicts are validated, covering {len(fully)}/20 complete cases. No retries or model substitutions.','', 'No aggregate headline or new heatmap is published from this incomplete, uneven category sample. Existing skill results remain historical. The unrun cases are missing, never ties.','',f'{len(records)-len(repairs)} verdicts passed the original validator; {len(repairs)} needed source-verified first-letter quote capitalization repair, with raw answers and outcomes unchanged. See quote-format-repairs.json and formatting-amendment.md. No extra model call was used.','', '| Case | Model | Reference | Outcome |','|---|---|---|---|']
        for x in sorted(records,key=lambda x:(x['case'],x['config'],x['reference'])):lines.append(f'| {x["case"]} | {x["config"]} | {x["reference"]} | {x["outcome"]} |')
        lines+=['']+end
    (r.OUT/'report.md').write_text('\n'.join(lines)+'\n');print(json.dumps(dict(complete=complete,accepted=len(records),format_repairs=len(repairs),new_calls=0)))

if __name__=='__main__':finish()
