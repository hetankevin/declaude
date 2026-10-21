#!/usr/bin/env python3
"""No-call report repair: collapse only identical duplicate JSON values."""
import json
from pathlib import Path
import v10_network as n
from v10_network import v,lh,pairwise,r
ORIGINAL=v.grades

def deduplicate(raw):
    changes=[]
    def hook(pairs):
        out={}
        for key,value in pairs:
            if key in out:
                if out[key]!=value:raise ValueError('Conflicting duplicate key; cannot repair')
                changes.append(dict(key=key,value=value,action='collapse identical duplicate'))
            out[key]=value
        return out
    value=json.loads(raw,object_pairs_hook=hook)
    return (json.dumps(value,ensure_ascii=False) if changes else raw),changes

def grades(job,raw,rubric,cases,texts,plan):
    try:normalized,fixes=deduplicate(raw)
    except json.JSONDecodeError:normalized,fixes=raw,[]
    rows,errors=ORIGINAL(job,normalized,rubric,cases,texts,plan)
    if fixes:
        for row in rows:
            row['raw_sha256']=pairwise.text_hash(raw)
            row['identical_duplicate_repairs']=fixes
    return rows,errors

def main():
    n.setup();p,c=n.load();texts=r.texts_for(p,c);rubric=(v.OUT/'rubric.txt').read_text();audit=[]
    for job in p['jobs']:
        if job['stage']!='judge':continue
        d=r.directory(job)
        if not (d/'answer.txt').exists():continue
        raw=(d/'answer.txt').read_text()
        try:normalized,fixes=deduplicate(raw)
        except json.JSONDecodeError:continue
        if not fixes:continue
        rows,errors=grades(job,raw,rubric,c,texts,p)
        if (d/'accepted.json').exists():lh.require(lh.read(d/'accepted.json')==rows,'Accepted evidence changed')
        else:lh.write(d/'accepted.json',rows)
        audit.append(dict(job=job['id'],raw_sha256=pairwise.text_hash(raw),normalized_sha256=pairwise.text_hash(normalized),repairs=fixes,remaining_validation_errors=errors))
    v.grades=grades;n.report()
    lh.write(v.OUT/'identical-duplicate-repairs.json',dict(new_model_calls=0,rule='Collapse duplicate keys only when their parsed values are identical. Reject conflicting duplicates. Preserve original raw evidence and every preference/reason.',repairs=audit,script_sha256=lh.hashed(Path(__file__))))
    report=v.OUT/'report.md';report.write_text(report.read_text()+'\nOne batch repeated the same empty source-quote key. A no-call reporting repair collapses identical values only, retaining the raw answer and all preferences/reasons. Two verdicts then pass validation. Its no-skill comparison still fails a required proof source quotation and remains ungraded, never a tie. Thus Sonnet vs none has n=6; its other comparisons have n=7. Sol has n=6 throughout. See identical-duplicate-repairs.json. Reproduce final artifacts with python3 tools/finalize_v10.py.\n')
if __name__=='__main__':main()
