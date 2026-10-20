#!/usr/bin/env python3
"""Frozen Codex-only development repair: freeze, generate, run, report.

No holdout loader is used. All model calls are confined to generate/run.
Writing is accepted on first transport success, never redrawn for quality.
"""
import argparse
import collections
from contextlib import contextmanager
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
from pathlib import Path
import random
import re
import statistics
import subprocess
import time
from types import SimpleNamespace

import bench
import context_regrade as context
import pairwise

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = {
    'astra-medium': ('codex', 'gpt-6-astra', 'medium'),
    'astra-high': ('codex', 'gpt-6-astra', 'high'),
    'sol-low': ('codex', 'gpt-6.1-sol', 'low'),
    'luna-medium': ('codex', 'gpt-6-luna', 'medium'),
}
JUDGES = dict(context.JUDGES)
REFERENCES = ('none', 'v4')
SEED = 'declaude-prose-repair-1'
MAX_ATTEMPTS = 4
BATCH_SIZE = 4
CATEGORIES = ('ordinary', 'research', 'argument', 'proof', 'control')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locations(candidate, subset):
    require(bool(re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]*', candidate)), 'Unsafe candidate version')
    require(candidate not in REFERENCES, 'Candidate must have its own version')
    require(subset in ('tune', 'validation'), 'Only development tune/validation are permitted')
    name = candidate + '-' + subset
    return ROOT / 'evals/results/prose-repair' / name, ROOT / '.local/prose-repair' / name


def development(subset):
    require(subset in ('tune', 'validation'), 'No holdout selection')
    rows = read(ROOT / 'evals/large/development.json')['cases']
    require(len(rows) == 40 and len({c['id'] for c in rows}) == 40, 'Expected 40 unique development cases')
    require(all(c['split'] == 'development' and c['subset'] in ('tune', 'validation') for c in rows), 'Nondevelopment case')
    selected = sorted((c for c in rows if c['subset'] == subset), key=lambda c: c['id'])
    require(len(selected) == 20, 'Expected 20 cases per subset')
    require(all(re.fullmatch(r'[A-Za-z0-9_-]+', c['id']) for c in selected), 'Unsafe case ID')
    return selected


def baselines(cases):
    ids = {c['id'] for c in cases}
    # Filter by selected development ID FIRST. Never inspect holdout fields/text.
    rows = [r for r in read(ROOT / 'evals/results/large-interim/responses.json') if r['case'] in ids]
    rows = [r for r in rows if r['config'] in CONFIGS and r['arm'] in REFERENCES]
    expected = {(c, cfg, arm) for c in ids for cfg in CONFIGS for arm in REFERENCES}
    require(len(rows) == len(expected) and {(r['case'], r['config'], r['arm']) for r in rows} == expected, 'Missing/duplicate saved development baselines')
    bycase = {c['id']: c for c in cases}
    v4_hash = pairwise.text_hash(bench.bundle(ROOT / 'evals/versions/v4'))
    for r in rows:
        c = bycase[r['case']]
        require(r['split'] == 'development' and r['subset'] == c['subset'], 'Baseline split mismatch')
        require(r['task_sha256'] == pairwise.text_hash(c['task']), 'Baseline task changed')
        require((r['model'], r['effort']) == CONFIGS[r['config']][1:], 'Baseline model mismatch')
        require(r['skill_sha256'] == (v4_hash if r['arm'] == 'v4' else None), 'Baseline v4 bundle mismatch')
    return sorted(rows, key=lambda r: (r['case'], r['config'], r['arm']))


def jobs_for(cases, candidate):
    grouped = {c['id']: [(c['id'], cfg, ref) for cfg in CONFIGS for ref in REFERENCES] for c in cases}
    # Exactly 20% of unique primary pairs, shared across judges, at least one/case.
    rank = lambda p: pairwise.digest([SEED, p, 'audit'])
    audited = {min(ps, key=rank) for ps in grouped.values()}
    rest = sorted((p for ps in grouped.values() for p in ps if p not in audited), key=rank)
    total = sum(map(len, grouped.values()))
    audited.update(rest[:max(0, math.ceil(.2 * total) - len(audited))])
    jobs = []
    for cid, ps in sorted(grouped.items()):
        for judge in JUDGES:
            ordered = sorted(ps, key=lambda p: pairwise.digest([SEED, judge, p, 'position']))
            for order in ('primary', 'reversed'):
                entries = []
                for i, p in enumerate(ordered):
                    if order == 'reversed' and p not in audited:
                        continue
                    side = ('left', 'right')[(i + (order == 'reversed')) % 2]
                    entries.append(dict(case=cid, config=p[1], candidate=candidate, reference=p[2], a_side=side))
                for start in range(0, len(entries), BATCH_SIZE):
                    chunk = [dict(e, label=f'P{i+1:02}') for i, e in enumerate(entries[start:start+BATCH_SIZE])]
                    job = dict(case=cid, judge=judge, order=order, pairs=chunk)
                    job['id'] = pairwise.digest(job)[:24]
                    jobs.append(job)
    return jobs


def public_safe(value):
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    require(not re.search(r'/(?:Users|home|private|tmp|var/folders)/|\.local/|Bearer\s+[A-Za-z0-9_-]{12,}|sk-[A-Za-z0-9_-]{20,}', text), 'Private data detected; publication stopped')


def freeze(candidate, subset, skill=None):
    public, work = locations(candidate, subset)
    with pairwise.locked(work):
        require(not (public / 'plan.json').exists(), 'Plan already frozen; choose a new explicit version')
        cases = development(subset)
        refs = baselines(cases)
        skill = Path(skill) if skill else ROOT / 'evals/versions' / candidate
        files = [skill / 'SKILL.md'] + sorted((skill / 'references').glob('*.md'))
        files = [p for p in files if not p.name.endswith('.local.md')]
        bundle = bench.bundle(skill)
        proof = skill / 'references/proofs.md'
        packaged = ROOT / 'skill/references/proofs.md'
        v4 = ROOT / 'evals/versions/v4/references/proofs.md'
        require(proof.read_bytes() == packaged.read_bytes() == v4.read_bytes(), 'Proof guidance must match packaged v4 byte for byte')
        frozen_context = ROOT / 'evals/results/context-regrade'
        author = read(frozen_context / 'author-context.json')
        require(author == context.CONTEXT, 'Author context differs from frozen contextual judge')
        payloads = {'cases.json': cases, 'baselines.json': refs, 'author-context.json': author}
        texts = {'bundle.txt': bundle, 'rubric.txt': (frozen_context / 'rubric.txt').read_text()}
        blobs = {'proofs.md': proof.read_bytes()}
        protocol = ROOT / 'evals/large/prose-repair-protocol.md'
        if protocol.exists():
            texts['protocol.md'] = protocol.read_text()
        for value in [*payloads.values(), *texts.values(), proof.read_text()]:
            public_safe(value)
        public.mkdir(parents=True, exist_ok=True)
        for name, value in payloads.items():
            pairwise.save_json(public / name, value)
        for name, value in texts.items():
            pairwise.atomic_write(public / name, value)
        for name, value in blobs.items():
            (public / name).write_bytes(value)
        jobs = jobs_for(cases, candidate)
        plan = dict(schema='prose-repair-v1', candidate=candidate, subset=subset, seed=SEED,
                    configs=CONFIGS, judges=JUDGES, references=list(REFERENCES), batch_size=BATCH_SIZE,
                    max_attempts=MAX_ATTEMPTS, generated_output_cap=80,
                    generation_attempt_cap=320, judge_attempt_cap=MAX_ATTEMPTS * len(jobs),
                    case_ids=[c['id'] for c in cases], jobs=jobs,
                    files={name: sha(public / name) for name in [*payloads, *texts, *blobs]},
                    candidate_files={str(p.relative_to(skill)): sha(p) for p in files},
                    bundle_sha256=pairwise.text_hash(bundle), proof_sha256=sha(proof),
                    source_development_sha256=sha(ROOT / 'evals/large/development.json'),
                    selected_baselines_sha256=pairwise.digest(refs),
                    rubric_source_sha256=sha(frozen_context / 'rubric.txt'),
                    context_source_sha256=sha(frozen_context / 'author-context.json'),
                    audit_fraction=.2, primary_judgments=320,
                    audit_judgments=sum(len(j['pairs']) for j in jobs if j['order'] == 'reversed'),
                    policy='First transport-valid writing and first fully schema-valid batch only. Four attempts for transport/schema failures. No writing quality retries. Development only; fresh holdout reserved unrun.',
                    tool_sha256={name: sha(ROOT / 'tools' / name) for name in ('prose_repair.py', 'bench.py', 'context_regrade.py', 'pairwise.py')})
        plan['plan_sha256'] = pairwise.digest(plan)
        public_safe(plan)
        pairwise.save_json(public / 'plan.json', plan)
        pairwise.save_json(work / 'freeze.json', dict(plan_sha256=plan['plan_sha256'], skill=str(skill.resolve())))
    return plan


def load(candidate, subset):
    public, work = locations(candidate, subset)
    plan = read(public / 'plan.json')
    require(plan['plan_sha256'] == pairwise.digest({k: v for k, v in plan.items() if k != 'plan_sha256'}), 'Frozen plan hash changed')
    require((plan['candidate'], plan['subset']) == (candidate, subset), 'Frozen identity mismatch')
    require(plan['configs'] == {k: list(v) for k, v in CONFIGS.items()} and plan['judges'] == {k: list(v) for k, v in JUDGES.items()}, 'Frozen provider/model/effort changed')
    require(plan['max_attempts'] == MAX_ATTEMPTS and plan['generated_output_cap'] == 80, 'Frozen limits changed')
    for name, expected in plan['files'].items():
        require('/' not in name and name not in ('.', '..'), 'Unsafe frozen filename')
        require(sha(public / name) == expected, 'Frozen input hash changed: ' + name)
    cases = read(public / 'cases.json')
    require(len(cases) == 20 and len({c['id'] for c in cases}) == 20, 'Frozen case matrix mismatch')
    require(all(c['split'] == 'development' and c['subset'] == subset for c in cases), 'Nondevelopment frozen case')
    require(plan['case_ids'] == [c['id'] for c in cases] and jobs_for(cases, candidate) == plan['jobs'], 'Frozen jobs changed')
    require(plan['bundle_sha256'] == sha(public / 'bundle.txt') and plan['proof_sha256'] == sha(public / 'proofs.md'), 'Frozen bundle/proof mismatch')
    refs = read(public / 'baselines.json')
    require(pairwise.digest(refs) == plan['selected_baselines_sha256'], 'Frozen baselines changed')
    wanted = {(c['id'], cfg, arm) for c in cases for cfg in CONFIGS for arm in REFERENCES}
    require(len(refs) == len(wanted) and {(r['case'], r['config'], r['arm']) for r in refs} == wanted, 'Frozen reference matrix mismatch')
    author = read(public / 'author-context.json')
    contextual = {c['id']: dict(c, user_context=author['common']+'\n\n'+author[c['category']], is_proof=c['category']=='proof') for c in cases}
    texts = {(r['case'], r['config'], r['arm']): r['response'] for r in refs}
    if (work / 'freeze.json').exists():
        require(read(work / 'freeze.json')['plan_sha256'] == plan['plan_sha256'], 'Private freeze anchor mismatch')
    return plan, (public / 'rubric.txt').read_text(), contextual, texts


def guard(config, allowed):
    require(config in allowed, 'Configuration is outside the frozen Codex manifest')
    actual = bench.CONFIGS.get(config)
    require(actual is not None and actual[0] == 'codex' and tuple(actual) == tuple(allowed[config]), 'Only frozen Codex provider/model/effort allowed')


def clean_meta(meta, config, allowed):
    require((meta.get('model'), meta.get('effort')) == tuple(allowed[config])[1:], 'Returned model/effort mismatch')
    usage = {k: v for k, v in meta.get('usage', {}).items() if k in ('reported_tokens', 'input_tokens', 'output_tokens', 'total_tokens') and type(v) in (int, float)}
    return dict(provider='codex', model=meta['model'], effort=meta['effort'], usage=usage)


@contextmanager
def capture_cli(directory):
    """bench.call normally discards CLI envelopes. Retain them locally, including timeouts."""
    original = bench.subprocess
    count = 0
    def execute(*args, **kwargs):
        nonlocal count
        count += 1
        require(count == 1, 'Unexpected extra CLI invocation')
        try:
            result = original.run(*args, **kwargs)
        except subprocess.TimeoutExpired as exc:
            pairwise.save_json(directory / 'cli.json', dict(timeout=True, stdout=str(exc.stdout or ''), stderr=str(exc.stderr or '')))
            raise
        finally:
            # Preserve even a failed/timeout invocation's last-message bytes before
            # bench.call removes its TemporaryDirectory. Envelopes stay private.
            command = args[0] if args else kwargs.get('args', [])
            if isinstance(command, (list, tuple)) and '-o' in command:
                output = Path(command[command.index('-o') + 1])
                if output.is_file():
                    (directory / 'cli-last-message.txt').write_bytes(output.read_bytes())
        pairwise.save_json(directory / 'cli.json', dict(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
        return result
    bench.subprocess = SimpleNamespace(run=execute)
    try:
        yield
    finally:
        bench.subprocess = original


def transport(prompt, config, directory, allowed, original):
    """Cache every attempt before validation. Interrupted attempts are never repeated."""
    guard(config, allowed)
    directory.mkdir(parents=True, exist_ok=True)
    fingerprint = pairwise.digest(dict(prompt=prompt, config=config, identity=allowed[config]))
    request = dict(prompt=prompt, config=config, fingerprint=fingerprint)
    if (directory / 'request.json').exists():
        require(read(directory / 'request.json') == request, 'Cached request changed')
    else:
        pairwise.save_json(directory / 'request.json', request)
    for attempt in range(1, MAX_ATTEMPTS+1):
        d = directory / str(attempt)
        status = d / 'status.json'
        raw = d / 'raw.txt'
        if status.exists():
            state = read(status)
            if state['state'] == 'answered':
                text = raw.read_text()
                require(pairwise.text_hash(text) == state['raw_sha256'], 'Cached raw answer changed')
                clean_meta(state['call'], config, allowed)
                yield attempt, text, state['call']
            else:
                require(state['state'] in ('calling', 'transport_error'), 'Unknown cached attempt state')
            continue
        require(not raw.exists(), 'Orphaned raw attempt; manual recovery required')
        pairwise.save_json(status, dict(state='calling', config=config, started=time.time(), runner_sha256=sha(Path(__file__))))
        try:
            guard(config, allowed)
            with capture_cli(d):
                text, meta = original(prompt, config)
        except (RuntimeError, subprocess.SubprocessError, OSError) as exc:
            pairwise.save_json(status, dict(state='transport_error', config=config, error=repr(exc), runner_sha256=sha(Path(__file__))))
            continue
        # Persist exact raw answer before any metadata/schema processing.
        pairwise.atomic_write(raw, text)
        meta = clean_meta(meta, config, allowed)
        pairwise.save_json(status, dict(state='answered', config=config, call=meta, raw_sha256=pairwise.text_hash(text), runner_sha256=sha(Path(__file__))))
        yield attempt, text, meta


def generation_prompt(case, bundle):
    return ('Complete the following writing task. Return the requested artifact, not a plan. All needed source text is supplied; do not use tools.\n\n'
            + '<editing-guidance>\n' + bundle + '\n</editing-guidance>\n\n<task>\n' + case['task'] + '\n</task>')


def generation_one(plan, case, cfg, work, bundle):
    """One process owns bench's temporary call wrapper and one output lock."""
    candidate = plan['candidate']
    d = work / 'generation' / case['id'] / cfg
    with pairwise.locked(d):
        expected_prompt = generation_prompt(case, bundle)
        original = bench.call
        def guarded_call(prompt, config, **kwargs):
            require(config == cfg and prompt == expected_prompt, 'Generation outside frozen manifest')
            guard(config, plan['configs'])
            for attempt, text, meta in transport(prompt, config, d, plan['configs'], original):
                pairwise.save_json(d / 'accepted.json', dict(attempt=attempt, raw_sha256=pairwise.text_hash(text), prompt_sha256=pairwise.text_hash(prompt), plan_sha256=plan['plan_sha256']))
                return text, meta
            raise RuntimeError('Generation transport attempts exhausted')
        bench.call = guarded_call
        try:
            guard(cfg, plan['configs'])
            bench.run_one(case, cfg, candidate, bundle, work / 'runs')
            validate_generation(plan, case, cfg, work, bundle)
        finally:
            bench.call = original
    return case['id'] + '/' + cfg


def parallel(function, arguments, workers, work):
    require(1 <= workers <= 32, 'Workers must be between 1 and 32')
    failures = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(function, *args): i for i, args in enumerate(arguments)}
        for done, future in enumerate(as_completed(futures), 1):
            try:
                print(done, '/', len(arguments), future.result(), 'cached', flush=True)
            except Exception as exc:
                failures += 1
                pairwise.save_json(work / ('job-error-' + str(futures[future]) + '.json'), dict(error=repr(exc)))
                print(done, '/', len(arguments), 'incomplete; private error saved', flush=True)
    require(not failures, 'Some jobs failed; available results retained')


def generation(candidate, subset, workers=8):
    public, work = locations(candidate, subset)
    with pairwise.locked(work):
        plan, _, cases, _ = load(candidate, subset)
        bundle = (public / 'bundle.txt').read_text()
        anchor = read(work / 'freeze.json')
        skill = Path(anchor['skill'])
        require(pairwise.text_hash(bench.bundle(skill)) == plan['bundle_sha256'], 'Live candidate changed after freeze')
        require(sha(ROOT / 'skill/references/proofs.md') == plan['proof_sha256'], 'Packaged proof changed')
        for cfg in CONFIGS:
            guard(cfg, plan['configs'])
        parallel(generation_one, [(plan, case, cfg, work, bundle) for case in cases.values() for cfg in CONFIGS], workers, work)


def validate_generation(plan, case, cfg, work, bundle):
    d = work / 'generation' / case['id'] / cfg
    accepted = read(d / 'accepted.json')
    attempt = accepted['attempt']
    require(1 <= attempt <= MAX_ATTEMPTS, 'Generation attempt out of range')
    for earlier in range(1, attempt):
        require(read(d / str(earlier) / 'status.json')['state'] in ('transport_error', 'calling'), 'Earlier valid writing discarded')
    status = read(d / str(attempt) / 'status.json')
    raw = (d / str(attempt) / 'raw.txt').read_text()
    require(status['state'] == 'answered' and status['raw_sha256'] == accepted['raw_sha256'] == pairwise.text_hash(raw), 'Generation raw hash mismatch')
    require(accepted['plan_sha256'] == plan['plan_sha256'] and accepted['prompt_sha256'] == pairwise.text_hash(generation_prompt(case, bundle)), 'Generation provenance mismatch')
    dest = work / 'runs' / case['id'] / cfg / plan['candidate']
    text = (dest / 'response.md').read_text()
    meta = read(dest / 'meta.json')
    expected = dict(case=case['id'], config=cfg, arm=plan['candidate'], task_sha256=pairwise.text_hash(case['task']), skill_sha256=plan['bundle_sha256'])
    require(all(meta.get(k) == v for k, v in expected.items()), 'Generation metadata mismatch')
    clean_meta(meta, cfg, plan['configs'])
    require(text == raw+'\n', 'Generation output changed')
    return dict(case=case['id'], config=cfg, arm=plan['candidate'], response=text, response_sha256=pairwise.text_hash(text), **{k: meta[k] for k in ('model', 'effort', 'task_sha256', 'skill_sha256')}, attempt=attempt, prompt_sha256=accepted['prompt_sha256'], raw_sha256=accepted['raw_sha256'])


def request(job, rubric, cases, texts):
    # Adapt the existing anonymous batch adapter; its reference lookup is none-only.
    proxy_texts = {}
    proxy_job = dict(job, pairs=[])
    for i, e in enumerate(job['pairs']):
        alias = str(i)
        proxy_job['pairs'].append(dict(e, config=alias))
        proxy_texts[e['case'], alias, 'none'] = texts[e['case'], e['config'], e['reference']]
        proxy_texts[e['case'], alias, e['candidate']] = texts[e['case'], e['config'], e['candidate']]
    return context.request(proxy_job, rubric, cases, proxy_texts)


def records_for(job, raw, attempt, rubric, cases, texts, plan):
    prompt, supplied, pairs = request(job, rubric, cases, texts)
    parsed, syntax = context.parse_batch(raw)
    pairwise.require(isinstance(parsed, dict) and set(parsed) == set(pairs), 'Batch labels mismatch')
    records = []
    for e in job['pairs']:
        verdict, repairs = context.repair_evidence(parsed[e['label']], dict(supplied, responses=pairs[e['label']]))
        verdict = pairwise.validate_verdict(verdict, dict(supplied, responses=pairs[e['label']]))
        label = 'A' if e['a_side'] == 'right' else 'B'
        r = dict(version='prose-repair-v1', batch=job['id'], case=e['case'], config=e['config'], candidate=e['candidate'], reference=e['reference'], judge=job['judge'], order=job['order'], candidate_position=label, pair_id=e['label'], attempt=attempt, raw_judgment=verdict, **pairwise.normalized(verdict, label), response_sha256={arm: pairwise.text_hash(texts[e['case'], e['config'], arm]) for arm in (e['reference'], e['candidate'])}, prompt_sha256=pairwise.text_hash(prompt), raw_sha256=pairwise.text_hash(raw), rubric_sha256=pairwise.text_hash(rubric), context_sha256=pairwise.text_hash(supplied['user_context']), plan_sha256=plan['plan_sha256'], evidence_format_repairs=repairs, json_syntax_repairs=syntax)
        r['record_sha256'] = pairwise.digest(r)
        records.append(r)
    return records


def judge_one(job, plan, rubric, cases, texts, work):
    d = work / 'judges' / job['id']
    with pairwise.locked(d):
        for key, value in JUDGES.items():
            if key not in bench.CONFIGS:
                bench.CONFIGS[key] = value
            guard(key, plan['judges'])
        prompt, _, _ = request(job, rubric, cases, texts)
        accepted = None
        for attempt, raw, meta in transport(prompt, job['judge'], d, plan['judges'], bench.call):
            try:
                records = records_for(job, raw, attempt, rubric, cases, texts, plan)
            except pairwise.SchemaError as exc:
                pairwise.save_json(d / str(attempt) / 'invalid.json', dict(error=str(exc)))
                continue
            accepted = records
            break
        require(accepted is not None, 'Judge attempts exhausted; inspect private artifacts')
        if (d / 'records.json').exists():
            require(read(d / 'records.json') == accepted, 'Cached first valid verdict changed')
        else:
            pairwise.save_json(d / 'records.json', accepted)
    return job['id']


def run(candidate, subset, workers=8):
    generation(candidate, subset, workers)
    public, work = locations(candidate, subset)
    with pairwise.locked(work):
        plan, rubric, cases, texts = load(candidate, subset)
        bundle = (public / 'bundle.txt').read_text()
        for cid, case in cases.items():
            for cfg in CONFIGS:
                row = validate_generation(plan, case, cfg, work, bundle)
                texts[cid, cfg, candidate] = row['response']
        parallel(judge_one, [(job, plan, rubric, cases, texts, work) for job in plan['jobs']], workers, work)


def net_stats(rows, dimension=None, samples=3000):
    """Signed case means and a case bootstrap. Ties always contribute zero."""
    score = {'win': 1, 'tie': 0, 'loss': -1}
    grouped = collections.defaultdict(list)
    counts = collections.Counter()
    for r in rows:
        outcome = r['outcome'] if dimension is None else r['dimensions'][dimension]
        if outcome == 'NA':
            continue
        require(outcome in score, 'Unknown outcome')
        grouped[r['case']].append(score[outcome])
        counts[outcome] += 1
    if not grouped:
        return None
    means = {cid: statistics.mean(values) for cid, values in grouped.items()}
    ids = sorted(means)
    rng = random.Random(47132026)
    draws = sorted(100 * statistics.mean(means[cid] for cid in rng.choices(ids, k=len(ids))) for _ in range(samples))
    return dict(net_pp=100 * statistics.mean(means.values()), net_ci95_pp=[draws[int(.025*samples)], draws[int(.975*samples)-1]], cases=len(ids), judgments=sum(counts.values()), wins=counts['win'], ties=counts['tie'], losses=counts['loss'])


def expected_keys(plan):
    return {(e['case'], e['config'], e['candidate'], e['reference'], j['judge'], j['order']) for j in plan['jobs'] for e in j['pairs']}


def complete_matrix(plan, records):
    keys = [(r['case'], r['config'], r['candidate'], r['reference'], r['judge'], r['order']) for r in records]
    require(len(keys) == len(set(keys)), 'Duplicate observations')
    require(set(keys) == expected_keys(plan), 'Incomplete or unexpected verdict matrix; headline statistics forbidden')
    require(sum(r['order'] == 'primary' for r in records) == plan['primary_judgments'], 'Primary count mismatch')
    require(sum(r['order'] == 'reversed' for r in records) == plan['audit_judgments'], 'Audit count mismatch')


def agreement(records):
    cross = collections.defaultdict(dict)
    order = collections.defaultdict(dict)
    for r in records:
        key = (r['case'], r['config'], r['candidate'], r['reference'])
        if r['order'] == 'primary':
            cross[key][r['judge']] = r
        order[key + (r['judge'],)][r['order']] = r
    def count(pairs):
        return dict(pairs=len(pairs), cases=len({a['case'] for a, b in pairs}), same=sum(a['outcome'] == b['outcome'] for a, b in pairs), opposite=sum({a['outcome'], b['outcome']} == {'win', 'loss'} for a, b in pairs))
    judge_pairs = [tuple(v[j] for j in JUDGES) for v in cross.values() if set(v) == set(JUDGES)]
    order_pairs = [(v['primary'], v['reversed']) for v in order.values() if set(v) == {'primary', 'reversed'}]
    return dict(cross_judge=count(judge_pairs), order=count(order_pairs), order_by_judge={j: count([(a, b) for a, b in order_pairs if a['judge'] == j]) for j in JUDGES})


def summarize(plan, cases, records, attempts):
    complete_matrix(plan, records)
    primary = [r for r in records if r['order'] == 'primary']
    def metrics(rows):
        return dict(overall=net_stats(rows), nonproof=net_stats([r for r in rows if cases[r['case']]['category'] != 'proof']), categories={cat: net_stats([r for r in rows if cases[r['case']]['category'] == cat]) for cat in CATEGORIES}, dimensions={dim: net_stats(rows, dim) for dim in pairwise.DIMENSIONS if dim != 'overall'}, material_flags={arm: dict(flags=sum(r[arm+'_material_error'] for r in rows), judgments=len(rows), cases=len({r['case'] for r in rows}), severity=dict(collections.Counter(r['raw_judgment']['material_errors'][r['candidate_position'] if arm == 'candidate' else ('B' if r['candidate_position'] == 'A' else 'A')]['severity'] for r in rows))) for arm in ('candidate', 'reference')})
    comparisons = {}
    for ref in REFERENCES:
        rows = [r for r in primary if r['reference'] == ref]
        comparisons[ref] = dict(**metrics(rows), models={cfg: metrics([r for r in rows if r['config'] == cfg]) for cfg in CONFIGS}, judges={judge: metrics([r for r in rows if r['judge'] == judge]) for judge in JUDGES}, agreement=agreement([r for r in records if r['reference'] == ref]))
    def usage(rows):
        return dict(attempts=len(rows), answered=sum(r['state'] == 'answered' for r in rows), transport_errors=sum(r['state'] == 'transport_error' for r in rows), interrupted=sum(r['state'] == 'calling' for r in rows), invalid_schema=sum(r.get('invalid_schema', False) for r in rows), calls_with_reported_tokens=sum('reported_tokens' in r.get('call', {}).get('usage', {}) for r in rows), reported_tokens=sum(r.get('call', {}).get('usage', {}).get('reported_tokens', 0) for r in rows))
    return dict(candidate=plan['candidate'], subset=plan['subset'], status='complete', plan_sha256=plan['plan_sha256'], metric='case-averaged win percentage minus loss percentage; ties zero, retained in denominator', bootstrap=dict(unit='case', samples=3000, seed=47132026), cases=len(cases), primary_judgments=len(primary), audit_judgments=len(records)-len(primary), comparisons=comparisons, agreement=agreement(records), usage=dict(**usage(attempts), by_stage={stage: usage([r for r in attempts if r['stage'] == stage]) for stage in ('generation', 'judge')}, claude_calls=0, saved_baselines_reused=160, generation_outputs=80), limitations='Development data, not untouched evaluation. Two fallible Codex judges use frozen author-specific context. Audits do not enter performance. CLI token usage omits unavailable reports and is not account usage or a billing estimate.')


def audit_attempts(directory, stage, identity, config, allowed):
    rows = []
    # Unknown attempt directories must not silently exceed the frozen cap.
    numbered = {p.name for p in directory.iterdir() if p.is_dir() and p.name.isdigit()}
    require(numbered <= {str(i) for i in range(1, MAX_ATTEMPTS+1)}, 'Attempt cap exceeded')
    for number in range(1, MAX_ATTEMPTS+1):
        d = directory / str(number)
        if not (d / 'status.json').exists():
            continue
        s = read(d / 'status.json')
        require(s['config'] == config and s['state'] in ('calling', 'answered', 'transport_error'), 'Attempt identity/state mismatch')
        row = dict(stage=stage, identity=identity, config=config, attempt=number, state=s['state'], invalid_schema=(d / 'invalid.json').exists(), runner_sha256=s.get('runner_sha256'))
        if s['state'] == 'answered':
            raw = (d / 'raw.txt').read_text()
            require(s['raw_sha256'] == pairwise.text_hash(raw), 'Attempt raw hash mismatch')
            row['raw_sha256'] = s['raw_sha256']
            row['call'] = clean_meta(s['call'], config, allowed)
        rows.append(row)
    return rows


def local_evidence(plan, rubric, cases, texts, public, work):
    outputs, attempts, records, accepted_raw = [], [], [], []
    bundle = (public / 'bundle.txt').read_text()
    expected_gen = {(cid, cfg) for cid in cases for cfg in CONFIGS}
    actual_gen = {(p.parent.name, p.name) for p in (work / 'generation').glob('*/*') if p.is_dir()}
    require(actual_gen == expected_gen, 'Generation directory matrix mismatch')
    for cid, case in cases.items():
        for cfg in CONFIGS:
            row = validate_generation(plan, case, cfg, work, bundle)
            outputs.append(row)
            texts[cid, cfg, plan['candidate']] = row['response']
            d = work / 'generation' / cid / cfg
            prompt = generation_prompt(case, bundle)
            require(read(d / 'request.json') == dict(prompt=prompt, config=cfg, fingerprint=pairwise.digest(dict(prompt=prompt, config=cfg, identity=plan['configs'][cfg]))), 'Generation request mismatch')
            attempts.extend(audit_attempts(d, 'generation', dict(case=cid, config=cfg), cfg, plan['configs']))
    require({p.name for p in (work / 'judges').iterdir() if p.is_dir()} == {j['id'] for j in plan['jobs']}, 'Judge directory matrix mismatch')
    for job in plan['jobs']:
        d = work / 'judges' / job['id']
        cached = read(d / 'records.json')
        require(cached and len({r['attempt'] for r in cached}) == 1, 'Batch attempt mismatch')
        accepted = cached[0]['attempt']
        require(1 <= accepted <= MAX_ATTEMPTS, 'Judge attempt out of range')
        prompt, _, _ = request(job, rubric, cases, texts)
        saved_request = read(d / 'request.json')
        require(saved_request == dict(prompt=prompt, config=job['judge'], fingerprint=pairwise.digest(dict(prompt=prompt, config=job['judge'], identity=plan['judges'][job['judge']]))), 'Judge request mismatch')
        batch_attempts = audit_attempts(d, 'judge', dict(batch=job['id']), job['judge'], plan['judges'])
        attempts.extend(batch_attempts)
        first_valid = None
        for a in batch_attempts:
            require(a['attempt'] <= accepted, 'Attempt after accepted judgment')
            if a['state'] != 'answered':
                continue
            raw = (d / str(a['attempt']) / 'raw.txt').read_text()
            try:
                rebuilt = records_for(job, raw, a['attempt'], rubric, cases, texts, plan)
            except pairwise.SchemaError:
                require(a['invalid_schema'], 'Invalid schema attempt was not recorded')
                continue
            require(not a['invalid_schema'], 'Valid verdict marked invalid')
            first_valid = a['attempt']
            require(first_valid == accepted and rebuilt == cached, 'First valid judgment or normalized evidence changed')
            accepted_raw.append(dict(batch=job['id'], attempt=accepted, text=raw, raw_sha256=pairwise.text_hash(raw)))
            records.extend(rebuilt)
            break
        require(first_valid == accepted, 'No valid accepted judgment')
    complete_matrix(plan, records)
    return outputs, records, accepted_raw, attempts


def portable_evidence(plan, rubric, cases, texts, public):
    publication = read(public / 'publication.json')
    require(publication['plan_sha256'] == plan['plan_sha256'], 'Publication plan mismatch')
    for filename, digest in publication['files'].items():
        require('/' not in filename and filename not in ('.', '..'), 'Unsafe public filename')
        require(sha(public / filename) == digest, 'Published file hash changed')
    outputs = read(public / 'responses.json')
    expected = {(cid, cfg, arm) for cid in cases for cfg in CONFIGS for arm in (*REFERENCES, plan['candidate'])}
    require(len(outputs) == len(expected) and {(r['case'], r['config'], r['arm']) for r in outputs} == expected, 'Published response matrix mismatch')
    generated = []
    for r in outputs:
        key = (r['case'], r['config'], r['arm'])
        require(pairwise.text_hash(r['response']) == r['response_sha256'], 'Published response hash mismatch')
        if r['arm'] in REFERENCES:
            require(r['response'] == texts[key], 'Saved baseline changed')
        else:
            require(r['task_sha256'] == pairwise.text_hash(cases[r['case']]['task']) and r['skill_sha256'] == plan['bundle_sha256'], 'Published generation input mismatch')
            require((r['model'], r['effort']) == tuple(plan['configs'][r['config']])[1:], 'Published generation model mismatch')
            require(r['response'].endswith('\n') and pairwise.text_hash(r['response'][:-1]) == r['raw_sha256'], 'Published writing raw hash mismatch')
            require(r['prompt_sha256'] == pairwise.text_hash(generation_prompt(cases[r['case']], (public / 'bundle.txt').read_text())), 'Published generation prompt mismatch')
            texts[key] = r['response']
            generated.append(r)
    records = read(public / 'observations.json')
    complete_matrix(plan, records)
    raw = read(public / 'judge-responses.json')
    byraw = {r['batch']: r for r in raw}
    require(len(byraw) == len(raw) and set(byraw) == {j['id'] for j in plan['jobs']}, 'Published raw batch matrix mismatch')
    byrecord = collections.defaultdict(list)
    for r in records:
        byrecord[r['batch']].append(r)
    for j in plan['jobs']:
        r = byraw[j['id']]
        require(1 <= r['attempt'] <= MAX_ATTEMPTS and r['raw_sha256'] == pairwise.text_hash(r['text']), 'Published raw provenance mismatch')
        require(records_for(j, r['text'], r['attempt'], rubric, cases, texts, plan) == byrecord[j['id']], 'Published verdict differs from accepted raw')
    return generated, records, raw, read(public / 'attempts.json')


def validate_attempt_matrix(plan, outputs, records, attempts):
    expected = {('generation', r['case']+'/'+r['config']): (r['attempt'], plan['configs'][r['config']], r['raw_sha256']) for r in outputs}
    expected.update({('judge', r['batch']): (r['attempt'], plan['judges'][r['judge']], r['raw_sha256']) for r in records})
    grouped = collections.defaultdict(list)
    for a in attempts:
        stage = a['stage']
        ident = a['identity']
        key = (stage, ident['case']+'/'+ident['config'] if stage == 'generation' else ident['batch'])
        require(key in expected, 'Unexpected attempted job')
        grouped[key].append(a)
    require(set(grouped) == set(expected), 'Attempt coverage mismatch')
    for key, values in grouped.items():
        accepted, identity, raw_sha = expected[key]
        require(1 <= accepted <= MAX_ATTEMPTS, 'Accepted attempt out of range')
        require(sorted(a['attempt'] for a in values) == list(range(1, accepted+1)), 'Missing/duplicate/extra attempt')
        for a in values:
            require(a['state'] in ('answered', 'calling', 'transport_error'), 'Unknown attempt state')
            if a['state'] == 'answered':
                require((a['call']['provider'], a['call']['model'], a['call']['effort']) == tuple(identity), 'Attempt provider/model/effort mismatch')
            if a['attempt'] == accepted:
                require(a['state'] == 'answered' and not a['invalid_schema'] and a['raw_sha256'] == raw_sha, 'Accepted attempt mismatch')
            else:
                require(a['state'] != 'answered' or (key[0] == 'judge' and a['invalid_schema']), 'First valid answer discarded')
    require(sum(a['stage'] == 'generation' for a in attempts) <= plan['generation_attempt_cap'], 'Generation attempt cap exceeded')
    require(sum(a['stage'] == 'judge' for a in attempts) <= plan['judge_attempt_cap'], 'Judge attempt cap exceeded')


def markdown_report(summary):
    def cell(m):
        if m is None:
            return 'NA'
        lo, hi = m['net_ci95_pp']
        return f"{m['net_pp']:+.1f} [{lo:+.1f}, {hi:+.1f}]"
    lines = ['# Codex development prose repair', '', f"Candidate {summary['candidate']}; development/{summary['subset']}. All {summary['cases']} cases, 80 generated outputs, {summary['primary_judgments']} primary and {summary['audit_judgments']} audit verdicts are complete.", '', 'Net advantage is win percentage minus loss percentage. Ties contribute zero and remain in the denominator. Intervals resample cases, keeping configurations and judges together. Reversed-order audits never enter performance estimates.']
    for ref, data in summary['comparisons'].items():
        lines += ['', '| Reference | Scope | Win / tie / loss | Net advantage, pp [95% case CI] |', '|---|---|---:|---:|']
        scopes = [('overall', data['overall']), ('nonproof', data['nonproof']), *((f'category: {k}', m) for k, m in data['categories'].items()), *((f'dimension: {k}', m) for k, m in data['dimensions'].items()), *((f'generator: {cfg}', m['overall']) for cfg, m in data['models'].items()), *((f'judge: {j}', m['overall']) for j, m in data['judges'].items())]
        for label, m in scopes:
            counts = 'NA' if m is None else f"{m['wins']} / {m['ties']} / {m['losses']}"
            lines.append(f'| {ref} | {label} | {counts} | {cell(m)} |')
        flags = data['material_flags']
        lines += ['', f"Against {ref}: candidate/reference material flags {flags['candidate']['flags']}/{flags['reference']['flags']} in {flags['candidate']['judgments']} primary verdicts. These count judgments, not independent errors.", '']
    agree = summary['agreement']
    lines += [f"Judge agreement: {agree['cross_judge']['same']}/{agree['cross_judge']['pairs']}, with {agree['cross_judge']['opposite']} direct win/loss disagreements. Order agreement: {agree['order']['same']}/{agree['order']['pairs']}, with {agree['order']['opposite']} direct reversals.", '', summary['limitations'], '', f"Usage: {summary['usage']['attempts']} Codex attempts; {summary['usage']['reported_tokens']} reported tokens from {summary['usage']['calls_with_reported_tokens']} attempts with token reports. Zero Claude calls. Failed or interrupted calls without usage are unmeasured.", '', 'summary.json contains category, dimension, generator, judge, nonproof and material-severity breakdowns. observations.json retains full and normalized grades; judge-responses.json contains exact accepted raw verdict text. responses.json contains exact synthetic writing, including reused baselines. All raw attempts, CLI envelopes and errors remain private. publication.json hashes public evidence. execution-amendment.json distinguishes the recorded freeze-time runner from later execution/report source hashes. These are development results and do not authorize promotion or consume the reserved fresh holdout.', '']
    return '\n'.join(lines)


def report(candidate, subset, published=False):
    public, work = locations(candidate, subset)
    with pairwise.locked(work):
        plan, rubric, cases, texts = load(candidate, subset)
        if published:
            outputs, records, raw, attempts = portable_evidence(plan, rubric, cases, texts, public)
        else:
            outputs, records, raw, attempts = local_evidence(plan, rubric, cases, texts, public, work)
        validate_attempt_matrix(plan, outputs, records, attempts)
        summary = summarize(plan, cases, records, attempts)
        if published:
            require(read(public / 'summary.json') == summary, 'Published summary mismatch')
            print('Published evidence and complete matrix verified; no model calls.')
            return summary
        baseline_rows = [dict(r, response_sha256=pairwise.text_hash(r['response'])) for r in read(public / 'baselines.json')]
        normalized = [{k: r[k] for k in ('case', 'config', 'candidate', 'reference', 'judge', 'order', 'outcome', 'dimensions', 'candidate_material_error', 'reference_material_error', 'record_sha256')} for r in records]
        amendment = dict(plan_sha256=plan['plan_sha256'], frozen_runner_sha256=plan['tool_sha256']['prose_repair.py'], report_runner_sha256=sha(Path(__file__)), attempt_runner_sha256=sorted({a['runner_sha256'] for a in attempts if a.get('runner_sha256')}), changes='After freezing, added bounded process scheduling, report/test support (including labeled scopes and table headers), and retention of temporary final-message bytes from failed CLI invocations. Frozen cases, generation prompts, candidate/proof bytes, references, rubric, author context, judges, ordering, batch matrix and retry policy are unchanged.', source_hash_policy='Freeze-time tool hash is descriptive provenance, not a prohibition on adding reporting. Attempt status hashes identify runner bytes on disk when the status was saved; source-only report additions may occur during generation. Raw inputs and accepted outputs are separately bound and strictly revalidated.', generation_workers_default=8)
        payloads = {'responses.json': baseline_rows+outputs, 'observations.json': records, 'grades.json': normalized, 'judge-responses.json': raw, 'attempts.json': attempts, 'summary.json': summary, 'execution-amendment.json': amendment, 'coverage.json': dict(status='complete', cases=20, outputs=80, primary_judgments=plan['primary_judgments'], audit_judgments=plan['audit_judgments'], batches=len(plan['jobs']))}
        markdown = markdown_report(summary)
        for value in [*payloads.values(), markdown]:
            public_safe(value)
        for filename, value in payloads.items():
            pairwise.save_json(public / filename, value)
        pairwise.atomic_write(public / 'report.md', markdown)
        pairwise.save_json(public / 'publication.json', dict(plan_sha256=plan['plan_sha256'], files={name: sha(public / name) for name in [*payloads, 'report.md']}))
        print('Complete development report published; no model calls.')
        return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('freeze', 'generate', 'run', 'report'))
    parser.add_argument('--candidate', default='v8-dev')
    parser.add_argument('--subset', choices=('tune', 'validation'), required=True)
    parser.add_argument('--published', action='store_true', help='Revalidate portable public report without private raw attempts')
    parser.add_argument('--workers', type=int, default=8, help='Isolated worker processes (1-32; generate/run only)')
    parser.add_argument('--skill', type=Path, help='Candidate folder (freeze only)')
    args = parser.parse_args(argv)
    public, work = locations(args.candidate, args.subset)
    try:
        if args.action == 'freeze':
            plan = freeze(args.candidate, args.subset, args.skill)
            print(json.dumps(dict(status='frozen', outputs=80, primary_judgments=320, audit_judgments=plan['audit_judgments'], batches=len(plan['jobs']))))
        elif args.action == 'generate':
            generation(args.candidate, args.subset, args.workers)
        elif args.action == 'run':
            run(args.candidate, args.subset, args.workers)
        else:
            report(args.candidate, args.subset, args.published)
    except Exception as exc:
        pairwise.save_json(work / 'last-error.json', dict(action=args.action, error=repr(exc)))
        parser.exit(1, 'Stopped; details retained in the private prose-repair workspace. No failed call is silently repeated.\n')


if __name__ == '__main__':
    main()
