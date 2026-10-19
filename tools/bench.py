#!/usr/bin/env python3
"""Paired isolated writing evaluations and blinded rubric grading."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = {
    'haiku': ('claude', 'claude-haiku-5-5', None),
    'opus-low': ('claude', 'claude-opus-5-5', 'low'),
    'opus-xhigh': ('claude', 'claude-opus-5-5', 'xhigh'),
    'fable': ('claude', 'claude-fable-5-1', None),
    'astra-high': ('codex', 'gpt-6-astra', 'high'),
    'sol-low': ('codex', 'gpt-6.1-sol', 'low'),
    'luna-medium': ('codex', 'gpt-6-luna', 'medium'),
    'grader-opus': ('claude', 'claude-opus-5-5', 'high'),
    'sonnet-low': ('claude', 'claude-sonnet-5-5', 'low'),
    'sonnet-high': ('claude', 'claude-sonnet-5-5', 'high'),
    'astra-medium': ('codex', 'gpt-6-astra', 'medium'),
}


def bundle(path):
    files = [path / 'SKILL.md'] + sorted((path / 'references').glob('*.md'))
    files = [p for p in files if not p.name.endswith('.local.md')]
    return '\n\n'.join(f'FILE {p.relative_to(path)}\n{p.read_text()}' for p in files)


def json_result(text):
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*|\s*```$', '', text)
    return json.loads(text)


def call(prompt, config, timeout=1500):
    provider, model, effort = CONFIGS[config]
    started = time.time()
    with tempfile.TemporaryDirectory(prefix='declaude-eval-') as wd:
        if provider == 'claude':
            cmd = ['claude', '-p', '--safe-mode', '--tools', '', '--model', model,
                   '--no-session-persistence', '--output-format', 'json']
            if effort is not None:
                cmd += ['--effort', effort]
            p = subprocess.run(cmd, input=prompt, text=True, capture_output=True, cwd=wd, timeout=timeout)
            data = json.loads(p.stdout) if p.stdout.strip().startswith('{') else {}
            text = data.get('result', '')
            usage = data.get('usage', {})
            error = bool(data.get('is_error'))
        else:
            home = Path(wd) / 'home'
            codex_home = home / '.codex'
            codex_home.mkdir(parents=True)
            real_auth = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'auth.json'
            (codex_home / 'auth.json').symlink_to(real_auth)
            output = Path(wd) / 'last.md'
            binary = os.environ.get('CODEX_BIN') or shutil.which('codex')
            if not binary:
                raise RuntimeError('codex is not installed')
            cmd = [binary, 'exec', '--skip-git-repo-check', '--ephemeral', '-s', 'read-only',
                   '-m', model, '-c', f'model_reasoning_effort="{effort}"',
                   '-c', 'features.hooks=false', '-C', wd, '-o', str(output), '-']
            p = subprocess.run(cmd, input=prompt, text=True, capture_output=True, cwd=wd,
                               env=dict(os.environ, HOME=str(home), CODEX_HOME=str(codex_home)), timeout=timeout)
            text = output.read_text() if output.exists() else ''
            match = re.search(r'tokens used\s*\n\s*([\d,]+)', p.stderr + p.stdout)
            usage = {'reported_tokens': int(match[1].replace(',', ''))} if match else {}
            error = False
        if p.returncode or error or not text.strip():
            raise RuntimeError(f'{config} execution failed ({p.returncode}): {p.stderr[-300:]} {text[-300:]}')
        return text, {'model': model, 'effort': effort, 'seconds': round(time.time()-started, 2), 'usage': usage}


def run_one(case, config, arm, skill, out):
    dest = out / case['id'] / config / arm
    task_hash = hashlib.sha256(case['task'].encode()).hexdigest()
    skill_hash = hashlib.sha256(skill.encode()).hexdigest() if arm != 'none' else None
    if (dest / 'response.md').exists():
        meta = json.loads((dest / 'meta.json').read_text())
        if meta.get('task_sha256') != task_hash or meta.get('skill_sha256') != skill_hash or (meta.get('model'),meta.get('effort')) != CONFIGS[config][1:]:
            raise RuntimeError('Cached artifact has different task or skill; use a fresh output directory')
        return f'cached {case["id"]}/{config}/{arm}'
    prompt = 'Complete the following writing task. Return the requested artifact, not a plan. All needed source text is supplied; do not use tools.\n\n'
    if arm != 'none':
        prompt += '<editing-guidance>\n' + skill + '\n</editing-guidance>\n\n'
    prompt += '<task>\n' + case['task'] + '\n</task>'
    text, meta = call(prompt, config)
    meta.update(task_sha256=task_hash, skill_sha256=skill_hash, case=case['id'], config=config, arm=arm)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'meta.json').write_text(json.dumps(meta, indent=2)+'\n')
    (dest / 'response.md').write_text(text+'\n')
    return f'done {case["id"]}/{config}/{arm}'


def grade_one(case, out, grader_version="v2"):
    grader_hash = hashlib.sha256((ROOT/"evals/graders"/f"{grader_version}.txt").read_bytes()).hexdigest()
    paths = sorted((out / case['id']).glob('*/*/response.md'))
    if not paths:
        raise RuntimeError('No responses for '+case['id'])
    rubric_hash = hashlib.sha256(json.dumps(case, sort_keys=True).encode()).hexdigest()
    grouped = {}
    for path in paths:
        grouped.setdefault(path.parts[-3], []).append(path)
    configs = sorted(grouped)
    random.Random('declaude-expanded-configs-'+case['id']).shuffle(configs)
    per_pool = max(1, 10 // max(len(v) for v in grouped.values()))
    for offset in range(0, len(configs), per_pool):
        pool_id = offset // per_pool + 1
        pool = [p for cfg in configs[offset:offset+per_pool] for p in grouped[cfg]]
        random.Random(f'declaude-expanded-{case["id"]}-{pool_id}').shuffle(pool)
        fingerprint = hashlib.sha256(json.dumps(dict(rubric=rubric_hash, grader=grader_hash,
            responses=[(str(p.relative_to(out)), hashlib.sha256(p.read_bytes()).hexdigest()) for p in pool]), sort_keys=True).encode()).hexdigest()
        if all(p.with_name('grading.json').exists() and json.loads(p.with_name('grading.json').read_text()).get('pool_sha256') == fingerprint for p in pool):
            continue
        grade_pool(case, pool, pool_id, fingerprint, rubric_hash, grader_version)
    return 'graded '+case['id']


def grade_pool(case, paths, pool_id, fingerprint, rubric_hash, grader_version="v2"):
    labels = [f'R{i+1:02}' for i in range(len(paths))]
    responses = '\n\n'.join(f'<response id="{label}">\n{p.read_text()}\n</response>' for label,p in zip(labels,paths))
    prompt = (ROOT/'evals/graders'/f'{grader_version}.txt').read_text() + case['task'] + '\nASSERTIONS:\n' + json.dumps(case['assertions']) + '\nRESPONSES:\n' + responses
    text, meta = call(prompt, 'grader-opus')
    data = json_result(text)
    if set(data) != set(labels):
        raise ValueError('Missing or additional grade labels')
    # Validate the entire pool before saving any grade.
    for grade in data.values():
        assert type(grade['score']) is int and 1 <= grade['score'] <= 5
        assert len(grade['assertions']) == len(case['assertions'])
        assert all(type(a['passed']) is bool and isinstance(a['evidence'],str) for a in grade['assertions'])
    for label,path in zip(labels,paths):
        grade = data[label]
        grade['assertions'] = [dict(a, **b) for a,b in zip(case['assertions'],grade['assertions'])]
        grade['grader'] = {'model':meta['model'], 'effort':meta['effort'], 'blind_label':label, 'pool_id':pool_id, 'pool_size':len(paths), 'version':grader_version}
        grade['rubric_sha256'] = rubric_hash
        grade['pool_sha256'] = fingerprint
        path.with_name('grading.json').write_text(json.dumps(grade,indent=2)+'\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('action', choices=['run','grade'])
    ap.add_argument('--cases', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--skill', type=Path, default=ROOT/'skill')
    ap.add_argument('--skills', help='Version-specific bundles, for example v3=evals/versions/v3,v4=skill')
    ap.add_argument('--configs', default='haiku,sonnet-low,sonnet-high,opus-low,opus-xhigh,fable,astra-medium,astra-high,sol-low,luna-medium')
    ap.add_argument('--arms', default='none,v4')
    ap.add_argument('--subset', default='all')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--grader-version', choices=['v1','v2'], default='v2')
    args=ap.parse_args()
    cases=json.loads(args.cases.read_text())['cases']
    if args.subset != 'all':
        cases=[c for c in cases if c.get('subset',c.get('split'))==args.subset]
    assert cases
    if args.action=='run':
        arms=args.arms.split(',')
        if args.skills:
            paths=dict(item.split('=',1) for item in args.skills.split(','))
            if set(arms)-{'none'} != set(paths):raise ValueError('--skills must name exactly the non-baseline arms')
            bundles={arm:bundle(Path(path)) for arm,path in paths.items()}
        else:
            if len(set(arms)-{'none'})>1:raise ValueError('Multiple skill versions require --skills; do not relabel the same bundle')
            bundles={arm:bundle(args.skill) for arm in arms if arm!='none'}
        bundles['none']=''
        jobs=[(c,cfg,arm,bundles[arm],args.out) for c in cases for cfg in args.configs.split(',') for arm in arms]
        fn=run_one
    else:
        jobs=[(c,args.out,args.grader_version) for c in cases];fn=grade_one
    failures=[]
    with ThreadPoolExecutor(args.workers) as pool:
        futures=[pool.submit(fn,*j) for j in jobs]
        for future in as_completed(futures):
            try: print(future.result(),flush=True)
            except Exception as exc:
                failures.append(str(exc));print('FAILED '+str(exc),flush=True)
    if failures:
        raise SystemExit(f'{len(failures)} jobs failed; no complete comparison can be reported')


if __name__=='__main__':
    main()
