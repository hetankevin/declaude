#!/usr/bin/env python3
"""Four-call, frozen-rubric grading adapter for the small revision pilot."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import long_horizon as lh
import pairwise
from context_regrade import parse_batch, repair_evidence

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'evals/results/long-horizon-v9'
WORK = ROOT / '.local/long-horizon-v9-grades'


def load():
    plan = lh.read(PUBLIC / 'judge-plan.json')
    for file, key in [('rubric.txt', 'rubric_sha256'), ('author-context.json', 'context_sha256')]:
        lh.require(lh.hashed(PUBLIC / file) == plan[key], 'Frozen grading input changed')
    lh.require(lh.hashed(ROOT / 'evals/long-horizon/protocol.md') == plan['protocol_sha256'], 'Protocol changed')
    lh.require(plan['max_calls'] == 4 and plan['token_budget'] == 50000 and plan['reservation_tokens'] == 12500, 'Budget changed')
    lh.require(plan['judge'] == {'model': 'gpt-6.1-sol', 'effort': 'high'}, 'Judge changed')
    return plan, lh.read(PUBLIC / 'author-context.json'), (PUBLIC / 'rubric.txt').read_text()


def supplied(case, turn, context):
    # since_turn in the authored cases is zero-based; runner turns are one-based.
    instructions = [case['initial_request']] + case['feedback'][:turn - 1]
    task = 'Original document:\n' + case['initial_document'] + '\n\nChronological user requests through this checkpoint:\n' + '\n\n'.join(f'Turn {i+1}: {x}' for i, x in enumerate(instructions))
    return pairwise.supplied_case(dict(task=task, is_proof=case['is_proof'],
        user_context=context['common'] + '\n\n' + context[case['category']] + ('\n\n' + context['proof'] if case['is_proof'] else ''),
        assertions=[i['text'] for i in case['invariants'] if i['since_turn'] <= turn - 1]))


def request(job, case, rows, depth, context, rubric):
    turns = list(dict.fromkeys([1, depth])) if job['order'] == 'primary' else [depth]
    pairs, metadata = {}, {}
    for index, turn in enumerate(turns, 1):
        key = f'P{index:02d}'
        candidate = job['candidate_position']
        task = supplied(case, turn, context)
        task['responses'] = {label: rows[(case['id'], 'v9-dev' if label == candidate else 'none', turn)]['document'] for label in ('A', 'B')}
        pairs[key] = task
        metadata[key] = {'turn': turn, 'candidate_position': candidate}
    prompt = rubric + '\n\nBATCH OUTPUT ADAPTER: Each pair below is an INDEPENDENT checkpoint task with its own source, user context, chronological instructions, and anonymous responses. Apply the entire rubric separately to each pair. Judge that checkpoint only against its supplied instructions; do not import requests from another pair. Earlier constraints persist unless explicitly superseded. Assess final artifact quality and retention of applicable corrections, not editor chat. Return a JSON object mapping every pair ID to its complete verdict object. Do not rank across pairs or use external tools. Keep evidence excerpts short and verbatim.\n\nINPUT_JSON:\n' + pairwise.canonical({'pairs': pairs})
    return prompt, pairs, metadata


def usage():
    started = list(WORK.glob('job-*/request.json'))
    used = 0
    for p in started:
        out = p.with_name('result.json')
        lh.require(out.exists(), 'Unfinished grading attempt: inspect without replay')
        v = lh.read(out)
        lh.require(lh.hashed(p.with_name('cli.jsonl')) == v['cli_sha256'], 'CLI evidence changed')
        parsed = lh.parse_cli(p.with_name('cli.jsonl').read_bytes())
        lh.require(parsed['reported_tokens'] == v['reported_tokens'], 'Usage changed')
        used += parsed['reported_tokens'] if parsed['reported_tokens'] is not None else 12500
    return len(started), used


def call(prompt, dest, plan):
    dest.mkdir(parents=True, mode=0o700)
    lh.write(dest / 'request.json', {'prompt': prompt, 'prompt_sha256': lh.digest(prompt.encode()), 'judge': plan['judge'], 'started': time.time()})
    home = dest / 'home'
    ch = home / '.codex'
    ch.mkdir(parents=True, mode=0o700)
    os.chmod(home, 0o700)
    (ch / 'auth.json').symlink_to((Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'auth.json').resolve())
    out = dest / 'answer.txt'
    command = [str(Path(shutil.which('codex')).resolve()), '--no-daemon', 'exec', '--json', '--ephemeral', '--ignore-user-config', '--ignore-rules', '--skip-git-repo-check', '-m', plan['judge']['model'], '-o', str(out)]
    for key, val in {**lh.POLICY, 'sandbox_mode': 'read-only', 'model_reasoning_effort': plan['judge']['effort']}.items():
        command += ['-c', key + '=' + json.dumps(val)]
    command += ['-']
    with tempfile.TemporaryDirectory(prefix='declaude-blind-grade-') as wd:
        try:
            p = subprocess.run(command, input=prompt.encode(), capture_output=True, cwd=wd, env=lh.environment(dest), timeout=900)
            raw, err, code = p.stdout, p.stderr, p.returncode
        except subprocess.TimeoutExpired as e:
            raw, err, code = e.stdout or b'', e.stderr or b'', -1
    lh.write(dest / 'cli.jsonl', raw)
    lh.write(dest / 'stderr.txt', err)
    parsed = lh.parse_cli(raw)
    result = {'cli_sha256': lh.digest(raw), 'exit_code': code, **parsed}
    lh.write(dest / 'result.json', result)
    lh.require(code == 0 and parsed['completed'] and parsed['reported_tokens'] is not None and out.is_file(), 'Judge did not return a usable completed turn; no retry')
    return out.read_text()


def validate(raw, pairs, meta):
    parsed, syntax = parse_batch(raw)
    pairwise.keys(parsed, pairs, 'batch')
    records = []
    for key, source in pairs.items():
        verdict, repairs = repair_evidence(parsed[key], source)
        pairwise.validate_verdict(verdict, source)
        records.append(dict(pair_id=key, **meta[key], **pairwise.normalized(verdict, meta[key]['candidate_position']),
            raw_judgment=verdict, evidence_repairs=repairs, syntax_repairs=syntax,
            source_sha256=pairwise.digest(source)))
    return records


def inputs(checkpoint):
    plan, context, rubric = load()
    # Revalidate every live trajectory and compare the exported rows, without opening a holdout.
    writer, cases = lh.load(PUBLIC / 'plan.json')
    all_rows = lh.collect(writer, PUBLIC / 'plan.json', ROOT / '.local/long-horizon-v9')
    payload = lh.read(checkpoint / 'trajectories.json')
    exported = payload['rows']
    depth = payload['exported_turns_per_trajectory']
    lh.require(exported == [r for r in all_rows if r['turn'] <= depth], 'Export differs from verified trajectories')
    rows = {(r['case'], r['arm'], r['turn']): r for r in exported}
    return plan, context, rubric, {c['id']: c for c in cases}, rows, depth


def run(checkpoint):
    plan, context, rubric, cases, rows, depth = inputs(checkpoint)
    with pairwise.locked(WORK):
        signature = dict(judge_plan=lh.hashed(PUBLIC / 'judge-plan.json'), script=lh.hashed(Path(__file__)), depth=depth,
                         trajectories=lh.hashed(checkpoint / 'trajectories.json'))
        anchor = WORK / 'anchor.json'
        if anchor.exists(): lh.require(lh.read(anchor) == signature, 'Grading inputs/adapter changed')
        else: lh.write(anchor, signature)
        for index, job in enumerate(plan['jobs'], 1):
            dest = WORK / f'job-{index:02d}'
            prompt, pairs, meta = request(job, cases[job['case']], rows, depth, context, rubric)
            if (dest / 'request.json').exists():
                lh.require(lh.read(dest / 'request.json')['prompt'] == prompt, 'Cached prompt changed')
                continue  # Invalid attempts count and are never retried automatically.
            n, used = usage()
            if n >= plan['max_calls'] or used + plan['reservation_tokens'] > plan['token_budget']: break
            raw = call(prompt, dest, plan)
            try:
                accepted = validate(raw, pairs, meta)
                lh.write(dest / 'accepted.json', [dict(case=job['case'], order=job['order'], judge=plan['judge'], **r) for r in accepted])
                print(f'job {index}: ' + ', '.join(r['outcome'] for r in accepted), flush=True)
            except (ValueError, KeyError, TypeError) as e:
                lh.write(dest / 'invalid.json', {'error': str(e)})
                print(f'job {index}: invalid judgment retained; no retry', flush=True)
    report(checkpoint)


def report(checkpoint):
    plan, context, rubric, cases, rows, depth = inputs(checkpoint)
    accepted, missing, answers = [], [], []
    for index, job in enumerate(plan['jobs'], 1):
        d = WORK / f'job-{index:02d}'
        prompt, pairs, meta = request(job, cases[job['case']], rows, depth, context, rubric)
        if not (d / 'accepted.json').exists():
            missing.append({'case': job['case'], 'order': job['order'], 'status': 'invalid' if (d / 'invalid.json').exists() else 'unrun'})
            continue
        lh.require(lh.read(d / 'request.json')['prompt'] == prompt, 'Prompt mismatch')
        raw = (d / 'answer.txt').read_text()
        records = [dict(case=job['case'], order=job['order'], judge=plan['judge'], **r) for r in validate(raw, pairs, meta)]
        lh.require(records == lh.read(d / 'accepted.json'), 'Cached verdict mismatch')
        accepted += records
        answers.append({'case': job['case'], 'order': job['order'], 'prompt': prompt, 'raw_answer': raw})
    n, used = usage()
    out = PUBLIC / 'grades'
    for name, value in [('judgments.json', accepted), ('accepted-answers.json', answers), ('coverage.json', {'calls': n, 'charged_tokens': used, 'depth': depth, 'missing': missing, 'note': 'Reported CLI tokens, with one reservation for any unknown attempt; not billing.'})]:
        lh.public_safe(value)
        lh.write(out / name, value)
    lines = ['# Small revision pilot', '', f'Astra high, two development cases, {depth} of 6 revision turns per trajectory. Sol high judges; no holdout was opened.', '', '| Checkpoint | Wins | Ties | Losses | Net advantage (pp) |', '|---|---:|---:|---:|---:|']
    for turn in dict.fromkeys([1, depth]):
        group = [r for r in accepted if r['order'] == 'primary' and r['turn'] == turn]
        w,t,l = [sum(r['outcome'] == k for r in group) for k in ['win','tie','loss']]
        lines.append(f'| {turn} | {w} | {t} | {l} | {100*(w-l)/len(group):+.1f} |' if group else f'| {turn} | — | — | — | ungraded |')
    lines += ['', 'Ties contribute zero. Two cases cannot establish general performance; these are development results, not OOS. Reversed-order judgments are diagnostics and excluded from the table.', '', '| Case | Turn | Order | Outcome |', '|---|---:|---|---|']
    for r in accepted: lines.append(f'| {r["case"]} | {r["turn"]} | {r["order"]} | {r["outcome"]} |')
    lines += ['', f'Grading: {n}/4 calls; {used:,} charged CLI tokens. Missing/invalid jobs: {len(missing)}. Raw accepted answers and source-verified evidence are saved alongside this report.', '', 'No comparison with v4 was run. A change in this pilot may reflect both the revised core and selective reference loading. Installation decision requires artifact review and the frozen release criteria.']
    (out / 'report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'calls': n, 'charged_tokens': used, 'accepted': len(accepted), 'missing': len(missing)}))

if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('action', choices=['run','report'])
    a.add_argument('--checkpoint', type=Path, required=True)
    args = a.parse_args()
    (run if args.action == 'run' else report)(args.checkpoint.resolve())
