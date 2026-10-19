#!/usr/bin/env python3
"""Blinded pairwise grading; all inputs are read-only, all artifacts go under out.

CLI reads bench response.md files. grade_pair() also accepts arbitrary texts for
local calibration. By default left is reference and right is candidate. Each
invocation uses bench.call in a fresh context, never another judge's answer.
Raw answers, prompts, and failures are private (0700 directory, 0600 files,
Git ignore rule); verdicts include unblinding metadata and are not public exports.
"""
import argparse
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile

try:
    from . import bench
except ImportError:
    import bench

VERSION = 'pairwise-v1.1'
MAX_SCHEMA_ATTEMPTS = 4  # Retain every answer and accept the first valid one.
DEFAULT_SEED = 'declaude-pairwise-v1'
DEFAULT_CONFIGS = 'haiku,sonnet-low,sonnet-high,opus-low,opus-xhigh,fable,astra-medium,astra-high,sol-low,luna-medium'
DEFAULT_JUDGES = 'grader-opus,astra-high'
RUBRIC = Path(__file__).resolve().parents[1] / 'evals/graders/pairwise-v1.txt'
DIMENSIONS = ('meaning', 'naturalness', 'progression', 'voice', 'proof', 'overall')


class SchemaError(ValueError):
    """Malformed or inconsistent judge output (the only retryable failure)."""


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def text_hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise SchemaError('Duplicate JSON key: ' + key)
            result[key] = value
        return result

    def invalid(value):
        raise SchemaError('Invalid JSON constant: ' + value)

    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)
    except (ValueError, RecursionError) as exc:
        raise SchemaError(str(exc)) from exc


def parse_answer(raw):
    text = raw.strip()
    fence = re.fullmatch(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    return strict_json(fence[1] if fence else text)


def require(condition, message):
    if not condition:
        raise SchemaError(message)


def keys(value, expected, where):
    require(type(value) is dict and set(value) == set(expected), 'Invalid keys at ' + where)


def nonempty(value, where):
    require(type(value) is str and bool(value.strip()), 'Expected nonempty string at ' + where)


def validate_verdict(verdict, supplied):
    """Validate types, exact quotations, applicability, and severity consistency."""
    keys(verdict, ('is_proof', 'proof_reason', 'material_error_A', 'material_error_B',
                   'material_errors', 'dimensions', 'overall'), 'verdict')
    require(type(verdict['is_proof']) is bool, 'is_proof must be boolean')
    nonempty(verdict['proof_reason'], 'proof_reason')
    if 'is_proof' in supplied:
        require(verdict['is_proof'] == supplied['is_proof'], 'Proof applicability disagrees with task metadata')
    sources = {'source': supplied['task'], **supplied['responses']}

    def evidence(item, required, where):
        nonempty(item['reason'], where + '.reason')
        keys(item['quotes'], sources, where + '.quotes')
        for label, quotes in item['quotes'].items():
            require(type(quotes) is list, 'Quotes must be arrays at ' + where)
            for quote in quotes:
                nonempty(quote, where + '.quote')
                require(quote in sources[label], 'Nonverbatim ' + label + ' quote at ' + where)
            if label in required and sources[label].strip():
                require(bool(quotes), 'Missing ' + label + ' evidence at ' + where)

    keys(verdict['material_errors'], ('A', 'B'), 'material_errors')
    severity = {}
    for label, item in verdict['material_errors'].items():
        keys(item, ('severity', 'reason', 'quotes'), 'material_errors.' + label)
        require(type(item['severity']) is str and item['severity'] in ('none', 'minor', 'major'), 'Invalid severity')
        flag = verdict['material_error_' + label]
        require(type(flag) is bool and flag == (item['severity'] != 'none'), 'Material error flag mismatch')
        evidence(item, ('source', label), 'material_errors.' + label)
        severity[label] = ('none', 'minor', 'major').index(item['severity'])
    keys(verdict['dimensions'], DIMENSIONS, 'dimensions')
    for name, item in verdict['dimensions'].items():
        keys(item, ('preference', 'reason', 'quotes'), name)
        inactive = name == 'proof' and not verdict['is_proof']
        allowed = ('NA',) if inactive else ('A', 'B', 'tie')
        require(type(item['preference']) is str and item['preference'] in allowed, 'Invalid preference for ' + name)
        required = [] if inactive else ['A', 'B']
        if name == 'meaning' or (name == 'proof' and not inactive):
            required.append('source')
        evidence(item, required, name)
    overall = verdict['overall']
    require(type(overall) is str and overall in ('A', 'B', 'tie'), 'Invalid overall preference')
    require(overall == verdict['dimensions']['overall']['preference'], 'Conflicting overall preferences')
    if severity['A'] != severity['B']:
        require(overall == min(severity, key=severity.get), 'Overall must prefer lower material-error severity')
    return verdict


def repair_math_delimiter_quotes(verdict, supplied):
    """Restore one missing dollar delimiter only when the source verifies it.

    This never changes judgments or reasons. Original raw answers remain intact;
    every exact old/new evidence string is recorded in the normalized artifact.
    """
    fixed = copy.deepcopy(verdict)
    repairs = []
    sources = {'source': supplied['task'], **supplied['responses']}
    if not isinstance(fixed, dict): return fixed, repairs
    for section in ('material_errors','dimensions'):
        items = fixed.get(section,{})
        if not isinstance(items,dict): continue
        for name,item in items.items():
            if not isinstance(item,dict) or not isinstance(item.get('quotes'),dict): continue
            for label,quotes in item['quotes'].items():
                if label not in sources or not isinstance(quotes,list): continue
                for index,quote in enumerate(quotes):
                    if not isinstance(quote,str) or quote in sources[label] or '$' not in quote: continue
                    candidates={quote[:i]+'$'+quote[i:] for i in range(len(quote)+1)
                                if quote[:i]+'$'+quote[i:] in sources[label]}
                    if len(candidates)==1:
                        replacement=candidates.pop()
                        quotes[index]=replacement
                        repairs.append(dict(path=[section,name,'quotes',label,index],
                                            old=quote,new=replacement,
                                            operation='restore one source-verified math delimiter'))
    return fixed, repairs


def supplied_case(case):
    """Allowlist task/assertion contents; never serialize the case wholesale."""
    if not isinstance(case, dict) or not isinstance(case.get('task'), str) or not case['task'].strip():
        raise ValueError('case.task must be nonempty text including the source')
    assertions = case.get('assertions', [])
    if not isinstance(assertions, list):
        raise ValueError('case.assertions must be a list')
    cleaned = []
    for item in assertions:
        if isinstance(item, str):
            cleaned.append(item)
        elif isinstance(item, dict) and isinstance(item.get('text'), str):
            assertion = {'text': item['text']}
            if isinstance(item.get('group'), str):
                assertion['group'] = item['group']
            cleaned.append(assertion)
        else:
            raise ValueError('Assertions must be strings or objects with text')
    result = {'task': case['task'], 'assertions': cleaned}
    if 'is_proof' in case:
        if type(case['is_proof']) is not bool:
            raise ValueError('case.is_proof must be boolean when supplied')
        result['is_proof'] = case['is_proof']
    return result


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.tmp-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save_json(path, value):
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


@contextmanager
def locked(directory):
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(directory, 0o700)
    fd = os.open(directory / '.lock', os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(fd, 'w') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def normalized(verdict, candidate_label):
    def outcome(preference):
        if preference in ('tie', 'NA'):
            return preference
        return 'win' if preference == candidate_label else 'loss'
    return {
        'outcome': outcome(verdict['overall']),
        'dimensions': {name: outcome(item['preference']) for name, item in verdict['dimensions'].items()},
        'candidate_material_error': verdict['material_error_' + candidate_label],
        'reference_material_error': verdict['material_error_' + ('B' if candidate_label == 'A' else 'A')],
    }


def grade_pair(case, lefttext, righttext, judge, *, out, config='local',
               left_id='reference', right_id='candidate', candidate_side='right',
               seed=DEFAULT_SEED, reverse=False, a_side=None, rubric=None):
    """Grade/cache one pair with one judge; left/right identities never enter prompt.

    Default ordering is a seeded hash of case/config/judge. CLI passes a_side to
    assign each pair independently, balanced in expectation and stable across subsets. reverse swaps that base ordering for an audit.
    Use a separate out directory per comparison. Results are stored at
    out/case/config/judge/{primary,reversed}.json. raw_judgment is the parsed
    anonymous verdict; exact answer bytes are in the private raw_path.
    rubric is optional full rubric text. case.is_proof can pin applicability;
    otherwise the judge determines it from the task. Returns the complete record.
    Schema failures get at most two total calls per fingerprint, across resumes.
    Transport failures are preserved and raised without an automatic retry.
    """
    if judge not in bench.CONFIGS:
        raise ValueError('Unknown judge: ' + judge)
    if candidate_side not in ('left', 'right') or a_side not in (None, 'left', 'right'):
        raise ValueError('Invalid side')
    if type(reverse) is not bool or any(type(t) is not str for t in (lefttext, righttext)):
        raise ValueError('Texts must be strings and reverse must be boolean')
    supplied = supplied_case(case)
    case_id = str(case.get('id', digest(supplied)))
    if a_side is None:
        a_side = ('left', 'right')[int(digest([str(seed), case_id, config, judge]), 16) % 2]
    base_side = a_side
    if reverse:
        a_side = 'right' if a_side == 'left' else 'left'
    b_side = 'right' if a_side == 'left' else 'left'
    texts = {'left': lefttext, 'right': righttext}
    supplied['responses'] = {'A': texts[a_side], 'B': texts[b_side]}
    rubric = RUBRIC.read_text(encoding='utf-8') if rubric is None else rubric
    if not isinstance(rubric, str) or not rubric.strip():
        raise ValueError('Rubric must be nonempty text')
    prompt = rubric + '\n\nINPUT_JSON:\n' + canonical(supplied)
    provider, model, effort = bench.CONFIGS[judge]
    metadata = dict(case=case_id, config=config, judge=judge, provider=provider,
                    model=model, effort=effort, left_id=left_id, right_id=right_id,
                    candidate_side=candidate_side, seed=str(seed), reverse=reverse,
                    base_a_side=base_side, order={'A': a_side, 'B': b_side})
    request = dict(version=VERSION, rubric=rubric, prompt=prompt,
                   responses=texts, metadata=metadata)
    fingerprint = digest(request)
    out = Path(out)
    private_root = out / '.private'
    private_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(private_root, 0o700)
    atomic_write(private_root / '.gitignore', '*\n')
    private = private_root / fingerprint
    order = 'reversed' if reverse else 'primary'
    dest = out / component(case_id) / component(config) / component(judge) / (order + '.json')
    candidate_label = 'A' if a_side == candidate_side else 'B'

    def record_for(verdict, raw, attempt, repairs):
        identities = {'left': left_id, 'right': right_id}
        reference_side = 'left' if candidate_side == 'right' else 'right'
        payload = dict(version=VERSION, fingerprint=fingerprint, metadata=metadata,
                       case=case_id, config=config, reference=identities[reference_side],
                       candidate=identities[candidate_side], judge=judge, order=order,
                       candidate_position=candidate_label,
                       rubric_sha256=text_hash(rubric), prompt_sha256=text_hash(prompt),
                       response_sha256={k: text_hash(v) for k, v in texts.items()},
                       raw_sha256=text_hash(raw), raw_path=f'.private/{fingerprint}/attempt-{attempt}.txt',
                       attempt=attempt, raw_judgment=verdict, **normalized(verdict, candidate_label))
        if repairs:
            payload['evidence_format_repairs'] = repairs
        return dict(payload, record_sha256=digest(payload))

    with locked(private):
        request_path = private / 'request.json'
        if request_path.exists():
            if strict_json(request_path.read_text(encoding='utf-8')) != request:
                raise RuntimeError('Private request hash mismatch; refusing to overwrite')
        else:
            save_json(request_path, request)
        # Reconstruct from exact raw evidence on resume. Corrupt normalized records
        # are repaired without consuming a call; failed raw attempts stay untouched.
        for attempt in range(1, MAX_SCHEMA_ATTEMPTS + 1):
            raw_path = private / f'attempt-{attempt}.txt'
            status_path = private / f'attempt-{attempt}.json'
            if raw_path.exists():
                raw = raw_path.read_bytes().decode('utf-8')
                status = strict_json(status_path.read_text()) if status_path.exists() else None
                if status and status.get('raw_sha256') != text_hash(raw):
                    raise RuntimeError('Raw answer hash mismatch; refusing to reuse')
            else:
                if status_path.exists():
                    raise RuntimeError('Previous call failed or was interrupted; inspect private attempt status before retrying')
                save_json(status_path, {'state': 'calling'})
                try:
                    raw, call_meta = bench.call(prompt, judge)
                except Exception as exc:
                    save_json(status_path, {'state': 'transport_error', 'error': repr(exc)})
                    raise RuntimeError('Judge call failed; details saved privately') from None
                atomic_write(raw_path, raw)
                save_json(status_path, {'state': 'answered', 'raw_sha256': text_hash(raw), 'call': call_meta})
            try:
                verdict, repairs = repair_math_delimiter_quotes(parse_answer(raw), supplied)
                verdict = validate_verdict(verdict, supplied)
            except SchemaError as exc:
                save_json(private / f'attempt-{attempt}.schema-error.json', {'error': str(exc), 'raw_sha256': text_hash(raw)})
                continue
            record = record_for(verdict, raw, attempt, repairs)
            if dest.exists():
                try:
                    cached = strict_json(dest.read_text(encoding='utf-8'))
                except SchemaError:
                    cached = None
                if cached == record:
                    return cached
            save_json(dest, record)
            return record
        raise SchemaError(f'{MAX_SCHEMA_ATTEMPTS} schema-invalid answers; see private raw attempts')


def csv_names(value):
    result = value.split(',')
    if not all(result) or len(result) != len(set(result)):
        raise ValueError('Names must be nonempty and unique')
    return result


def component(value):
    if not isinstance(value, str) or value in ('', '.', '..') or '/' in value or '\\' in value:
        raise ValueError('Identifiers must be single path components')
    return value


def read_response(runs, case, config, arm):
    path = runs / component(case['id']) / component(config) / component(arm) / 'response.md'
    text = path.read_bytes().decode('utf-8')
    meta = strict_json(path.with_name('meta.json').read_text(encoding='utf-8'))
    expected = {'task_sha256': text_hash(case['task']), 'case': case['id'],
                'config': config, 'arm': arm, 'model': bench.CONFIGS[config][1],
                'effort': bench.CONFIGS[config][2]}
    if not isinstance(meta, dict) or any(meta.get(k) != v for k, v in expected.items()):
        raise ValueError('Stale or mismatched response metadata: ' + str(path))
    return text


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cases', required=True, type=Path)
    ap.add_argument('--runs', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--reference', required=True, choices=('none', 'v4'))
    ap.add_argument('--candidate', required=True)
    ap.add_argument('--configs', default=DEFAULT_CONFIGS)
    ap.add_argument('--judges', default=DEFAULT_JUDGES)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--order-audit', type=float, default=0.2)
    ap.add_argument('--seed', default=DEFAULT_SEED)
    args = ap.parse_args(argv)
    configs, judges = csv_names(args.configs), csv_names(args.judges)
    if any(name not in bench.CONFIGS for name in configs + judges):
        ap.error('Unknown config or judge')
    if len(judges) != 2 or len({bench.CONFIGS[j][0] for j in judges}) != 2:
        ap.error('--judges requires exactly two distinct provider families')
    if args.workers < 1 or not math.isfinite(args.order_audit) or not 0 <= args.order_audit <= 1:
        ap.error('--workers must be positive; --order-audit must be between 0 and 1')
    component(args.candidate)
    if args.candidate == args.reference:
        ap.error('Candidate and reference must differ')
    data = strict_json(args.cases.read_text(encoding='utf-8'))
    cases = data['cases'] if isinstance(data, dict) else data
    if not isinstance(cases, list) or not cases:
        ap.error('Dataset must contain a nonempty cases list')
    ids = [component(c['id']) for c in cases]
    if len(ids) != len(set(ids)):
        ap.error('Duplicate case IDs')
    # Preflight every response before any model call. Candidate artifacts stay intact.
    pairs = []
    for case in cases:
        supplied_case(case)
        for config in configs:
            left = read_response(args.runs, case, config, args.reference)
            right = read_response(args.runs, case, config, args.candidate)
            pairs.append((case, config, left, right))
    jobs = []
    for judge in judges:
        ranked = sorted(pairs, key=lambda p: digest([args.seed, p[0]['id'], p[1], judge, 'balance']))
        for index, (case, config, left, right) in enumerate(ranked):
            audit = int(digest([args.seed, case['id'], config, 'audit']), 16) / 2**256 < args.order_audit
            for reverse in ([False, True] if audit else [False]):
                jobs.append(dict(case=case, lefttext=left, righttext=right, judge=judge,
                                 out=args.out, config=config, left_id=args.reference,
                                 right_id=args.candidate, seed=args.seed, reverse=reverse,
                                 a_side=('left', 'right')[int(digest([args.seed, case['id'], config, judge, 'side']), 16) % 2]))
    # Mix judge families in the execution queue; assignments and cache keys stay fixed.
    jobs.sort(key=lambda job: digest([args.seed, job['case']['id'], job['config'], job['judge'], job['reverse'], 'queue']))
    failures = 0
    with ThreadPoolExecutor(args.workers) as pool:
        futures = {pool.submit(grade_pair, **job): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            label = f"{job['case']['id']}/{job['config']}/{job['judge']}/{'reverse' if job['reverse'] else 'primary'}"
            try:
                result = future.result()
                print(label + ' ' + result['outcome'], flush=True)
            except Exception as exc:
                failures += 1
                print(f'FAILED {label}: {exc}', flush=True)
    if failures:
        raise SystemExit(f'{failures}/{len(jobs)} judgments failed; comparison incomplete')
    print(f'{len(jobs)} judgments complete (including cached records and order audits)', flush=True)


if __name__ == '__main__':
    main()
