#!/usr/bin/env python3
"""No-call final reporting with disclosed optional-source-quote validation repairs."""
import json
from pathlib import Path
import resume_restored_check as continuation
import finish_restored_check as finish
from restored_check import lh,pairwise,prior
r=continuation.r
INITIAL=finish.repair_initial_case

def repair_optional_source(verdict,source):
    value,changes=INITIAL(verdict,source)
    pool=source['task']+('\n\nUser context:\n'+source['user_context'] if source.get('user_context') else '')
    assertions=source.get('assertions',[])
    assertion_text='\n'.join(a if isinstance(a,str) else a.get('text','') for a in assertions)
    for name in ('naturalness','progression','voice','overall'):
        item=value['dimensions'][name];kept=[]
        for i,q in enumerate(item['quotes']['source']):
            if q in pool:kept.append(q);continue
            changes.append(dict(kind='optional_source_quote_removed',field='dimensions.'+name+'.quotes.source',index=i,before=q,after=None,reason='Exact quote from supplied assertions, outside original source/context quote pool.' if q in assertion_text else 'Nonverbatim optional source quote; retained only in raw evidence, not accepted as a quotation.'))
        item['quotes']['source']=kept
    return value,changes

def main():
    p,c,a=continuation.load();continuation.setup();r.report()
    u=lh.read(r.OUT/'usage.json');u.update(call_cap=101,continuation_calls=u['calls']-66,authorized_retries=1,continuation_plan_sha256=a['sha256']);lh.write(r.OUT/'usage.json',u)
    finish.repair_initial_case=repair_optional_source
    finish.finish()
    observations=lh.read(r.OUT/'observations.json');qualified=[]
    for obs in observations:
        changes=obs.get('initial_case_quote_repairs',[])
        if any(x.get('kind')=='optional_source_quote_removed' for x in changes):
            obs['optional_source_quote_qualified']=True;qualified.append(obs)
    cov=lh.read(r.OUT/'coverage.json');cov.update(initial_case_repaired=1,optional_source_quote_qualified=len(qualified))
    manifest=lh.read(r.OUT/'quote-format-repairs.json')
    manifest.update(rule='Original source-verified first-letter correction, plus removal of nonverbatim OPTIONAL source quotes only in naturalness/progression/voice/overall. Required response quotes and required source evidence in meaning, material-error and proof checks remain strict. No reason, preference or severity changes. Raw answers retained. Report sensitivity excluding qualified verdicts.',report_adapter_sha256=lh.hashed(Path(__file__)),continuation_plan_sha256=a['sha256'])
    sensitivity={}
    for ref in ('none','v4'):
        sensitivity[ref]={}
        for cfg in (*r.CONFIGS,'all'):
            rows=[x for x in observations if x['reference']==ref and (cfg=='all' or x['config']==cfg) and not x.get('optional_source_quote_qualified')]
            sensitivity[ref][cfg]=prior.net_stats(rows)
    for name,v in [('observations.json',observations),('coverage.json',cov),('quote-format-repairs.json',manifest),('quote-sensitivity.json',sensitivity)]:lh.public_safe(v);lh.write(r.OUT/name,v)
    path=r.OUT/'report.md';s=path.read_text()
    start=s.index('Validation:');end=s.index('\n\nUsage:',start)
    s=s[:start]+('Validation: 117 verdicts passed the original validator. One required source-verified initial-letter capitalization correction. Two verdicts had inadmissible optional source quotes in the voice dimension: one quoted a supplied assertion outside the validator\'s source/context pool, the other paraphrased an author preference as a quotation. Those optional quotes were removed from accepted evidence, with the raw answers, reasons, scores and severity flags unchanged. Required factual, proof and response quotations still pass the original validator. See quote-format-repairs.json and optional-quote-amendment.md. These two verdicts are flagged and excluded in quote-sensitivity.json. These are post-freeze reporting amendments, not additional model judgments. Reproduce with `python3 tools/finalize_restored_results.py`, then `python3 tools/plot_restored_check.py`.')+s[end:]
    s+='\n## Sensitivity to optional quote issues\n\nThese figures exclude the two qualified Sonnet proof judgments. The full table above retains their unchanged preferences.\n\n| Model | vs none (pp; judgments) | vs v4 (pp; judgments) |\n|---|---:|---:|\n'
    for cfg in (*r.CONFIGS,'all'):
        cells=[f'{sensitivity[ref][cfg]["net_pp"]:+.1f}; n={sensitivity[ref][cfg]["judgments"]}' for ref in ('none','v4')]
        s+='| '+cfg+' | '+' | '.join(cells)+' |\n'
    s+='\nExecution amendment: one user-authorized Astra capacity retry, 101 total attempts. All prior evidence was preserved. Budget accounting retains 30,000 tokens/8 credits as a reservation for the original failure\'s unknown usage, not as a measured debit. See continuation-plan.json.\n'
    path.write_text(s)
    print(json.dumps(dict(complete=cov['complete'],accepted=cov['accepted'],qualified=len(qualified),calls=u['calls'],new_calls=u['continuation_calls'],tokens=u['known_reported_tokens'],credits=u['codex_paid_credit_equivalent'])))
if __name__=='__main__':main()
