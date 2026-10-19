#!/usr/bin/env python3
"""Publish anonymized observations, paired summaries, and optional heatmaps."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import statistics as st


def derive_case_metadata(rows, cases):
    """Frozen cases own split/subset. Missing imported fields are filled in."""
    for row in rows:
        case = cases[row['case']]
        for key in ('split', 'subset'):
            expected = case.get(key)
            if key in row and row[key] != expected:
                raise ValueError(f"{row['case']}: imported {key} disagrees with cases")
            row[key] = expected
    return rows


def expected_pools(case, responses, grader_hash):
    """Pure reconstruction of bench.grade_one; response keys are relative paths.

    Keep byte hashes, sorted initial paths, both deterministic shuffles, and the
    largest arm count's pool size exactly aligned with the generation runner.
    """
    rubric_hash = hashlib.sha256(json.dumps(case, sort_keys=True).encode()).hexdigest()
    grouped = {}
    for path in sorted(responses):
        grouped.setdefault(Path(path).parts[-3], []).append(path)
    if not grouped:
        raise ValueError('No responses for ' + case['id'])
    configs = sorted(grouped)
    random.Random('declaude-expanded-configs-' + case['id']).shuffle(configs)
    per_pool = max(1, 10 // max(len(v) for v in grouped.values()))
    expected = {}
    for offset in range(0, len(configs), per_pool):
        pool_id = offset // per_pool + 1
        pool = [p for cfg in configs[offset:offset+per_pool] for p in grouped[cfg]]
        random.Random(f"declaude-expanded-{case['id']}-{pool_id}").shuffle(pool)
        fingerprint = hashlib.sha256(json.dumps(dict(rubric=rubric_hash, grader=grader_hash,
            responses=[(p, hashlib.sha256(responses[p]).hexdigest()) for p in pool]), sort_keys=True).encode()).hexdigest()
        for i, path in enumerate(pool):
            expected[path] = dict(pool_sha256=fingerprint, rubric_sha256=rubric_hash,
                                 pool_id=pool_id, pool_size=len(pool), blind_label=f'R{i+1:02}')
    return expected


def verify_pools(rows, cases, root=None):
    """Verify each source separately, before combining run roots or filtering arms.

    An observation export must include the entire grading input for each case.
    Disk roots include ungraded responses too, as bench.grade_one does. Exported
    grading_source IDs preserve separately graded roots without revealing paths.
    """
    by_case = {}
    for row in rows:
        by_case.setdefault((row['case'], row.get('grading_source')), []).append(row)
    for (case_id, _source), items in by_case.items():
        versions = {r['grader']['version'] for r in items}
        if len(versions) != 1:
            raise ValueError('Mixed grader versions for ' + case_id)
        version = versions.pop()
        if not isinstance(version, str) or version in ('', '.', '..') or '/' in version or '\\' in version:
            raise ValueError('Invalid grader version')
        grader_hash = hashlib.sha256((Path(__file__).resolve().parents[1]/'evals/graders'/f'{version}.txt').read_bytes()).hexdigest()
        if root is None:
            responses = {f"{r['case']}/{r['config']}/{r['arm']}/response.md": r['response'].encode('utf-8') for r in items}
            if len(responses) != len(items):
                raise ValueError('Duplicate observations')
        else:
            responses = {str(p.relative_to(root)): p.read_bytes() for p in sorted((root/case_id).glob('*/*/response.md'))}
        expected = expected_pools(cases[case_id], responses, grader_hash)
        for row in items:
            path = f"{row['case']}/{row['config']}/{row['arm']}/response.md"
            want = expected[path]
            if row['response'].encode('utf-8') != responses[path]:
                raise ValueError('Response changed during report read: ' + path)
            for key in ('pool_sha256', 'rubric_sha256'):
                if row.get(key) != want[key]:
                    raise ValueError(f'{key} mismatch: {path}; supply the full original grading pool')
            for key in ('pool_id', 'pool_size', 'blind_label'):
                if row['grader'].get(key) != want[key]:
                    raise ValueError(f'Grader {key} mismatch: {path}')
            row['words'] = len(row['response'].split())


def load_rows(paths, observations, cases, selection=False):
    rows = []
    if observations:
        imported = derive_case_metadata(json.loads(observations.read_text()), cases)
        verify_pools(imported, cases)
        rows.extend(imported)
    used_sources = {r.get('grading_source') for r in rows}
    for root in paths:
        source_id = f'run-{len(used_sources)}'
        while source_id in used_sources:
            source_id += '-next'
        used_sources.add(source_id)
        source = []
        for p in sorted(root.glob('*/*/*/grading.json')):
            case, cfg, arm = p.parts[-4:-1]
            g = json.loads(p.read_text())
            response = p.with_name('response.md').read_bytes().decode('utf-8')
            row = dict(case=case, config=cfg, arm=arm, grading_source=source_id, score=g['score'], assertions=g['assertions'],
                       note=g['note'], grader=g['grader'], pool_sha256=g.get('pool_sha256'),
                       rubric_sha256=g.get('rubric_sha256'), response=response, words=len(response.split()))
            if not selection:
                meta = json.loads(p.with_name('meta.json').read_text())
                row.update({k: meta[k] for k in ('model', 'effort', 'task_sha256', 'skill_sha256')})
            source.append(row)
        derive_case_metadata(source, cases)
        verify_pools(source, cases, root)
        rows.extend(source)
    keys = [(r['case'], r['config'], r['arm']) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate observations; do not select a preferred repeat')
    return rows


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


def main(argv=None):
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
    a=ap.parse_args(argv)
    case_rows=[c for p in a.cases for c in json.loads(p.read_text())['cases']]
    cases={c['id']:c for c in case_rows}
    if len(cases)!=len(case_rows):raise ValueError('Duplicate case IDs')
    rows=load_rows(a.runs,a.observations,cases)
    selection_rows=load_rows(a.selection_runs,a.selection_observations,cases,selection=True)
    reference=a.reference
    final=[r for r in rows if r['arm'] in [reference,a.selected]]
    # A complete paired matrix is required before an overall benchmark is reported.
    configs=sorted({r['config'] for r in final})
    if a.matrix:
        matrix=json.loads(a.matrix.read_text())
        assert set(configs)==set(matrix['configs']),'Configurations do not match the preregistered matrix'
        assert len(rows)==matrix['total_outputs'],'Output count does not match the matrix'
        for path in a.cases:
            digest=matrix.get('dataset_sha256',{}).get(path.stem)
            if digest:assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,'Dataset hash mismatch'
        if matrix.get('grader_sha256'):
            grader_path=Path(__file__).resolve().parents[1]/'evals/graders'/f"{matrix['grader']}.txt"
            assert hashlib.sha256(grader_path.read_bytes()).hexdigest()==matrix['grader_sha256'],'Grader prompt hash mismatch'
        for row in rows:
            expected=matrix['configs'][row['config']]
            assert (row['model'],row['effort'])==(expected['model'],expected['effort']),'Model/effort metadata mismatch'
            assert row['task_sha256']==hashlib.sha256(cases[row['case']]['task'].encode()).hexdigest(),'Task hash mismatch'
            hashes=matrix.get('skill_sha256_by_arm',{'none':None,'v3':matrix.get('skill_sha256')})
            assert row['skill_sha256']==hashes[row['arm']],'Skill hash mismatch'
            assert row['rubric_sha256']==hashlib.sha256(json.dumps(cases[row['case']],sort_keys=True).encode()).hexdigest(),'Rubric hash mismatch'
            expected_assertions=cases[row['case']]['assertions']
            assert [(v['group'],v['text']) for v in row['assertions']]==[(v['group'],v['text']) for v in expected_assertions],'Grader changed assertion definitions'
            if matrix.get('grader'):assert row['grader'].get('version')==matrix['grader'],'Grader version mismatch'
    assert set(r['case'] for r in final)==set(cases),'Cases are missing'
    assert set((r['case'],r['config'],r['arm']) for r in final)=={(c,cfg,arm) for c in cases for cfg in configs for arm in [reference,a.selected]},'Incomplete paired matrix'
    parts=['# Evaluation results','',f'Selected skill: {a.selected}. One run per case, configuration, and condition. Binary pass rates are assertion-weighted (each applicable assertion has equal weight). Intervals resample paired cases, not individual assertions.','']
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
        parts += ['', f'| Configuration | {reference} assertion-weighted rate / holistic | {a.selected} assertion-weighted rate / holistic |','|---|---:|---:|']
        for cfg in configs:
            br=[r for r in rs if r['config']==cfg and r['arm']==reference];sr=[r for r in rs if r['config']==cfg and r['arm']==a.selected]
            parts.append(f'| {cfg} | {fmt("all",value(br,"all"))} / {value(br,"holistic"):.2f} | {fmt("all",value(sr,"all"))} / {value(sr,"holistic"):.2f} |')
        parts.append('')
    if selection_rows:
        parts += ['## Initial development A/B selection','', 'The initial and revised skill versions were compared on Sonnet low and Astra medium only. These cases were available for selection and are not held out.','', '| Subset | Version | Assertion-weighted rate | Holistic |','|---|---|---:|---:|']
        for subset in ['tune','validation']:
            for arm in ['none','v1','v2','v3']:
                rs=[r for r in selection_rows if r['subset']==subset and r['arm']==arm and r['config'] in ['sonnet-low','astra-medium']]
                if rs:parts.append(f'| {subset} | {arm} | {fmt("all",value(rs,"all"))} | {value(rs,"holistic"):.2f} |')
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'observations.json').write_text(json.dumps(rows,indent=2)+'\n')
    (a.out/'selection-observations.json').write_text(json.dumps(selection_rows,indent=2)+'\n')
    (a.out/'report.md').write_text('\n'.join(parts).rstrip()+'\n')
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
