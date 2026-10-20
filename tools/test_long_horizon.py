"""Synthetic transport only: these tests cannot start Codex or read real manuscripts."""
import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import long_horizon as lh

TID = '12345678-1234-1234-1234-123456789abc'


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.addCleanup(patch.stopall)
        patch.object(lh, 'ROOT', self.root).start()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        (self.root / '.gitignore').write_text('.local/\n')
        source = self.root / 'evals/versions/v9-dev'
        (source / 'references').mkdir(parents=True)
        (source / 'SKILL.md').write_text('Read references/proofs.md for proof tasks.\n')
        (source / 'references/proofs.md').write_text('Preserve every proof step.\n')
        (source / 'references/secret.local.md').write_text('must never load')
        self.auth = self.root / 'auth'
        self.auth.mkdir()
        (self.auth / 'auth.json').write_text('{}')
        patch.dict(lh.os.environ, {'CODEX_HOME': str(self.auth), 'CODEX_BIN': '/synthetic/codex',
                                  'OPENAI_API_KEY': 'host-secret', 'CODEX_THREAD_ID': 'host-thread'}).start()
        self.case = dict(id='dev-01', category='argument', source_pattern_ids=['pattern-a'],
                         initial_document='Original complete document.\n', initial_request='Revise the argument.',
                         feedback=['Clarify the reasoning.'] * 5,
                         invariants=[dict(id='i1', text='Preserve the claim.', since_turn=1)], is_proof=False)
        self.cases = self.root / 'development.json'
        self.cases.write_text(json.dumps(dict(version=1, split='development', cases=[self.case])))
        self.public = self.root / 'frozen'
        self.plan_path = self.public / 'plan.json'
        self.work = self.root / '.local/run'
        self.calls = []
        self.mode = 'success'
        self.tokens = 100
        self.fake = patch.object(lh, 'execute', side_effect=self.execute).start()
        self.workspaces = []
        original_setup = lh.setup
        def setup(*args):
            result = original_setup(*args)
            self.workspaces.append(Path(result[1]['workspace']))
            return result
        patch.object(lh, 'setup', side_effect=setup).start()
        self.addCleanup(self.clean_workspaces)

    def clean_workspaces(self):
        for p in self.workspaces:
            lh.shutil.rmtree(p, ignore_errors=True)

    def freeze(self, **kwargs):
        return lh.freeze(self.cases, self.public, **kwargs)

    def pilot(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return lh.run(self.plan_path, self.work)

    def execute(self, cmd, prompt, ws, env, timeout, attempt):
        self.calls.append((cmd, prompt, ws, env, timeout))
        self.assertGreater(timeout, 0)
        self.assertNotIn('OPENAI_API_KEY', env)
        self.assertNotIn('CODEX_THREAD_ID', env)
        self.assertNotIn('--ephemeral', cmd)
        self.assertIn('sandbox_mode="workspace-write"', cmd)
        self.assertIn('features.hooks=false', cmd)
        self.assertIn('features.skip_host_skill_discovery=true', cmd)
        self.assertIn('gpt-6-astra', cmd)
        self.assertIn('model_reasoning_effort="high"', cmd)
        home = Path(env['CODEX_HOME'])
        hp = home / 'sessions' / ('rollout-' + TID + '.jsonl')
        hp.parent.mkdir(exist_ok=True)
        tail = []
        if hp.exists():
            self.assertIn('resume', cmd)
            self.assertEqual(cmd[cmd.index('resume') + 1], TID)
        else:
            self.assertNotIn('resume', cmd)
            tail.append(dict(type='session_meta', payload=dict(id=TID, cwd=str(ws))))
        tail += [dict(type='turn_context', payload=dict(model='gpt-6-astra', effort='high')),
                 dict(type='event_msg', payload=dict(type='user_message', message=prompt))]
        cli = [dict(type='thread.started', thread_id=TID), dict(type='turn.started')]
        if self.mode == 'timeout':
            (attempt / 'cli.jsonl').write_text(json.dumps(cli[0]) + '\n')
            (attempt / 'stderr.txt').write_text('timeout')
            raise subprocess.TimeoutExpired(cmd, timeout)
        if self.mode == 'retry_once' and len(self.calls) == 1:
            cli.append(dict(type='turn.failed', error=dict(message='transport connection failed')))
            rc = 1
        elif self.mode == 'model_error':
            cli.append(dict(type='turn.failed', error=dict(message='model unavailable')))
            rc = 1
        else:
            if self.mode == 'missing_document':
                (ws / 'document.md').unlink()
            elif self.mode != 'unchanged':
                (ws / 'document.md').write_text((ws / 'document.md').read_text() + 'A small edit.\n')
            (attempt / 'response.txt').write_text('Revised.\n')
            tail.append(dict(type='event_msg', payload=dict(type='task_complete')))
            if self.mode == 'compaction':
                tail.append(dict(type='compacted', payload=dict(message='summary')))
            cli.append(dict(type='turn.completed', usage=dict(input_tokens=self.tokens, cached_input_tokens=20, output_tokens=10)))
            rc = 0
        with hp.open('a') as f:
            f.write(''.join(json.dumps(e) + '\n' for e in tail))
        (attempt / 'cli.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in cli))
        (attempt / 'stderr.txt').write_text('')
        return rc

    def first_dir(self):
        return self.work / 'trajectories/dev-01/astra-high/none'

    def test_plan_defined_matrix_and_progressive_disclosure(self):
        data = json.loads(self.cases.read_text())
        second = copy.deepcopy(self.case)
        second['id'] = 'dev-02'
        data['cases'].append(second)
        self.cases.write_text(json.dumps(data))
        plan = self.freeze()
        self.assertEqual(len(plan['expected_keys']), 24)
        self.assertEqual(plan['max_calls'], 26)
        self.assertEqual(plan['configs'], lh.CONFIGS)
        self.assertEqual(set(plan['skill_files']), {'SKILL.md', 'references/proofs.md'})
        self.assertEqual(lh.guidance(plan, self.plan_path, 'none'), {})
        g = lh.guidance(plan, self.plan_path, 'v9-dev')
        self.assertEqual(g['AGENTS.md'], b'Read references/proofs.md for proof tasks.\n')
        self.assertNotIn(b'Preserve every', g['AGENTS.md'])

    def test_persistent_sessions_cache_and_public_export(self):
        self.freeze()
        result = self.pilot()
        self.assertTrue(result['complete'])
        self.assertEqual(len(self.calls), 12)
        self.assertEqual(sum('resume' not in c[0] for c in self.calls), 2)
        self.assertEqual(len({str(c[2]) for c in self.calls}), 2)
        self.assertEqual(len({c[3]['HOME'] for c in self.calls}), 2)
        self.assertTrue(self.calls[0][1].startswith('Follow AGENTS.md if present.'))
        self.assertEqual(self.calls[2][1], self.case['feedback'][0])
        base = self.calls[0][2]
        skill = self.calls[1][2]
        self.assertFalse((base / 'AGENTS.md').exists())
        self.assertFalse((base / 'references').exists())
        self.assertTrue((skill / 'references/proofs.md').exists())
        self.pilot()
        self.assertEqual(len(self.calls), 12, 'Saved success must not be regenerated')
        out = self.root / 'export'
        lh.export(self.plan_path, self.work, out)
        public = (out / 'trajectories.json').read_text()
        self.assertNotIn(TID, public)
        self.assertNotIn(str(self.root), public)
        self.assertEqual(len(json.loads(public)['rows']), 12)

    def test_baseline_contamination_fails_before_spend(self):
        self.freeze()
        self.pilot()
        (self.calls[0][2] / 'AGENTS.md').write_text('leaked skill')
        with self.assertRaisesRegex(ValueError, 'contamination'):
            self.pilot()
        self.assertEqual(len(self.calls), 12)

    def test_chain_and_feedback_tampering(self):
        self.freeze()
        self.pilot()
        path = self.first_dir() / 'turns/02/accepted.json'
        saved = lh.read(path)
        saved['row']['previous_chain_sha256'] = 'wrong'
        lh.write(path, saved)
        with self.assertRaisesRegex(ValueError, 'tampering'):
            self.pilot()
        self.assertEqual(len(self.calls), 12)

    def test_live_history_tampering(self):
        self.freeze()
        self.pilot()
        state = lh.read(self.first_dir() / 'session.json')
        with Path(state['history_path']).open('a') as f:
            f.write('{"type":"foreign"}\n')
        with self.assertRaisesRegex(ValueError, 'history changed'):
            self.pilot()
        self.assertEqual(len(self.calls), 12)

    def test_partial_matrix_and_budget_stop(self):
        self.freeze(token_budget=20100, reserve=20000)
        result = self.pilot()
        self.assertEqual(len(self.calls), 1)
        self.assertFalse(result['complete'])
        self.assertEqual(result['reported_tokens'], 110)  # Cached inputs are not added twice.
        with self.assertRaisesRegex(ValueError, 'Incomplete matrix'):
            lh.export(self.plan_path, self.work, self.root / 'export')
        self.assertFalse((self.root / 'export').exists())
        self.pilot()
        self.assertEqual(len(self.calls), 1)

    def test_exact_model_arm_preservation_even_rehashed_plan(self):
        self.freeze()
        plan = lh.read(self.plan_path)
        plan['configs']['astra-high']['model'] = 'gpt-other'
        plan['plan_sha256'] = lh.digest({k: v for k, v in plan.items() if k != 'plan_sha256'})
        lh.write(self.plan_path, plan)
        with self.assertRaisesRegex(ValueError, 'model/effort/arms'):
            self.pilot()
        self.assertFalse(self.calls)

    def test_holdout_path_rejected_before_open(self):
        with self.assertRaisesRegex(ValueError, 'never be opened'):
            lh.freeze(self.root / 'holdout.json', self.public)
        self.assertFalse(self.calls)

    def test_timeout_is_not_replayed(self):
        self.freeze()
        self.mode = 'timeout'
        with self.assertRaises(subprocess.TimeoutExpired):
            self.pilot()
        self.assertEqual(len(self.calls), 1)
        with self.assertRaises(ValueError):
            self.pilot()
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(list(self.work.rglob('error.json')))

    def test_model_errors_and_missing_document_stay_visible(self):
        self.freeze()
        self.mode = 'model_error'
        with self.assertRaisesRegex(ValueError, 'Terminal'):
            self.pilot()
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(list(self.work.rglob('error.json')))
        with self.assertRaises(ValueError):
            self.pilot()
        self.assertEqual(len(self.calls), 1)

    def test_missing_document_no_redraw(self):
        self.freeze()
        self.mode = 'missing_document'
        with self.assertRaises(ValueError):
            self.pilot()
        with self.assertRaises(ValueError):
            self.pilot()
        self.assertEqual(len(self.calls), 1)

    def test_explicit_failed_transport_can_resume_once(self):
        self.freeze()
        self.mode = 'retry_once'
        result = self.pilot()
        self.assertTrue(result['complete'])
        self.assertEqual(len(self.calls), 13)
        self.assertEqual(result['failed_attempts'], 1)
        self.assertIn('resume', self.calls[1][0])
        self.assertEqual(self.calls[0][1], self.calls[1][1])
        self.assertTrue((self.first_dir() / 'turns/01/attempt-1/result.json').exists())

    def test_compaction_reported_and_unchanged_edits_accepted(self):
        self.freeze()
        self.mode = 'compaction'
        result = self.pilot()
        self.assertEqual(result['compaction_events'], 12)

    def test_no_quality_redraw_for_unchanged_document(self):
        self.freeze()
        self.mode = 'unchanged'
        self.assertTrue(self.pilot()['complete'])
        self.assertEqual(len(self.calls), 12)

    def test_changed_reference_invalidates_frozen_cache(self):
        self.freeze()
        (self.public / 'bundles/v9-dev/references/proofs.md').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'Frozen input changed'):
            self.pilot()
        self.assertFalse(self.calls)

    def test_turn_major_checkpoint_smoke_and_partial_export(self):
        data = json.loads(self.cases.read_text())
        second = copy.deepcopy(self.case)
        second['id'] = 'dev-02'
        data['cases'].append(second)
        self.cases.write_text(json.dumps(data))
        self.freeze()
        with contextlib.redirect_stdout(io.StringIO()):
            first = lh.run(self.plan_path, self.work, max_new_calls=1)
            self.assertEqual(first['completed_turns'], 1)
            self.assertEqual(first['deepest_common_completed_turn'], 0)
            result = lh.run(self.plan_path, self.work, max_new_calls=3)
        self.assertEqual(len(self.calls), 4)
        self.assertTrue(all('resume' not in c[0] for c in self.calls))
        self.assertEqual(result['deepest_common_completed_turn'], 1)
        out = self.root / 'checkpoint'
        lh.export(self.plan_path, self.work, out, through_turn=1)
        payload = lh.read(out / 'trajectories.json')
        self.assertEqual(len(payload['rows']), 4)
        self.assertFalse(payload['complete_planned_matrix'])
        with self.assertRaisesRegex(ValueError, 'Incomplete matrix'):
            lh.export(self.plan_path, self.work, self.root / 'bad-checkpoint', through_turn=2)

    def test_parallel_workers_refused(self):
        self.freeze()
        with self.assertRaisesRegex(ValueError, 'sequentially'):
            lh.run(self.plan_path, self.work, workers=2)
        self.assertFalse(self.calls)


if __name__ == '__main__':
    unittest.main()
