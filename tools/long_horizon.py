#!/usr/bin/env python3
"""Persistent, development-only Codex writing pilot. No calls outside `run`.

References are accessible files, never inlined. Token accounting is a soft CLI
usage guard, not a billing cap. Unknown/interrupted outcomes require inspection,
never automatic replay. Only legacy append-only JSONL rollouts are supported;
unknown session storage fails closed. All runtime evidence stays in .local.
"""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = {'astra-high': {'provider': 'codex', 'model': 'gpt-6-astra', 'effort': 'high'}}
COMPARISON = 'v9 with accessible task-relevant references versus no skill'
INTRO = ('Follow AGENTS.md if present. Revise the complete document.md file in place. '
         'On this and every subsequent turn, leave the whole revised document in document.md; '
         'minimal actual edits are fine. Use only this workspace and its supplied references. '
         'Do not read other directories or real manuscripts, use the network, or modify guidance. '
         'Keep the final chat response brief.\n\n')
DISABLED = ('hooks', 'plugins', 'apps', 'memories', 'skill_search',
            'skill_mcp_dependency_install', 'multi_agent', 'multi_agent_v2',
            'browser_use', 'computer_use', 'in_app_browser', 'shell_snapshot',
            'remote_plugin', 'unbounded_connection_retries')
POLICY = {'sandbox_mode': 'workspace-write', 'approval_policy': 'never',
          'web_search': 'disabled', 'sandbox_workspace_write.network_access': False,
          'sandbox_workspace_write.exclude_tmpdir_env_var': True,
          'sandbox_workspace_write.exclude_slash_tmp': True,
          'features.skip_host_skill_discovery': True,
          'shell_environment_policy.inherit': 'none',
          **{'features.' + name: False for name in DISABLED}}
UUID_RE = r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    if not isinstance(value, bytes):
        value = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
    return hashlib.sha256(value).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    data = value if isinstance(value, bytes) else (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()
    tmp = path.with_name(path.name + '.tmp')
    with open(tmp, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    tmp.replace(path)


def hashed(path):
    require(path.is_file() and not path.is_symlink(), 'Missing or symlink artifact: ' + str(path))
    return digest(path.read_bytes())


def public_safe(value):
    text = json.dumps(value, ensure_ascii=False)
    require(not re.search(UUID_RE + r'|/(?:Users|home|private|tmp|var/folders)/|\.local/|Bearer\s+\S+|sk-[\w-]{20,}', text),
            'Private identifiers/paths detected; publication refused')


def safe_input(path):
    require('holdout' not in str(path.resolve()).lower() and 'heldout' not in str(path.resolve()).lower(),
            'Holdout paths must never be opened')
    return path.read_bytes()


def validate_cases(data, turns):
    require(data.get('split') == 'development', 'Only development is accepted')
    require('version' in data and isinstance(data.get('cases'), list) and data['cases'], 'Invalid cases schema')
    ids = []
    for case in data['cases']:
        cid = case['id']
        require(isinstance(cid, str) and re.fullmatch(r'[A-Za-z0-9_-]+', cid), 'Unsafe case id')
        require(case.get('split', 'development') == 'development', 'Nondevelopment case')
        require(isinstance(case['category'], str) and type(case['is_proof']) is bool, 'Invalid case metadata')
        require(isinstance(case['source_pattern_ids'], list) and all(isinstance(x, str) for x in case['source_pattern_ids']), 'Invalid source ids')
        require(all(isinstance(case[x], str) and case[x].strip() for x in ('initial_document', 'initial_request')), 'Missing initial text')
        require(isinstance(case['feedback'], list) and len(case['feedback']) == turns - 1 and
                all(isinstance(x, str) and x.strip() for x in case['feedback']), 'Wrong fixed feedback count')
        require(isinstance(case['invariants'], list), 'Invalid invariants')
        for inv in case['invariants']:
            require(isinstance(inv['id'], str) and isinstance(inv['text'], str) and
                    type(inv['since_turn']) is int and 0 <= inv['since_turn'] <= turns, 'Invalid invariant')
        ids.append(cid)
    require(len(set(ids)) == len(ids), 'Duplicate cases')


def expected_keys(cases, configs, arms, turns):
    return [f'{c["id"]}/{cfg}/{arm}/{t:02d}' for c in cases for cfg in configs for arm in arms for t in range(1, turns + 1)]


def freeze(cases_path, out, turns=6, token_budget=250000, reserve=20000, timeout=1500):
    raw = safe_input(cases_path)
    cases = json.loads(raw)
    validate_cases(cases, turns)
    require(1 <= turns <= 8 and 0 < reserve <= token_budget <= 250000 and 0 < timeout <= 3600,
            'Invalid turn/budget/timeout limits')
    arms = ['none', 'v9-dev']
    keys = expected_keys(cases['cases'], CONFIGS, arms, turns)
    require(len(keys) <= 24, 'Pilot is limited to 24 planned writing turns')
    source = ROOT / 'evals/versions/v9-dev'
    paths = [source / 'SKILL.md'] + sorted((source / 'references').rglob('*'))
    files = {}
    for p in paths:
        require(not p.is_symlink(), 'Symlink guidance is forbidden')
        if p.is_file() and not p.name.endswith('.local.md'):
            require(p.suffix == '.md', 'Portable guidance must be Markdown')
            files[str(p.relative_to(source))] = p.read_bytes()
    require('SKILL.md' in files and files['SKILL.md'].strip(), 'Candidate SKILL.md missing')
    payloads = {'cases.json': raw, **{'bundles/v9-dev/' + k: v for k, v in files.items()}}
    plan = dict(schema='long-horizon-v1', phase='development', split='development', turns=turns,
                configs=CONFIGS, arms=arms, expected_keys=keys, max_writer_turns=len(keys),
                max_attempts_per_turn=2, max_transport_extras=2, max_calls=len(keys) + 2,
                token_budget=token_budget, reservation_tokens=reserve, timeout_seconds=timeout,
                comparison=COMPARISON, packing='AGENTS.md = exact SKILL.md bytes; portable references beside it',
                scheduling='turn-major',
                introduction=INTRO, policy=POLICY,
                files={k: digest(v) for k, v in payloads.items()},
                skill_files={k: digest(v) for k, v in files.items()},
                bundle_sha256=digest({k: digest(v) for k, v in files.items()}),
                runner_sha256=hashed(Path(__file__)))
    plan['plan_sha256'] = digest(plan)
    public_safe(plan)
    for value in payloads.values():
        public_safe(value.decode('utf-8'))
    require(not out.exists(), 'Freeze destination already exists')
    out.mkdir(parents=True)
    for name, value in payloads.items():
        write(out / name, value)
    write(out / 'plan.json', plan)
    return plan


def load(plan_path):
    plan = json.loads(safe_input(plan_path))
    require(plan['plan_sha256'] == digest({k: v for k, v in plan.items() if k != 'plan_sha256'}), 'Plan hash changed')
    require(plan['phase'] == plan['split'] == 'development', 'Only development plans accepted')
    require(plan['schema'] == 'long-horizon-v1' and plan['configs'] == CONFIGS and
            plan['arms'] == ['none', 'v9-dev'], 'Frozen model/effort/arms changed')
    require(plan['introduction'] == INTRO and plan['policy'] == POLICY and plan['comparison'] == COMPARISON and plan['scheduling'] == 'turn-major',
            'Frozen execution policy changed')
    require(plan['runner_sha256'] == hashed(Path(__file__)), 'Runner changed after freeze; do not reuse its cache')
    require(1 <= plan['turns'] <= 8 and plan['max_attempts_per_turn'] == 2 and plan['max_transport_extras'] == 2,
            'Frozen limits changed')
    require(0 < plan['reservation_tokens'] <= plan['token_budget'] <= 250000 and
            0 < plan['timeout_seconds'] <= 3600, 'Invalid budget/time limit')
    names = {'cases.json'} | {'bundles/v9-dev/' + k for k in plan['skill_files']}
    require(set(plan['files']) == names and 'SKILL.md' in plan['skill_files'], 'Frozen guidance manifest changed')
    for name, sha in plan['files'].items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts and not name.endswith('.local.md'), 'Unsafe frozen filename')
        require(hashed(plan_path.parent / name) == sha, 'Frozen input changed: ' + name)
    require(plan['bundle_sha256'] == digest(plan['skill_files']) and
            all(plan['files']['bundles/v9-dev/' + k] == v for k, v in plan['skill_files'].items()), 'Bundle hash changed')
    data = read(plan_path.parent / 'cases.json')
    validate_cases(data, plan['turns'])
    keys = expected_keys(data['cases'], plan['configs'], plan['arms'], plan['turns'])
    require(keys == plan['expected_keys'] and len(keys) == plan['max_writer_turns'] <= 24 and
            plan['max_calls'] == len(keys) + 2, 'Frozen matrix/call cap changed')
    return plan, data['cases']


@contextmanager
def locked(work):
    resolved = work.resolve()
    require('.local' in resolved.parts and resolved.is_relative_to(ROOT.resolve() / '.local'), 'Private work must be under this repository .local')
    require(not work.is_symlink(), 'Symlink work directory forbidden')
    work.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(work, 0o700)
    # Existing repository ignore rule is a prerequisite, never silently modify it.
    ignored = subprocess.run(['git', 'check-ignore', '-q', str(work / 'privacy-probe')], cwd=ROOT)
    require(ignored.returncode == 0, '.local runtime is not ignored by Git')
    with open(work / 'runner.lock', 'a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def anchor(plan, work):
    expected = {'plan_sha256': plan['plan_sha256']}
    path = work / 'manifest.json'
    if path.exists():
        require(read(path) == expected, 'Private manifest differs from frozen plan')
    else:
        require(not any(work.glob('trajectories/*')), 'Orphan runtime without manifest')
        write(path, expected)


def guidance(plan, plan_path, arm):
    if arm == 'none':
        return {}
    return {('AGENTS.md' if name == 'SKILL.md' else name):
            (plan_path.parent / 'bundles' / arm / name).read_bytes() for name in plan['skill_files']}


def check_workspace(ws, guide):
    require(ws.is_dir() and not ws.is_symlink(), 'Session workspace missing/symlinked')
    for parent in ws.parents:
        require(not any((parent / n).exists() for n in ('AGENTS.md', 'AGENTS.override.md', '.codex', '.agents')),
                'Ancestor guidance contamination: ' + str(parent))
    actual = {str(p.relative_to(ws)) for p in ws.rglob('*') if p.is_file()}
    require(actual == {'document.md'} | set(guide), 'Unexpected workspace files or baseline guidance contamination')
    allowed_dirs = {str(parent) for name in guide for parent in Path(name).parents if str(parent) != '.'}
    require({str(p.relative_to(ws)) for p in ws.rglob('*') if p.is_dir()} == allowed_dirs,
            'Unexpected workspace directories or baseline references contamination')
    require(not any(p.is_symlink() for p in ws.rglob('*')), 'Workspace symlink detected')
    for name, data in guide.items():
        require((ws / name).read_bytes() == data, 'Workspace guidance changed')
    require((ws / 'document.md').read_bytes().strip(), 'No document artifact')


def setup(plan, plan_path, work, case, cfg, arm):
    d = work / 'trajectories' / case['id'] / cfg / arm
    state_path = d / 'session.json'
    identity = dict(plan_sha256=plan['plan_sha256'], case=case['id'], config=cfg, arm=arm)
    if state_path.exists():
        state = read(state_path)
        require(state['identity'] == identity, 'Session identity changed')
        return d, state
    require(not d.exists(), 'Orphan trajectory; inspect manually')
    d.mkdir(parents=True, mode=0o700)
    home = d / 'home'
    ch = home / '.codex'
    ch.mkdir(parents=True, mode=0o700)
    os.chmod(home, 0o700)
    auth = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'auth.json'
    require(auth.is_file(), 'Codex auth.json missing')
    (ch / 'auth.json').symlink_to(auth.resolve())
    ws = Path(tempfile.mkdtemp(prefix='declaude-long-horizon-')).resolve()
    os.chmod(ws, 0o700)
    write(ws / 'document.md', case['initial_document'].encode())
    for name, data in guidance(plan, plan_path, arm).items():
        write(ws / name, data)
    state = dict(identity=identity, workspace=str(ws), thread_id=None, history_path=None,
                 history_sha256=None, history_size=0)
    check_workspace(ws, guidance(plan, plan_path, arm))
    write(state_path, state)
    return d, state


def environment(d):
    home = (d / 'home').resolve()
    # Deliberately do not forward host config, agent, API, proxy, shell startup or skill variables.
    return {'HOME': str(home), 'CODEX_HOME': str(home / '.codex'),
            'XDG_CONFIG_HOME': str(home / '.config'), 'XDG_CACHE_HOME': str(home / '.cache'),
            'XDG_DATA_HOME': str(home / '.local/share'), 'ZDOTDIR': str(home),
            'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'LANG': 'en_US.UTF-8'}


def command(plan, cfg, state, output):
    binary = os.environ.get('CODEX_BIN') or shutil.which('codex')
    require(binary is not None, 'codex executable missing')
    cmd = [str(Path(binary).resolve()), '--no-daemon', 'exec']
    if state['thread_id']:
        cmd += ['resume', state['thread_id']]
    cmd += ['--json', '--skip-git-repo-check', '--ignore-user-config', '--ignore-rules',
            '-m', plan['configs'][cfg]['model'], '-o', str(output)]
    options = {**plan['policy'], 'model_reasoning_effort': plan['configs'][cfg]['effort'],
               'project_doc_max_bytes': 131072}
    for key, value in options.items():
        cmd += ['-c', key + '=' + json.dumps(value)]
    return cmd + ['-']


def events(data):
    return [json.loads(line) for line in data.splitlines() if line.strip()]


def parse_cli(data):
    rows = events(data)
    completed = [r for r in rows if r.get('type') == 'turn.completed']
    failed = [r for r in rows if r.get('type') in ('turn.failed', 'error')]
    ids = {r['thread_id'] for r in rows if r.get('type') == 'thread.started'}
    require(len(ids) <= 1, 'Multiple CLI thread identities')
    tid = next(iter(ids), None)
    if tid:
        require(str(uuid.UUID(tid)) == tid.lower(), 'Invalid thread UUID')
    require(len(completed) <= 1, 'More than one completed turn in one invocation')
    usage = completed[0].get('usage', {}) if completed else {}
    usage = {k: v for k, v in usage.items() if k in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'total_tokens')}
    require(all(type(v) is int and v >= 0 for v in usage.values()), 'Invalid usage')
    total = usage.get('total_tokens')
    if total is None and 'input_tokens' in usage and 'output_tokens' in usage:
        total = usage['input_tokens'] + usage['output_tokens']
    return dict(completed=bool(completed), failed=failed, thread_id=tid, usage=usage, reported_tokens=total)


def compactions(rows):
    return sum(1 for r in rows if any('compact' in str(x).lower() for x in
               (r.get('type', ''), r.get('payload', {}).get('type', ''), r.get('item', {}).get('type', ''))))


def verify_delta(raw, prompt, completed):
    rows = events(raw)
    messages = [r['payload']['message'] for r in rows if r.get('type') == 'event_msg' and
                r.get('payload', {}).get('type') == 'user_message']
    require(messages == [prompt], 'Session transcript does not contain exactly the submitted user request')
    ended = sum(r.get('type') == 'event_msg' and r.get('payload', {}).get('type') in
                ('task_complete', 'turn_complete') for r in rows)
    require(ended == int(completed), 'CLI and persistent transcript disagree on turn completion')
    require(any(r.get('type') == 'turn_context' for r in rows), 'Missing persistent turn context')


def history(d, state):
    if not state['thread_id']:
        require(not list((d / 'home/.codex/sessions').rglob('*.jsonl')), 'Unidentified persistent session')
        return None, b''
    paths = list((d / 'home/.codex/sessions').rglob('*' + state['thread_id'] + '*.jsonl'))
    require(len(paths) == 1, 'Persistent JSONL session not uniquely found; unsupported storage or missing history')
    p = paths[0]
    raw = p.read_bytes()
    rows = events(raw)
    metas = [r['payload'] for r in rows if r.get('type') == 'session_meta']
    require(len(metas) == 1 and metas[0]['id'] == state['thread_id'] and
            Path(metas[0]['cwd']).resolve() == Path(state['workspace']).resolve(), 'Session history identity/cwd mismatch')
    for row in rows:
        if row.get('type') == 'turn_context':
            context = row['payload']
            require(context.get('model') == CONFIGS[state['identity']['config']]['model'] and
                    context.get('effort', context.get('reasoning_effort')) == CONFIGS[state['identity']['config']]['effort'],
                    'Session history model/effort mismatch')
    return p, raw


def verify_live(d, state):
    ch = d / 'home/.codex'
    require((ch / 'auth.json').is_symlink(), 'Auth isolation changed')
    for base in (d / 'home', ch):
        require(base.stat().st_mode & 0o077 == 0, 'Private HOME permissions too broad')
    for base in (d / 'home', ch, d / 'home/.config'):
        for name in ('AGENTS.md', 'AGENTS.override.md', 'skills', 'hooks.json', 'config.toml', '.agents'):
            require(not (base / name).exists(), 'HOME guidance/config contamination')
    p, raw = history(d, state)
    require(len(raw) == state['history_size'] and (digest(raw) if raw else None) == state['history_sha256'],
            'Live session history changed outside the runner')
    if p:
        require(str(p) == state['history_path'], 'Session path changed')
    return raw


def budget(plan, work):
    started = list(work.glob('trajectories/*/*/*/turns/*/attempt-*/request.json'))
    total = unknown = failures = 0
    for request in started:
        result = request.with_name('result.json')
        require(result.exists(), 'Ambiguous unfinished attempt; no further calls allowed')
        value = read(result)
        cli = request.with_name('cli.jsonl')
        require(hashed(cli) == value['cli_sha256'], 'Attempt CLI changed')
        parsed = parse_cli(cli.read_bytes())
        require(parsed['reported_tokens'] == value['reported_tokens'] and parsed['usage'] == value['usage'], 'Attempt usage changed')
        if value['reported_tokens'] is None:
            unknown += 1
        else:
            total += value['reported_tokens']
        failures += value['status'] != 'completed'
    charged = total + unknown * plan['reservation_tokens']
    return dict(calls=len(started), failed_attempts=failures, reported_tokens=total,
                unreported_attempts=unknown, charged_tokens=charged,
                remaining_tokens=plan['token_budget'] - charged,
                can_call=len(started) < plan['max_calls'] and failures <= plan['max_transport_extras'] and
                charged + plan['reservation_tokens'] <= plan['token_budget'],
                accounting='soft CLI token guard; unknown failed usage charged one reservation, not a billing cap')


def request_for(plan, case, turn):
    feedback = case['initial_request'] if turn == 1 else case['feedback'][turn - 2]
    return feedback, (plan['introduction'] if turn == 1 else '') + feedback


def row_for(plan, case, cfg, arm, turn, previous, doc, response, parsed, compact):
    feedback, prompt = request_for(plan, case, turn)
    row = dict(key=f'{case["id"]}/{cfg}/{arm}/{turn:02d}', case=case['id'], config=cfg, arm=arm,
               turn=turn, phase='development', category=case['category'], is_proof=case['is_proof'],
               plan_sha256=plan['plan_sha256'], bundle_sha256=None if arm == 'none' else plan['bundle_sha256'],
               input_sha256=digest(case), previous_chain_sha256=previous,
               document_sha256=digest(doc), document=doc.decode('utf-8'),
               response_sha256=digest(response), response=response.decode('utf-8'),
               feedback=feedback, feedback_sha256=digest(feedback.encode()), prompt_sha256=digest(prompt.encode()),
               **plan['configs'][cfg], usage=parsed['usage'], reported_tokens=parsed['reported_tokens'],
               compaction_events=compact)
    row['chain_sha256'] = digest(row)
    return row


def initial_chain(plan, case, cfg, arm):
    return digest([plan['plan_sha256'], case, cfg, arm, digest(case['initial_document'].encode())])


def validate_trajectory(plan, plan_path, d, case, cfg, arm):
    state = read(d / 'session.json')
    require(state['identity'] == dict(plan_sha256=plan['plan_sha256'], case=case['id'], config=cfg, arm=arm), 'Trajectory identity mismatch')
    check_workspace(Path(state['workspace']), guidance(plan, plan_path, arm))
    live = verify_live(d, state)
    previous = initial_chain(plan, case, cfg, arm)
    rows, prior_history = [], b''
    last_doc = case['initial_document'].encode()
    incomplete = False
    for turn in range(1, plan['turns'] + 1):
        td = d / 'turns' / f'{turn:02d}'
        accepted = td / 'accepted.json'
        if not accepted.exists():
            incomplete = True
            # An interrupted or terminal failed attempt is never hidden by skipping it.
            for a in sorted(td.glob('attempt-*')):
                require((a / 'result.json').exists() and read(a / 'result.json')['status'] == 'retryable',
                        'Unaccepted/ambiguous attempt; inspect privately, do not replay')
            continue
        require(not incomplete, 'Completed turn after a missing turn')
        saved = read(accepted)
        chosen = saved['attempt']
        require(1 <= chosen <= 2, 'Invalid accepted attempt')
        attempts = sorted(td.glob('attempt-*'))
        require(len(attempts) == chosen, 'Extra or missing transport attempts')
        for number, a in enumerate(attempts, 1):
            result = read(a / 'result.json')
            require(result['status'] == ('completed' if number == chosen else 'retryable'), 'Earlier success discarded')
            for filename, sha in result['artifacts'].items():
                require('/' not in filename and hashed(a / filename) == sha, 'Attempt artifact tampering')
            req = read(a / 'request.json')
            require(req['prompt'] == request_for(plan, case, turn)[1] and req['previous_chain_sha256'] == previous and
                    req['plan_sha256'] == plan['plan_sha256'] and req['config'] == cfg and req['arm'] == arm,
                    'Attempt request/config/history changed')
            snap = (a / 'history.jsonl').read_bytes()
            require(snap.startswith(prior_history), 'Session history truncated or rewritten')
            verify_delta(snap[len(prior_history):], req['prompt'], number == chosen)
            prior_history = snap
        a = td / f'attempt-{chosen}'
        parsed = parse_cli((a / 'cli.jsonl').read_bytes())
        require(parsed['completed'] and not parsed['failed'] and parsed['thread_id'] == state['thread_id'], 'Saved CLI is not a successful same-thread turn')
        doc, response = (a / 'document.md').read_bytes(), (a / 'response.txt').read_bytes()
        require(doc.strip(), 'No document artifact')
        expected = row_for(plan, case, cfg, arm, turn, previous, doc, response, parsed, read(a / 'result.json')['compaction_events'])
        require(saved['row'] == expected, 'Snapshot chain/feedback/config tampering')
        previous, last_doc = expected['chain_sha256'], doc
        rows.append(expected)
    require(live.startswith(prior_history), 'Live history no longer contains accepted turns')
    require((Path(state['workspace']) / 'document.md').read_bytes() == last_doc, 'Live document differs from last valid snapshot')
    return rows, state


def execute(cmd, prompt, ws, env, timeout, attempt):
    """Stream raw outputs to disk so a killed coordinator leaves evidence."""
    with open(attempt / 'cli.jsonl', 'wb') as stdout, open(attempt / 'stderr.txt', 'wb') as stderr:
        result = subprocess.run(cmd, input=prompt.encode(), cwd=ws, env=env, stdout=stdout,
                                stderr=stderr, timeout=timeout)
    return result.returncode


def run_turn(plan, plan_path, work, d, state, case, cfg, arm, turn, previous, call_limit=None):
    ws = Path(state['workspace'])
    td = d / 'turns' / f'{turn:02d}'
    for number in range(1, 3):
        a = td / f'attempt-{number}'
        if a.exists():
            require((a / 'result.json').exists() and read(a / 'result.json')['status'] == 'retryable', 'Do not retry saved success/ambiguous attempt')
            continue
        tally = budget(plan, work)
        if not tally['can_call'] or (call_limit is not None and tally['calls'] >= call_limit):
            return False
        before = verify_live(d, state)
        check_workspace(ws, guidance(plan, plan_path, arm))
        original = (ws / 'document.md').read_bytes()
        feedback, prompt = request_for(plan, case, turn)
        a.mkdir(parents=True, mode=0o700)
        cmd = command(plan, cfg, state, a / 'response.txt')
        write(a / 'request.json', dict(prompt=prompt, plan_sha256=plan['plan_sha256'], config=cfg, arm=arm,
                                      previous_chain_sha256=previous, command=cmd, started=time.time()))
        try:
            rc = execute(cmd, prompt, ws, environment(d), plan['timeout_seconds'], a)
            if (ws / 'document.md').is_file():
                write(a / 'document.md', (ws / 'document.md').read_bytes())
            parsed = parse_cli((a / 'cli.jsonl').read_bytes())
            if parsed['thread_id']:
                require(state['thread_id'] in (None, parsed['thread_id']), 'Resume switched thread')
                state['thread_id'] = parsed['thread_id']
            hp, raw = history(d, state)
            require(raw.startswith(before), 'Session history rewritten during turn')
            write(a / 'history.jsonl', raw)
            verify_delta(raw[len(before):], prompt, parsed['completed'])
            state.update(history_path=str(hp) if hp else None, history_sha256=digest(raw) if raw else None, history_size=len(raw))
            write(d / 'session.json', state)
            # Snapshot exact bytes even for failed turns; missing artifacts remain errors.
            if (ws / 'document.md').is_file():
                write(a / 'document.md', (ws / 'document.md').read_bytes())
            if not (a / 'response.txt').exists():
                write(a / 'response.txt', b'')
            check_workspace(ws, guidance(plan, plan_path, arm))
            compact = compactions(events(raw[len(before):]))
            cli_compact = compactions(events((a / 'cli.jsonl').read_bytes()))
            # Only an explicit terminal transport failure with unchanged document is retryable.
            errors = json.dumps(parsed['failed']).lower()
            retryable = (not parsed['completed'] and any(r.get('type') == 'turn.failed' for r in parsed['failed']) and
                         re.search(r'transport|connection|stream disconnect|network|timed out', errors) is not None and
                         (ws / 'document.md').read_bytes() == original)
            ok = rc == 0 and parsed['completed'] and not parsed['failed'] and parsed['thread_id'] and raw
            status = 'completed' if ok else 'retryable' if retryable else 'error'
            result = dict(status=status, returncode=rc, **parsed, compaction_events=compact,
                          cli_compaction_events=cli_compact,
                          cli_sha256=hashed(a / 'cli.jsonl'),
                          artifacts={p.name: hashed(p) for p in a.iterdir() if p.is_file()})
            write(a / 'result.json', result)
            if ok:
                require(parsed['reported_tokens'] is not None, 'Successful turn has no reported usage; stop without replay')
                row = row_for(plan, case, cfg, arm, turn, previous, (a / 'document.md').read_bytes(),
                              (a / 'response.txt').read_bytes(), parsed, compact)
                write(td / 'accepted.json', dict(attempt=number, row=row))
                return True
            require(retryable and number < 2 and tally['failed_attempts'] < plan['max_transport_extras'],
                    'Terminal model/transport error; trajectory stopped')
        except BaseException as exc:
            if (ws / 'document.md').is_file() and not (ws / 'document.md').is_symlink():
                write(a / 'document.md', (ws / 'document.md').read_bytes())
            write(a / 'error.json', dict(error=repr(exc), outcome='stop; never automatically replay an ambiguous turn'))
            raise
    raise ValueError('Transport attempts exhausted')


def collect(plan, plan_path, work):
    require(read(work / 'manifest.json') == {'plan_sha256': plan['plan_sha256']}, 'Private manifest mismatch')
    _, cases = load(plan_path)
    rows = []
    expected_dirs = {work / 'trajectories' / c['id'] / cfg / arm for c in cases for cfg in plan['configs'] for arm in plan['arms']}
    require(set(work.glob('trajectories/*/*/*')) <= expected_dirs, 'Unexpected trajectory outside matrix')
    for c in cases:
        for cfg in plan['configs']:
            for arm in plan['arms']:
                d = work / 'trajectories' / c['id'] / cfg / arm
                if d.exists():
                    validated, _ = validate_trajectory(plan, plan_path, d, c, cfg, arm)
                    rows.extend(validated)
    return rows


def run(plan_path, work, workers=1, max_new_calls=None):
    require(workers == 1, 'Pilot runs sequentially to limit token overshoot; workers must be 1')
    plan, cases = load(plan_path)
    require(max_new_calls is None or max_new_calls > 0, 'max-new-calls must be positive')
    old_mask = os.umask(0o077)
    try:
        with locked(work):
            anchor(plan, work)
            collect(plan, plan_path, work)  # Validate ALL caches before spending anything.
            call_limit = None if max_new_calls is None else budget(plan, work)['calls'] + max_new_calls
            for turn in range(1, plan['turns'] + 1):
                for c in cases:
                    for cfg in plan['configs']:
                        for arm in plan['arms']:
                            if not budget(plan, work)['can_call'] or (call_limit is not None and budget(plan, work)['calls'] >= call_limit):
                                return status(plan_path, work)
                            d, state = setup(plan, plan_path, work, c, cfg, arm)
                            rows, state = validate_trajectory(plan, plan_path, d, c, cfg, arm)
                            if len(rows) >= turn:
                                continue
                            require(len(rows) == turn - 1, 'Missing prior round')
                            previous = rows[-1]['chain_sha256'] if rows else initial_chain(plan, c, cfg, arm)
                            if not run_turn(plan, plan_path, work, d, state, c, cfg, arm, turn, previous, call_limit):
                                return status(plan_path, work)
                            print(f'{c["id"]}/{cfg}/{arm}/{turn:02d}', 'saved', flush=True)
            return status(plan_path, work)
    except BaseException as exc:
        if work.exists():
            write(work / 'stopped.json', dict(error=repr(exc), at=time.time()))
        raise
    finally:
        os.umask(old_mask)


def status(plan_path, work):
    plan, cases = load(plan_path)
    rows = collect(plan, plan_path, work)
    common = min(sum(r['case'] == c['id'] and r['config'] == cfg and r['arm'] == arm for r in rows)
                 for c in cases for cfg in plan['configs'] for arm in plan['arms'])
    value = dict(phase='development', completed_turns=len(rows), expected_turns=len(plan['expected_keys']),
                 deepest_common_completed_turn=common, planned_turns_per_trajectory=plan['turns'],
                 complete=len(rows) == len(plan['expected_keys']), compaction_events=sum(r['compaction_events'] for r in rows),
                 **budget(plan, work))
    write(work / 'status.json', value)
    return value


def export(plan_path, work, out, through_turn=None):
    plan, _ = load(plan_path)
    with locked(work):
        rows = collect(plan, plan_path, work)
        depth = plan['turns'] if through_turn is None else through_turn
        require(1 <= depth <= plan['turns'], 'Invalid export depth')
        rows = [r for r in rows if r['turn'] <= depth]
        wanted = [k for k in plan['expected_keys'] if int(k.rsplit('/', 1)[1]) <= depth]
        require([r['key'] for r in rows] == wanted, 'Incomplete matrix; public export refused')
        tally = budget(plan, work)
        require(tally['calls'] <= plan['max_calls'] and tally['failed_attempts'] <= 2, 'Call cap exceeded')
        payload = dict(plan_sha256=plan['plan_sha256'], phase='development', comparison=plan['comparison'],
                       exported_turns_per_trajectory=depth, planned_turns_per_trajectory=plan['turns'],
                       complete_planned_matrix=depth == plan['turns'],
                       rows=rows, usage=tally, compaction_events=sum(r['compaction_events'] for r in rows))
        public_safe(payload)
        require(not (out / 'trajectories.json').exists(), 'Public output already exists')
        write(out / 'trajectories.json', payload)
    return dict(exported_turns=len(rows), phase='development')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='action', required=True)
    f = sub.add_parser('freeze')
    f.add_argument('--cases', required=True, type=Path)
    f.add_argument('--out', required=True, type=Path)
    f.add_argument('--turns', type=int, default=6)
    f.add_argument('--token-budget', type=int, default=250000)
    f.add_argument('--reserve', type=int, default=20000)
    f.add_argument('--timeout', type=int, default=1500)
    for name in ('run', 'status', 'export'):
        p = sub.add_parser(name)
        p.add_argument('--plan', required=True, type=Path)
        p.add_argument('--work', required=True, type=Path)
        if name == 'run':
            p.add_argument('--workers', type=int, default=1)
            p.add_argument('--max-new-calls', type=int, help='Bounded smoke/checkpoint in the same private usage ledger')
        if name == 'export':
            p.add_argument('--out', required=True, type=Path)
            p.add_argument('--through-turn', type=int, help='Explicit partial export; requires every trajectory through this turn')
    a = ap.parse_args()
    if a.action == 'freeze':
        result = freeze(a.cases, a.out, a.turns, a.token_budget, a.reserve, a.timeout)
        print(json.dumps({'plan_sha256': result['plan_sha256'], 'expected_turns': len(result['expected_keys'])}))
    else:
        args = [a.plan.resolve(), a.work.resolve()]
        if a.action == 'run':
            result = run(*args, a.workers, a.max_new_calls)
        elif a.action == 'export':
            result = export(*args, a.out.resolve(), a.through_turn)
        else:
            result = status(*args)
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
