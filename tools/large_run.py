#!/usr/bin/env python3
"""Run the fixed final matrix, grading each dependency group as it finishes.

Selection must already be complete. Only explicitly supplied case files are read;
there is no selection or tuning logic. Repeating the same command delegates cache
validation to bench and pairwise. Do not run other artifact writers in these roots.
Pairwise outputs use <selected>-vs-none/ and, for revisions, <selected>-vs-v4/
under --pairs-out. Selecting v4 runs only none/v4 (20 generations per case).
"""
import argparse
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path

try:
    from . import bench, pairwise
except ImportError:
    import bench
    import pairwise


CONFIGS = tuple(pairwise.DEFAULT_CONFIGS.split(','))
JUDGES = tuple(pairwise.DEFAULT_JUDGES.split(','))
STAGES = ('generation', 'pairwise', 'grading')


def private_directory(root):
    private = root / '.private'
    private.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(private, 0o700)
    pairwise.atomic_write(private / '.gitignore', '*\n')
    return private


@contextmanager
def run_lock(private):
    """Prevent two instances from writing the same run/comparison roots."""
    fd = os.open(private / 'large-run.lock', os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(fd, 'w') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Another large_run process owns this output root') from None
        yield


def load_cases(paths):
    cases, seen = [], set()
    for path in paths:
        data = pairwise.strict_json(path.read_text(encoding='utf-8'))
        batch = data.get('cases') if isinstance(data, dict) else data
        if not isinstance(batch, list) or not batch:
            raise ValueError('Each dataset must contain a nonempty cases list')
        for case in batch:
            pairwise.supplied_case(case)
            case_id = pairwise.component(case['id'])
            if case_id in seen:
                raise ValueError('Duplicate case ID: ' + case_id)
            # bench.grade_pool merges assertion dictionaries into its output.
            if any(not isinstance(item, dict) for item in case.get('assertions', [])):
                raise ValueError('Absolute grading requires assertion objects')
            if 'assertions' not in case:
                raise ValueError('Absolute grading requires case.assertions')
            seen.add(case_id)
            cases.append(case)
    return cases


def check_pool_layout(cases, out, arms):
    """bench grades every response in a case directory; refuse extra pool members.

    This inventory is only a safety check, never evidence that generation finished.
    """
    expected = {f'{config}/{arm}/response.md' for config in CONFIGS for arm in arms}
    for case in cases:
        directory = out / case['id']
        actual = {p.relative_to(directory).as_posix()
                  for p in directory.glob('*/*/response.md')}
        if actual - expected:
            raise ValueError('Unexpected responses in absolute grading pool: ' + case['id'])


def pair_jobs(case, config, args):
    """Match pairwise CLI side/audit hashes and grade_pair arguments exactly."""
    audit = int(pairwise.digest([args.seed, case['id'], config, 'audit']), 16) / 2**256 < 0.2
    jobs = []
    for reference in (('none',) if args.selected == 'v4' else ('none', 'v4')):
        for judge in JUDGES:
            a_side = ('left', 'right')[int(pairwise.digest(
                [args.seed, case['id'], config, judge, 'side']), 16) % 2]
            for reverse in ([False, True] if audit else [False]):
                jobs.append(dict(case=case, judge=judge, config=config,
                                 out=args.pairs_out / (args.selected + '-vs-' + reference),
                                 left_id=reference, right_id=args.selected,
                                 candidate_side='right', seed=args.seed,
                                 reverse=reverse, a_side=a_side))
    jobs.sort(key=lambda job: pairwise.digest([
        args.seed, case['id'], config, job['judge'], job['reverse'], 'queue']))
    return jobs


def grade_ready_pair(runs, job):
    # Executed only after every generation future for this group succeeded.
    left = pairwise.read_response(runs, job['case'], job['config'], job['left_id'])
    right = pairwise.read_response(runs, job['case'], job['config'], job['right_id'])
    return pairwise.grade_pair(lefttext=left, righttext=right, **job)


def error_record(stage, exc, **identity):
    return dict(stage=stage, **identity, error_type=type(exc).__name__, message=str(exc))


def run(cases, bundles, args, private):
    arms = tuple(bundles)
    planned_pairs = {(case['id'], config): pair_jobs(case, config, args)
                     for case in cases for config in CONFIGS}
    totals = dict(generation=len(cases) * len(CONFIGS) * len(arms),
                  pairwise=sum(map(len, planned_pairs.values())), grading=len(cases))
    counts = {stage: dict(total=totals[stage], scheduled=0, completed=0,
                         succeeded=0, failed=0, blocked=0) for stage in STAGES}
    failures, blocked, pending = [], [], {}
    groups_left = {key: len(arms) for key in planned_pairs}
    cases_left = {case['id']: len(CONFIGS) * len(arms) for case in cases}
    failed_groups, failed_cases = set(), set()
    completions, cached = 0, 0

    def save(status):
        pairwise.save_json(private / 'failures.json', dict(
            status=status, selected=args.selected, seed=args.seed,
            case_files=[str(path) for path in args.cases],
            counts=counts, cached_generation=cached, failures=failures, blocked=blocked))

    def progress():
        parts = [f'{stage}={counts[stage]["completed"]}/{totals[stage]}' for stage in STAGES]
        print(' '.join(parts) + f' cached-generation={cached} failed={len(failures)}'
              f' blocked={sum(c["blocked"] for c in counts.values())}', flush=True)

    def submit(pool, stage, identity, function, *positional):
        future = pool.submit(function, *positional)
        pending[future] = (stage, identity)
        counts[stage]['scheduled'] += 1

    save('running')
    with ThreadPoolExecutor(args.generation_workers) as generation, \
            ThreadPoolExecutor(args.pairwise_workers) as pairs, \
            ThreadPoolExecutor(args.grading_workers) as grading:
        try:
            # Case/config/arm keys are unique, including across input files.
            for case in cases:
                for config in CONFIGS:
                    for arm in arms:
                        submit(generation, 'generation', dict(case=case, config=config, arm=arm),
                               bench.run_one, case, config, arm, bundles[arm], args.out)
            while pending:
                finished, _ = wait(pending, return_when=FIRST_COMPLETED)
                for future in finished:
                    stage, identity = pending.pop(future)
                    case = identity['case']
                    case_id = case['id']
                    counts[stage]['completed'] += 1
                    completions += 1
                    try:
                        result = future.result()
                    except Exception as exc:
                        counts[stage]['failed'] += 1
                        details = dict(identity, case=case_id)
                        failures.append(error_record(stage, exc, **details))
                        if stage == 'generation':
                            failed_groups.add((case_id, identity['config']))
                            failed_cases.add(case_id)
                        save('running')
                    else:
                        counts[stage]['succeeded'] += 1
                        if stage == 'generation' and isinstance(result, str) and result.startswith('cached '):
                            cached += 1

                    if stage == 'generation':
                        key = (case_id, identity['config'])
                        groups_left[key] -= 1
                        cases_left[case_id] -= 1
                        if groups_left[key] == 0:
                            jobs = planned_pairs[key]
                            if key in failed_groups:
                                counts['pairwise']['blocked'] += len(jobs)
                                blocked.append(dict(stage='pairwise', case=case_id,
                                                    config=key[1], jobs=len(jobs),
                                                    reason='generation dependency failed'))
                            else:
                                for job in jobs:
                                    identity = dict(case=case, config=key[1], reference=job['left_id'],
                                                    judge=job['judge'], reverse=job['reverse'])
                                    submit(pairs, 'pairwise', identity, grade_ready_pair, args.out, job)
                        if cases_left[case_id] == 0:
                            if case_id in failed_cases:
                                counts['grading']['blocked'] += 1
                                blocked.append(dict(stage='grading', case=case_id, jobs=1,
                                                    reason='generation dependency failed'))
                            else:
                                submit(grading, 'grading', dict(case=case), bench.grade_one,
                                       case, args.out, 'v2')
                    if completions % 10 == 0:
                        progress()
                        save('running')
        except BaseException as exc:
            # Leave already running calls and their artifacts intact. Queued work
            # is cancelled; executor shutdown waits for active writers to finish.
            for future in pending:
                future.cancel()
            failures.append(error_record('scheduler', exc))
            save('interrupted' if isinstance(exc, KeyboardInterrupt) else 'incomplete')
            raise

    complete = all(c['succeeded'] == c['total'] for c in counts.values())
    save('complete' if complete else 'incomplete')
    progress()
    return 0 if complete else 1


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError('Worker counts must be positive')
    return number


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cases', type=Path, nargs='+', required=True)
    ap.add_argument('--selected', choices=('v4', 'v5a', 'v5b'), required=True)
    ap.add_argument('--skill', type=Path, required=True, help='Frozen selected skill directory')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--pairs-out', type=Path, required=True)
    ap.add_argument('--generation-workers', type=positive_int, default=16)
    ap.add_argument('--pairwise-workers', type=positive_int, default=28)
    ap.add_argument('--grading-workers', type=positive_int, default=8)
    ap.add_argument('--seed', default=pairwise.DEFAULT_SEED)
    args = ap.parse_args(argv)
    args.out = args.out.resolve()
    args.pairs_out = args.pairs_out.resolve()
    if args.out == args.pairs_out or args.out in args.pairs_out.parents or args.pairs_out in args.out.parents:
        ap.error('--out and --pairs-out must be separate, non-nested directories')
    try:
        private = private_directory(args.out)
        pairs_private = private_directory(args.pairs_out)
        with run_lock(private), run_lock(pairs_private):
            try:
                # No dataset is opened until --selected has been supplied/validated.
                cases = load_cases(args.cases)
                bundles = {'none': ''}
                if args.selected != 'v4':
                    bundles['v4'] = bench.bundle(bench.ROOT / 'evals/versions/v4')
                bundles[args.selected] = bench.bundle(args.skill)
                check_pool_layout(cases, args.out, bundles)
            except Exception as exc:
                pairwise.save_json(private / 'failures.json', dict(
                    status='incomplete', failures=[error_record('preflight', exc)]))
                print('Preflight failed; details in --out/.private/failures.json', flush=True)
                return 1
            return run(cases, bundles, args, private)
    except KeyboardInterrupt:
        print('Interrupted; partial outputs preserved. Resume with the same command.', flush=True)
        return 130
    except Exception as exc:
        # Avoid printing task/model text from exceptions into a public log, and
        # never overwrite the manifest of a process that holds an output lock.
        print(f'Run could not complete ({type(exc).__name__}); check output locks and '
              '--out/.private/failures.json.', flush=True)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
