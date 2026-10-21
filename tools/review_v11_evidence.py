#!/usr/bin/env python3
"""No-call evidence review; leaves the frozen v11 source artifacts unchanged."""
import json
from pathlib import Path
import v11_check as v
from v11_check import lh,pairwise,r
class Pairs(list):pass

def merge_quote_fields(raw):
    repairs=[]
    def convert(x,path=()):
        if isinstance(x,Pairs):
            d={}
            for k,item in x:
                value=convert(item,path+(k,))
                if k in d:
                    if d[k]==value:repairs.append(dict(path=list(path+(k,)),kind='identical duplicate',before=d[k],additional=value))
                    elif path and path[-1]=='quotes' and k in ('source','A','B') and isinstance(d[k],list) and isinstance(value,list) and all(isinstance(s,str) for s in d[k]+value):
                        repairs.append(dict(path=list(path+(k,)),kind='preserve both quotation lists',before=d[k].copy(),additional=value))
                        d[k]=list(dict.fromkeys(d[k]+value))
                    else:raise ValueError('Conflicting non-quotation values cannot be repaired')
                else:d[k]=value
            return d
        if isinstance(x,list):return [convert(a,path+(str(i),)) for i,a in enumerate(x)]
        return x
    data=convert(json.loads(raw,object_pairs_hook=Pairs))
    return json.dumps(data,ensure_ascii=False),repairs

def main():
    v.setup();p,c=v.load();texts=r.texts_for(p,c);rubric=(v.OUT/'rubric.txt').read_text();records=[];audit=[];answers=[]
    for j in p['jobs']:
        if j['stage']!='judge':continue
        raw=(r.directory(j)/'answer.txt').read_text();normal,fixes=merge_quote_fields(raw)
        rows,errors=v.grades(j,normal,rubric,c,texts,p)
        lh.require(not errors,'Every retained quotation must pass unchanged validation')
        for row in rows:
            row['raw_sha256']=pairwise.text_hash(raw)
            row['quotation_list_repairs']=[x for x in fixes if x['path'][0]==row['pair_id']]
        records+=rows;audit.append(dict(job=j['id'],raw_sha256=pairwise.text_hash(raw),normalized_sha256=pairwise.text_hash(normal),repairs=fixes))
        answers.append(dict(job=j['id'],answer=raw))
    for name,data in [('validated-observations.json',records),('reviewed-judge-responses.json',answers),('evidence-review.json',dict(new_model_calls=0,rule='Post-freeze reporting repair: preserve both duplicate quotation lists, then validate every quotation against the supplied text. No selection of one list over another. Conflicting reasons, preferences, severity or other non-quotation values rejected. Original artifacts unchanged.',batches=audit,script_sha256=lh.hashed(Path(__file__))))]:lh.public_safe(data);lh.write(v.OUT/name,data)
    print([(x['config'],x['reference'],x['outcome'],x['candidate_material_error']) for x in records])
if __name__=='__main__':main()
