#!/usr/bin/env python3
"""Validate and freeze the larger development and sealed holdout sets."""
import argparse,collections,hashlib,json
from pathlib import Path

CATEGORIES={'ordinary','research','argument','proof','control'}
GROUPS={'fidelity','style','argument','proof'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(paths):
 cases=[]
 for path in paths:
  chunk=json.loads(path.read_text())['cases']
  assert len(chunk)==20,(path.name,'expected20')
  assert collections.Counter(c['category'] for c in chunk)=={k:4 for k in CATEGORIES}
  for c in chunk:
   assert len(c['task'].split())>=150,(c['id'],'short task')
   assert 5<=len(c['assertions'])<=8,c['id']
   assert all(a['group'] in GROUPS and isinstance(a['text'],str) and a['text'].strip() for a in c['assertions'])
   assert sum(a['group']=='fidelity' for a in c['assertions'])>=2
   assert c['difficulty'] in ['hard','ordinary']
   assert isinstance(c['quality_dimensions'],list)
  cases+=chunk
 assert len({c['id'] for c in cases})==len(cases)
 assert len({c['task'] for c in cases})==len(cases)
 return cases

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--authors',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 dev=validate([a.authors/'dev-a.json',a.authors/'dev-b.json'])
 test=validate([a.authors/'test-a.json',a.authors/'test-b.json'])
 assert not {c['task'] for c in dev}&{c['task'] for c in test}
 # Equal category and author allocation; no baseline score is consulted.
 for tag in ['dev-a','dev-b']:
  for cat in sorted(CATEGORIES):
   cs=sorted([c for c in dev if tag in c['id'] and c['category']==cat],key=lambda c:c['id'])
   for i,c in enumerate(cs):c['subset']='tune' if i%2==0 else 'validation'
 for c in test:c['subset']='fresh'
 for c in dev+test:c.pop('author_notes',None)
 a.out.mkdir(parents=True,exist_ok=True)
 sealed=a.authors/'sealed-holdout.json'
 devpath=a.out/'development.json'
 for path,cs in [(devpath,dev),(sealed,test)]:path.write_text(json.dumps({'cases':cs},indent=2)+'\n')
 manifest={'development_sha256':digest(devpath),'holdout_sha256':digest(sealed),'total_cases':80,'split_counts':{},'author_file_sha256':{p.name:digest(p) for p in a.authors.glob('*.json') if p.name in ['dev-a.json','dev-b.json','test-a.json','test-b.json']},'holdout_opened_for_selection':False}
 for name,cs in [('development',dev),('holdout',test)]:
  lengths=sorted(len(c['task'].split()) for c in cs)
  manifest['split_counts'][name]={'cases':len(cs),'categories':dict(collections.Counter(c['category'] for c in cs)),'task_words_min':min(lengths),'task_words_max':max(lengths),'task_words_median':(lengths[19]+lengths[20])/2,'assertions':sum(len(c['assertions']) for c in cs)}
 (a.out/'dataset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(manifest['split_counts'],indent=2))
if __name__=='__main__':main()
