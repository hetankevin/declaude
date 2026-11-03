#!/usr/bin/env python3
"""Frozen scholarly integration benchmark. No paid calls except `run`.

One ledger covers short writing, both blind judges, order audits, and persistent
revision turns. Private raw envelopes never enter the public result directory.
"""
import argparse
import collections
import json
import time
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path
import bench
import context_regrade as context
import cross_model_small as cross
import grade_long_horizon as transport
import long_horizon as lh
import pairwise
import prose_repair as prior

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evals/results/scholarly-full'
WORK = ROOT / '.local/scholarly-full'
CAND = 'scholarly-20261103'
CONFIGS = ('haiku', 'sonnet-low', 'sonnet-high', 'opus-low', 'opus-xhigh',
           'fable', 'astra-medium', 'astra-high', 'sol-low', 'luna-medium')
SEED = 'scholarly-full-20261103'


def freeze():
    lh.require(not OUT.exists(), 'Already frozen')
    cases = []
    for split in ('development', 'holdout'):
        data = lh.read(ROOT / f'evals/large/{split}.json')
        items = data['cases'] if isinstance(data, dict) else data
        for case in items:
            case = dict(case, split=split)
            case['user_context'] = context.CONTEXT['common'] + '\n\n' + context.CONTEXT[case['category']]
            case['is_proof'] = case['category'] == 'proof'
            cases.append(case)
    lh.require(len(cases) == 80 and len({c['id'] for c in cases}) == 80, 'Case coverage')
    bycase = {c['id']: c for c in cases}
    baseline = [r for r in lh.read(ROOT / 'evals/results/large-interim/responses.json')
                if r['arm'] == 'none' and r['case'] in bycase and r['config'] in CONFIGS]
    existing = {(r['case'], r['config']) for r in baseline}
    lh.require(len(baseline) == len(existing) == 671, 'Saved baseline coverage changed')
    for r in baseline:
        lh.require(r['task_sha256'] == pairwise.text_hash(bycase[r['case']]['task']), 'Baseline task mismatch')
        lh.require((r['model'], r['effort']) == bench.CONFIGS[r['config']][1:], 'Baseline model mismatch')
        lh.require(r['skill_sha256'] is None and r['response'].strip(), 'Invalid baseline')
    paths = [ROOT / 'skill/SKILL.md'] + sorted((ROOT / 'skill/references').glob('*.md'))
    portable = {str(p.relative_to(ROOT / 'skill')): p.read_bytes() for p in paths if not p.name.endswith('.local.md')}
    bundle = bench.bundle(ROOT / 'skill')
    lh.require(pairwise.text_hash(bundle) == '58d57cffd82fd9fb784de10f2d1d746f74a5dbd33af8035f0b4ce3c1029986a4', 'Installed candidate changed')
    # Round-robin split/category to keep an early stopping prefix heterogeneous.
    groups = {(split, cat): [c for c in cases if c['split'] == split and c['category'] == cat]
              for split in ('development', 'holdout') for cat in prior.CATEGORIES}
    lh.require(all(len(v) == 8 for v in groups.values()), 'Expected balanced 80 cases')
    ordered = [groups[key][i] for i in range(8) for key in groups]
    jobs = []
    for c in ordered:
        for cfg in CONFIGS:
            for arm in (CAND, 'none'):
                if arm == 'none' and (c['id'], cfg) in existing:
                    continue
                jobs.append(dict(id=f"{c['id']}--{cfg}--{arm}", stage='generation', case=c['id'], config=cfg, arm=arm))
        for judge in context.JUDGES:
            order = sorted(CONFIGS, key=lambda cfg: pairwise.digest([SEED, c['id'], judge, cfg]))
            sides = {cfg: ('right' if i % 2 else 'left') for i, cfg in enumerate(order)}
            for orientation in ('primary', 'reversed'):
                selected = [cfg for cfg in order if orientation == 'primary' or
                            int(pairwise.digest([SEED, c['id'], cfg, 'audit']), 16) / 2**256 < .1]
                for i in range(0, len(selected), 5):
                    pairs = []
                    for j, cfg in enumerate(selected[i:i+5]):
                        side = sides[cfg]
                        if orientation == 'reversed': side = 'left' if side == 'right' else 'right'
                        pairs.append(dict(case=c['id'], config=cfg, candidate=CAND, reference='none',
                                          judge=judge, order=orientation, a_side=side, label=f'P{j+1:02d}'))
                    jobs.append(dict(id=f"{c['id']}--{judge}--{orientation}--{i//5}", stage='judge',
                                     case=c['id'], judge=judge, order=orientation, pairs=pairs))
    # Real persistent file-editing trajectories, not independent rewrites.
    long_data = lh.read(ROOT / 'evals/long-horizon/development.json')
    lh.validate_cases(long_data, 6)
    for turn in range(1, 7):
        for c in long_data['cases']:
            for arm in ('none', CAND):
                jobs.append(dict(id=f"long--{c['id']}--{arm}--{turn}", stage='long', case=c['id'],
                                 config='astra-high', arm=arm, turn=turn))
    for c in long_data['cases']:
        for judge in context.JUDGES:
            for orientation in ('primary', 'reversed'):
                side = 'A' if int(pairwise.digest([SEED, c['id'], judge]), 16) % 2 else 'B'
                if orientation == 'reversed': side = 'B' if side == 'A' else 'A'
                jobs.append(dict(id=f"long--{c['id']}--{judge}--{orientation}", stage='long-judge',
                                 case=c['id'], judge=judge, order=orientation, candidate_position=side))
    payloads = {'cases.json': cases, 'baselines.json': baseline, 'long-cases.json': long_data,
                'author-context.json': context.CONTEXT}
    for name, value in payloads.items(): lh.public_safe(value); lh.write(OUT / name, value)
    for name, data in {'bundle.txt': bundle.encode(), 'rubric.txt': (ROOT / 'evals/results/context-regrade/rubric.txt').read_bytes(),
                       **{'bundles/' + CAND + '/' + k: v for k, v in portable.items()}}.items():
        lh.public_safe(data.decode()); lh.write(OUT / name, data)
    scripts = ['scholarly_full.py', 'bench.py', 'context_regrade.py', 'cross_model_small.py',
               'grade_long_horizon.py', 'long_horizon.py', 'pairwise.py', 'prose_repair.py', 'small_repair.py']
    plan = dict(candidate=CAND, configs={c: list(bench.CONFIGS[c]) for c in CONFIGS}, judges=context.JUDGES,
                jobs=jobs, max_calls=1600, token_guard=50000000, max_claude_calls=557, max_workers=4,
                reservations={'generation': 60000, 'judge': 100000, 'long': 400000, 'long-judge': 120000},
                retries=0, seed=SEED, baseline_reuse=671, missing_baselines=129,
                audit='Hash-selected 10 percent of case/config pairs, both judges, reversed order. Audits excluded from performance.',
                interpretation='Original 40-case holdout is retrospective for this revision. Fresh 30-case and two-trajectory holdouts remain sealed. No tuning during evaluation.',
                limits='Call and Claude-writing caps are hard. Reported tokens include cached tokens. Scheduling uses reservations; a running call can exceed its reservation. Unknown usage or failed transport stops scheduling. Coordinator usage excluded.',
                long_baselines='Legacy pilot has one first turn and no validated complete trajectory. Run both arms with the same current CLI, six turns, no automatic retries.',
                files={str(p.relative_to(OUT)): lh.hashed(p) for p in OUT.rglob('*') if p.is_file()},
                scripts={n: lh.hashed(ROOT / 'tools' / n) for n in scripts},
                long=dict(configs=lh.CONFIGS, policy=lh.POLICY, introduction=lh.INTRO, turns=6,
                          skill_files={k: lh.digest(v) for k, v in portable.items()}))
    plan['long']['bundle_sha256'] = lh.digest(plan['long']['skill_files'])
    lh.require(len(jobs) <= 1600, 'Call budget exceeds approval')
    lh.require(sum(j['stage'] == 'generation' and bench.CONFIGS[j['config']][0] == 'claude' for j in jobs) == 557, 'Claude call count')
    plan['plan_sha256'] = pairwise.digest(plan)
    lh.write(OUT / 'plan.json', plan)
    print(json.dumps(dict(calls=len(jobs), stages=dict(collections.Counter(j['stage'] for j in jobs)), reused=671)))


def load():
    p = lh.read(OUT / 'plan.json')
    lh.require(p['plan_sha256'] == pairwise.digest({k: v for k, v in p.items() if k != 'plan_sha256'}), 'Plan changed')
    for n, h in p['files'].items(): lh.require(lh.hashed(OUT / n) == h, 'Frozen file changed: ' + n)
    for n, h in p['scripts'].items(): lh.require(lh.hashed(ROOT / 'tools' / n) == h, 'Frozen code changed: ' + n)
    return p, {c['id']: c for c in lh.read(OUT / 'cases.json')}


def directory(job): return WORK / 'calls' / job['id']
def reservation(job): return WORK / 'reservations' / (job['id'] + '.json')
def is_claude(job): return job['stage'] == 'generation' and bench.CONFIGS[job['config']][0] == 'claude'


def ledger(plan):
    rows = []
    for job in plan['jobs']:
        if not reservation(job).exists(): continue
        lh.require(lh.read(reservation(job)) == dict(plan_sha256=plan['plan_sha256'], job=job), 'Reservation mismatch')
        d = directory(job)
        r = lh.read(d / 'result.json') if (d / 'result.json').exists() else None
        known = r is not None and type(r.get('reported_tokens')) is int and r['reported_tokens'] >= 0
        if r and r.get('cli_sha256'):
            raw = d / ('cli.jsonl' if (d / 'cli.jsonl').exists() else 'cli.json')
            lh.require(lh.hashed(raw) == r['cli_sha256'], 'Raw evidence changed')
        rows.append(dict(id=job['id'], stage=job['stage'], claude=is_claude(job), finished=r is not None,
                         known=known, completed=bool(r and r.get('completed')), failed=(d / 'failure.json').exists(),
                         reported_tokens=r['reported_tokens'] if known else None,
                         charged_tokens=r['reported_tokens'] if known else plan['reservations'][job['stage']]))
    return rows


def allowed(plan, job, rows):
    return (not any(r['finished'] and (not r['known'] or not r['completed'] or r['failed']) for r in rows)
            and len(rows) < plan['max_calls']
            and (not is_claude(job) or sum(r['claude'] for r in rows) < plan['max_claude_calls'])
            and sum(r['charged_tokens'] for r in rows) + plan['reservations'][job['stage']] <= plan['token_guard'])


def generation_prompt(case, arm):
    if arm != 'none': return prior.generation_prompt(case, (OUT / 'bundle.txt').read_text())
    return ('Complete the following writing task. Return the requested artifact, not a plan. All needed source text is supplied; do not use tools.\n\n'
            + '<task>\n' + case['task'] + '\n</task>')


def texts_for(plan, cases):
    texts = {(r['case'], r['config'], 'none'): r['response'] for r in lh.read(OUT / 'baselines.json')}
    for job in plan['jobs']:
        if job['stage'] != 'generation': continue
        d = directory(job)
        if not (d / 'result.json').exists() or not lh.read(d / 'result.json').get('completed'): continue
        if not (d / 'answer.txt').exists(): continue
        lh.require(lh.read(d / 'request.json')['prompt'] == generation_prompt(cases[job['case']], job['arm']), 'Writing prompt changed')
        text = (d / 'answer.txt').read_text()
        lh.require(text.strip(), 'Empty draft')
        texts[job['case'], job['config'], job['arm']] = text
    return texts


def long_plan(plan):
    return dict(plan['long'], plan_sha256=plan['plan_sha256'])


def verify_delta(raw, prompt):
    """Support event and response-item rollout representations, without replay."""
    rows = lh.events(raw)
    event = [r['payload']['message'] for r in rows if r.get('type') == 'event_msg' and r.get('payload', {}).get('type') == 'user_message']
    response = [''.join(x.get('text', '') for x in r['payload'].get('content', []) if x.get('type') in ('input_text', 'text'))
                for r in rows if r.get('type') == 'response_item' and r.get('payload', {}).get('role') == 'user']
    lh.require(event == [prompt] or response.count(prompt) == 1, 'Submitted request missing or duplicated in history')
    lh.require(any(r.get('type') == 'turn_context' for r in rows), 'Missing turn context')


def run_long(job, plan, dest):
    case = next(c for c in lh.read(OUT / 'long-cases.json')['cases'] if c['id'] == job['case'])
    p = long_plan(plan)
    d, state = lh.setup(p, OUT / 'plan.json', WORK, case, 'astra-high', job['arm'])
    before = lh.verify_live(d, state)
    ws = Path(state['workspace'])
    lh.check_workspace(ws, lh.guidance(p, OUT / 'plan.json', job['arm']))
    if job['turn'] > 1:
        previous = WORK / 'calls' / (job['id'].rsplit('--', 1)[0] + '--' + str(job['turn'] - 1))
        lh.require(lh.read(previous / 'result.json')['completed'], 'Prior turn incomplete')
        lh.require((previous / 'document.md').read_bytes() == (ws / 'document.md').read_bytes(), 'Live document changed')
    _, prompt = lh.request_for(p, case, job['turn'])
    dest.mkdir(parents=True, mode=0o700)
    lh.write(dest / 'request.json', dict(prompt=prompt, job=job, history_before=lh.digest(before), plan_sha256=plan['plan_sha256']))
    rc = lh.execute(lh.command(p, 'astra-high', state, dest / 'answer.txt'), prompt, ws, lh.environment(d), 1500, dest)
    raw = (dest / 'cli.jsonl').read_bytes()
    parsed = lh.parse_cli(raw)
    # Persist usage before any history/schema validation so failure cannot hide cost.
    lh.write(dest / 'result.json', dict(**parsed, exit_code=rc, cli_sha256=lh.digest(raw)))
    lh.require(rc == 0 and parsed['completed'] and not parsed['failed'] and parsed['reported_tokens'] is not None, 'Long turn incomplete')
    lh.require(state['thread_id'] in (None, parsed['thread_id']) and parsed['thread_id'], 'Thread identity changed')
    state['thread_id'] = parsed['thread_id']
    hp, history = lh.history(d, state)
    lh.write(dest / 'history.jsonl', history)
    lh.require(history.startswith(before), 'History rewritten')
    verify_delta(history[len(before):], prompt)
    lh.check_workspace(ws, lh.guidance(p, OUT / 'plan.json', job['arm']))
    lh.write(dest / 'document.md', (ws / 'document.md').read_bytes())
    state.update(history_path=str(hp), history_sha256=lh.digest(history), history_size=len(history))
    lh.write(d / 'session.json', state)


def long_request(job):
    case = next(c for c in lh.read(OUT / 'long-cases.json')['cases'] if c['id'] == job['case'])
    sources = {}
    for turn in ([1, 6] if job['order'] == 'primary' else [6]):
        source = transport.supplied(case, turn, context.CONTEXT)
        source['responses'] = {label: (WORK / 'calls' / f"long--{case['id']}--{CAND if label == job['candidate_position'] else 'none'}--{turn}" / 'document.md').read_text() for label in ('A', 'B')}
        sources[f'T{turn}'] = source
    prompt = (OUT / 'rubric.txt').read_text() + '\n\nBATCH OUTPUT ADAPTER: Each pair is an independent checkpoint with its own source, chronological requests and anonymous responses. Earlier constraints persist unless superseded. Judge artifact quality, not chat. Return a JSON object mapping every pair ID to its full verdict. Keep evidence short and verbatim. No external tools.\n\nINPUT_JSON:\n' + pairwise.canonical({'pairs': sources})
    return prompt, sources


def grades(job, raw, cases, texts, plan):
    if job['stage'] == 'long-judge':
        prompt, sources = long_request(job)
        entries = [dict(label=k, candidate_position=job['candidate_position'], turn=int(k[1:]), config='astra-high') for k in sources]
    else:
        prompt, supplied, pairs = prior.request(job, (OUT / 'rubric.txt').read_text(), cases, texts)
        sources = {k: dict(supplied, responses=v) for k, v in pairs.items()}
        entries = [dict(e, candidate_position='A' if e['a_side'] == 'right' else 'B') for e in job['pairs']]
    parsed, syntax = context.parse_batch(raw)
    pairwise.keys(parsed, sources, 'batch')
    records, errors = [], []
    for e in entries:
        try:
            verdict, repairs = context.repair_evidence(parsed[e['label']], sources[e['label']])
            pairwise.validate_verdict(verdict, sources[e['label']])
            records.append(dict(case=job['case'], config=e['config'], candidate=CAND, reference='none',
                                judge=job['judge'], order=job['order'], stage=job['stage'], turn=e.get('turn'),
                                candidate_position=e['candidate_position'], raw_judgment=verdict,
                                **pairwise.normalized(verdict, e['candidate_position']), evidence_format_repairs=repairs,
                                json_syntax_repairs=syntax, source_sha256=pairwise.digest(sources[e['label']]),
                                prompt_sha256=pairwise.text_hash(prompt), raw_sha256=pairwise.text_hash(raw), plan_sha256=plan['plan_sha256']))
        except (ValueError, KeyError, TypeError) as exc: errors.append(dict(pair=e['label'], error=str(exc)))
    return records, errors


def execute(job):
    plan, cases = load()
    d = directory(job)
    lh.require(reservation(job).exists() and not (d / 'request.json').exists(), 'Never replay a started call')
    try:
        if job['stage'] == 'generation':
            prompt = generation_prompt(cases[job['case']], job['arm'])
            if is_claude(job): cross.claude_call(prompt, d, job['config'])
            else: transport.call(prompt, d, {'judge': dict(model=bench.CONFIGS[job['config']][1], effort=bench.CONFIGS[job['config']][2])})
        elif job['stage'] == 'long': run_long(job, plan, d)
        else:
            texts = texts_for(plan, cases)
            prompt = long_request(job)[0] if job['stage'] == 'long-judge' else prior.request(job, (OUT / 'rubric.txt').read_text(), cases, texts)[0]
            cfg = context.JUDGES[job['judge']]
            raw = transport.call(prompt, d, {'judge': dict(model=cfg[1], effort=cfg[2])})
            try:
                records, errors = grades(job, raw, cases, texts, plan)
                lh.write(d / 'accepted.json', records); lh.write(d / 'invalid.json', errors)
            except (ValueError, KeyError, TypeError) as exc: lh.write(d / 'invalid.json', [dict(error=str(exc))])
    except Exception as exc:
        if not (d / 'result.json').exists(): lh.write(d / 'result.json', dict(completed=False, reported_tokens=None))
        lh.write(d / 'failure.json', dict(error=repr(exc)))
    return job['id']


def ready(job, texts, done):
    if job['stage'] == 'judge':
        return all((job['case'], e['config'], arm) in texts for e in job['pairs'] for arm in ('none', CAND))
    if job['stage'] == 'long':
        return job['turn'] == 1 or job['id'].rsplit('--', 1)[0] + '--' + str(job['turn'] - 1) in done
    if job['stage'] == 'long-judge':
        return all(f"long--{job['case']}--{arm}--6" in done for arm in ('none', CAND))
    return True


def run(smoke=False):
    plan, cases = load()
    with pairwise.locked(WORK):
        lh.require(all(r['finished'] for r in ledger(plan)), 'Unfinished reservation; inspect without replay')
        jobs = plan['jobs']
        # These are real outputs in the matrix, not extra paid probes.
        smoke_ids = {next(j['id'] for j in jobs if j['stage'] == 'generation' and j['config'] == cfg and j['arm'] == CAND) for cfg in CONFIGS}
        if smoke: jobs = [j for j in jobs if j['id'] in smoke_ids]
        else:
            successful = {r['id'] for r in ledger(plan) if r['completed'] and not r['failed']}
            lh.require(smoke_ids <= successful, 'Run and validate the actual ten-config smoke slice first')
        with ProcessPoolExecutor(max_workers=1 if smoke else plan['max_workers']) as pool:
            active = {}
            while True:
                rows = ledger(plan); done = {r['id'] for r in rows if r['completed'] and not r['failed']}
                texts = texts_for(plan, cases)
                for job in jobs:
                    if len(active) >= (1 if smoke else plan['max_workers']): break
                    if reservation(job).exists() or not ready(job, texts, done) or not allowed(plan, job, rows): continue
                    lh.write(reservation(job), dict(plan_sha256=plan['plan_sha256'], job=job))
                    active[pool.submit(execute, job)] = job
                    rows = ledger(plan)
                if not active: break
                finished, _ = wait(active, timeout=5, return_when=FIRST_COMPLETED)
                for f in finished:
                    job = active.pop(f)
                    try: f.result()
                    except Exception as exc:
                        d = directory(job)
                        if not (d / 'result.json').exists(): lh.write(d / 'result.json', dict(completed=False, reported_tokens=None))
                        lh.write(d / 'failure.json', dict(error=repr(exc)))
                    rows = ledger(plan)
                    print(json.dumps(dict(job=job['id'], calls=len(rows), known_tokens=sum(r['reported_tokens'] or 0 for r in rows), failures=sum(r['failed'] or (r['finished'] and not r['completed']) for r in rows))), flush=True)
        report()


def report():
    plan, cases = load(); texts = texts_for(plan, cases); records = []; invalid = []
    for job in plan['jobs']:
        d = directory(job)
        if job['stage'] not in ('judge', 'long-judge') or not (d / 'accepted.json').exists(): continue
        new, errors = grades(job, (d / 'answer.txt').read_text(), cases, texts, plan)
        lh.require(new == lh.read(d / 'accepted.json'), 'Saved grades changed')
        records += new; invalid += [dict(job=job['id'], **e) for e in errors]
    rows = ledger(plan)
    usage = dict(calls=len(rows), max_calls=plan['max_calls'], claude_calls=sum(r['claude'] for r in rows), max_claude_calls=557,
                 known_reported_tokens=sum(r['reported_tokens'] or 0 for r in rows), charged_tokens=sum(r['charged_tokens'] for r in rows),
                 token_guard=plan['token_guard'], unknown_attempts=sum(r['finished'] and not r['known'] for r in rows), attempts=rows)
    coverage = dict(candidate_outputs=sum(k[2] == CAND for k in texts), expected_candidate_outputs=800,
                    baseline_outputs=sum(k[2] == 'none' for k in texts), expected_baseline_outputs=800,
                    primary_grades=sum(r['stage'] == 'judge' and r['order'] == 'primary' for r in records), expected_primary_grades=1600,
                    audit_grades=sum(r['stage'] == 'judge' and r['order'] == 'reversed' for r in records),
                    expected_audit_grades=sum(len(j['pairs']) for j in plan['jobs'] if j['stage'] == 'judge' and j['order'] == 'reversed'),
                    long_turns=sum(r['stage'] == 'long' and r['completed'] and not r['failed'] for r in rows), expected_long_turns=24,
                    long_grades=sum(r['stage'] == 'long-judge' for r in records), expected_long_grades=12)
    coverage['complete'] = all(coverage[k] == coverage['expected_' + k] for k in ('candidate_outputs', 'baseline_outputs', 'primary_grades', 'audit_grades', 'long_turns', 'long_grades'))
    responses = [dict(case=c, config=cfg, arm=arm, response=s, response_sha256=pairwise.text_hash(s)) for (c, cfg, arm), s in sorted(texts.items())]
    for name, value in [('usage.json', usage), ('coverage.json', coverage), ('responses.json', responses), ('observations.json', records), ('invalid.json', invalid)]:
        lh.public_safe(value); lh.write(OUT / name, value)
    note = ['# Scholarly integration: full evaluation', '',
            'Frozen current portable skill versus no skill. Forty development cases and forty retrospective original holdout cases, ten writer configurations. Both Astra-high and Sol-high author-specific blind judges. Reserved fresh holdouts remain sealed.', '',
            f"Coverage: {coverage['candidate_outputs']}/800 candidate drafts, {coverage['baseline_outputs']}/800 baseline drafts, {coverage['primary_grades']}/1600 primary grades, {coverage['audit_grades']}/{coverage['expected_audit_grades']} reversed-order grades. Long-horizon dev: {coverage['long_turns']}/24 turns, {coverage['long_grades']}/12 checkpoint grades.", '',
            f"Usage: {usage['calls']}/1600 calls, {usage['claude_calls']}/557 Claude writing calls, {usage['known_reported_tokens']:,} known reported tokens (cached included), {usage['unknown_attempts']} unknown attempts. Token scheduling guard: 50M with active-call reservations. This is not a subscription percentage or measured bill.", '',
            'Complete.' if coverage['complete'] else 'INCOMPLETE. No new headline performance claim. Missing and invalid grades are not ties.', '',
            'No tuning, no automatic quality retries, no model substitution. Saved baselines retain a time/backend confound. The author-specific rubric is unchanged but is not independently human-validated. Order audits do not count toward performance. Raw CLI envelopes stay private.']
    lh.write(OUT / 'report.md', ('\n'.join(note) + '\n').encode())
    print(json.dumps(coverage), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=['freeze', 'smoke', 'run', 'report'])
    action = parser.parse_args().action
    if action == 'smoke': run(smoke=True)
    else: globals()[action]()
