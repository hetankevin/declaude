#!/usr/bin/env python3
"""Publish anonymized observations, paired summaries, and optional heatmaps."""
import argparse
import json
from pathlib import Path
import random
import statistics as st


def value(rows, metric):
    if metric=='holistic': return st.mean(r['score'] for r in rows)
    if metric=='words': return st.median(r['words'] for r in rows)
    items=[a['passed'] for r in rows for a in r['assertions'] if metric=='all' or a['group']==metric]
    return st.mean(items) if items else None


def difference(rows, arm, reference, metric, samples=3000):
    by={}
    for row in rows: by.setdefault(row['case'],{}).setdefault(row['config'],{})[row['arm']]=row
    cases=[c for c in by if any(arm in v and reference in v for v in by[c].values())]
    def paired(cs):
        pairs=[v for c in cs for v in by[c].values() if arm in v and reference in v]
        a=value([v[arm] for v in pairs],metric);b=value([v[reference] for v in pairs],metric)
        return None if a is None or b is None else a-b
    rng=random.Random(20261019)
    ds=[paired(rng.choices(cases,k=len(cases))) for _ in range(samples)]
    ds=sorted(d for d in ds if d is not None)
    return [paired(cases),ds[int(.025*len(ds))],ds[int(.975*len(ds))-1]] if ds else None


def fmt(metric,x):
    if x is None:return '—'
    return f'{x:.2f}' if metric=='holistic' else (f'{x:.0f}' if metric=='words' else f'{100*x:.1f}%')


def grouped(rows, selected, reference='none'):
    from plot_matrix import ORDER, METRICS
    result={}
    for split in sorted({r['split'] for r in rows}):
        result[split]={}
        for cfg in ORDER:
            def matches(r):
                if cfg=='all':return True
                if cfg=='claude-all':return r['model'].startswith('claude-')
                if cfg=='codex-all':return r['model'].startswith('gpt-')
                return r['config']==cfg
            rs=[r for r in rows if r['split']==split and matches(r)]
            result[split][cfg]={}
            for metric,_ in METRICS:
                br=[r for r in rs if r['arm']==reference];sr=[r for r in rs if r['arm']==selected]
                counts={arm:sum(metric=='all' or a['group']==metric for r in rs if r['arm']==arm for a in r['assertions']) for arm in [reference,selected]} if metric not in ['holistic','words'] else {arm:len([r for r in rs if r['arm']==arm]) for arm in [reference,selected]}
                case_count=len({r['case'] for r in rs if metric in ['words','holistic','all'] or any(a['group']==metric for a in r['assertions'])})
                result[split][cfg][metric]={reference:value(br,metric),selected:value(sr,metric),'difference_ci':difference(rs,selected,reference,metric) if metric!='words' else None,'counts':counts,'case_count':case_count}
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--runs',nargs='*',type=Path,default=[])
    ap.add_argument('--cases',nargs='+',type=Path,required=True)
    ap.add_argument('--observations',type=Path)
    ap.add_argument('--selection-runs',nargs='*',type=Path,default=[])
    ap.add_argument('--selection-observations',type=Path)
    ap.add_argument('--selected',default='v3')
    ap.add_argument('--reference',default='none')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--plot',action='store_true')
    ap.add_argument('--matrix',type=Path,help='Require the preregistered configuration and output counts')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    cases={c['id']:c for p in a.cases for c in json.loads(p.read_text())['cases']}
    rows=json.loads(a.observations.read_text()) if a.observations else []
    for root in a.runs:
        for p in sorted(root.glob('*/*/*/grading.json')):
            case,cfg,arm=p.parts[-4:-1];g=json.loads(p.read_text());meta=json.loads(p.with_name('meta.json').read_text());response=p.with_name('response.md').read_text()
            rows.append(dict(case=case,split=cases[case]['split'],subset=cases[case].get('subset'),config=cfg,arm=arm,score=g['score'],assertions=g['assertions'],note=g['note'],grader=g['grader'],pool_sha256=g.get('pool_sha256'),rubric_sha256=g.get('rubric_sha256'),response=response,words=len(response.split()),model=meta['model'],effort=meta['effort'],task_sha256=meta['task_sha256'],skill_sha256=meta['skill_sha256']))
    keys=[(r['case'],r['config'],r['arm']) for r in rows]
    assert len(set(keys))==len(keys),'Duplicate observations; do not select a preferred repeat'
    (a.out/'observations.json').write_text(json.dumps(rows,indent=2)+'\n')
    selection_rows=json.loads(a.selection_observations.read_text()) if a.selection_observations else []
    for root in a.selection_runs:
        for p in sorted(root.glob('*/*/*/grading.json')):
            case,cfg,arm=p.parts[-4:-1];g=json.loads(p.read_text())
            selection_rows.append(dict(case=case,subset=cases[case].get('subset'),config=cfg,arm=arm,score=g['score'],assertions=g['assertions'],note=g['note'],grader=g['grader'],response=p.with_name('response.md').read_text()))
    (a.out/'selection-observations.json').write_text(json.dumps(selection_rows,indent=2)+'\n')
    reference=a.reference
    final=[r for r in rows if r['arm'] in [reference,a.selected]]
    # A complete paired matrix is required before an overall benchmark is reported.
    configs=sorted({r['config'] for r in final})
    if a.matrix:
        matrix=json.loads(a.matrix.read_text())
        assert set(configs)==set(matrix['configs']),'Configurations do not match the preregistered matrix'
        assert len(rows)==matrix['total_outputs'],'Output count does not match the matrix'
    assert set(r['case'] for r in final)==set(cases),'Cases are missing'
    assert set((r['case'],r['config'],r['arm']) for r in final)=={(c,cfg,arm) for c in cases for cfg in configs for arm in [reference,a.selected]},'Incomplete paired matrix'
    parts=['# Evaluation results','',f'Selected skill: {a.selected}. One run per case, configuration, and condition. Intervals resample paired cases, not individual assertions.','']
    summary={}
    for split in sorted({r['split'] for r in final}):
        rs=[r for r in final if r['split']==split]
        parts += [f'## {split}','', f'| Metric | {reference} | {a.selected} | Difference [95% interval] |','|---|---:|---:|---:|']
        summary[split]={}
        for m in ['all','fidelity','style','argument','proof','holistic','words']:
            b=value([r for r in rs if r['arm']==reference],m);s=value([r for r in rs if r['arm']==a.selected],m)
            d=difference(rs,a.selected,reference,m) if m!='words' else None
            scale=1 if m=='holistic' else 100
            ds='—' if d is None else f'{scale*d[0]:+.2f} [{scale*d[1]:+.2f}, {scale*d[2]:+.2f}]'+('' if m=='holistic' else ' pp')
            parts.append(f'| {m} | {fmt(m,b)} | {fmt(m,s)} | {ds} |')
            summary[split][m]={reference:b,a.selected:s,'difference_ci':d}
        parts += ['', f'| Configuration | {reference} assertions / holistic | {a.selected} assertions / holistic |','|---|---:|---:|']
        for cfg in configs:
            br=[r for r in rs if r['config']==cfg and r['arm']==reference];sr=[r for r in rs if r['config']==cfg and r['arm']==a.selected]
            parts.append(f'| {cfg} | {fmt("all",value(br,"all"))} / {value(br,"holistic"):.2f} | {fmt("all",value(sr,"all"))} / {value(sr,"holistic"):.2f} |')
        parts.append('')
    parts += ['## Development A/B selection','', 'The initial and revised skill versions were compared on Sonnet low and Astra medium only. These cases were available for selection and are not held out.','', '| Subset | Version | Assertions | Holistic |','|---|---|---:|---:|']
    for subset in ['tune','validation']:
        for arm in ['none','v1','v2','v3']:
            rs=[r for r in selection_rows if r['subset']==subset and r['arm']==arm and r['config'] in ['sonnet-low','astra-medium']]
            if rs:parts.append(f'| {subset} | {arm} | {fmt("all",value(rs,"all"))} | {value(rs,"holistic"):.2f} |')
    (a.out/'report.md').write_text('\n'.join(parts)+'\n')
    (a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    if len(configs)==10:
        groups=grouped(final,a.selected,reference)
        (a.out/'groups_by_config.json').write_text(json.dumps(groups,indent=2)+'\n')
        if a.plot:
            from plot_matrix import plot_matrix
            plot_matrix(groups,a.selected,a.out,reference)
    elif a.plot:
        raise ValueError('Expanded plotting requires the ten-configuration matrix')
    print('\n'.join(parts))


if __name__=='__main__':main()
