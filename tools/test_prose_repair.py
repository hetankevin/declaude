"""Synthetic-only runner checks. Never read holdout cases or invoke a model."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import bench
import pairwise
import prose_repair as run


class RepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(run, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.addCleanup(patch.stopall)
        patch.object(bench, 'grade_one', side_effect=AssertionError('Absolute grading forbidden')).start()
        patch.object(bench, 'grade_pool', side_effect=AssertionError('Pool grading forbidden')).start()
        patch.object(run.context, 'inputs', side_effect=AssertionError('Holdout loader forbidden')).start()
        self.call = patch.object(bench, 'call', side_effect=self.fake_call).start()
        for folder in ('skill', 'evals/versions/v4', 'evals/versions/v8-dev'):
            self.write(folder+'/SKILL.md', 'Synthetic editing guidance.')
            self.write(folder+'/references/proofs.md', 'Keep every proof step.\n')
        for name in ('prose_repair.py', 'bench.py', 'context_regrade.py', 'pairwise.py'):
            self.write('tools/'+name, 'synthetic source hash fixture')
        self.write('evals/results/context-regrade/rubric.txt', 'Return anonymous schema verdicts.')
        self.save('evals/results/context-regrade/author-context.json', run.context.CONTEXT)
        self.cases = [dict(id=f'dev-{subset}-{i:02}', task='source original statement', category=run.CATEGORIES[i % 5], split='development', subset=subset, assertions=[]) for subset in ('tune', 'validation') for i in range(20)]
        self.save('evals/large/development.json', dict(cases=self.cases))
        skill_hash = pairwise.text_hash(bench.bundle(self.root/'evals/versions/v4'))
        refs = [dict(case=c['id'], config=cfg, arm=arm, split='development', subset=c['subset'], response='reference source statement '+arm, model=identity[1], effort=identity[2], task_sha256=pairwise.text_hash(c['task']), skill_sha256=skill_hash if arm == 'v4' else None) for c in self.cases for cfg, identity in run.CONFIGS.items() for arm in run.REFERENCES]
        self.save('evals/results/large-interim/responses.json', refs)
        self.public, self.work = run.locations('v8-dev', 'tune')

    def write(self, filename, text):
        path = self.root/filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def save(self, filename, value):
        self.write(filename, json.dumps(value))

    def freeze(self):
        run.freeze('v8-dev', 'tune')
        return run.load('v8-dev', 'tune')

    @staticmethod
    def fake_call(prompt, config):
        identity = {**run.CONFIGS, **run.JUDGES}[config]
        meta = dict(model=identity[1], effort=identity[2], usage={'reported_tokens': 7})
        if 'INPUT_JSON:' not in prompt:
            return 'candidate source statement', meta
        payload = json.loads(prompt.split('INPUT_JSON:\n', 1)[1])
        verdicts = {}
        for label, responses in payload['pairs'].items():
            quotes = dict(source=['source'], A=[responses['A']], B=[responses['B']])
            verdicts[label] = dict(is_proof=payload['is_proof'], proof_reason='Task-based applicability.', material_error_A=False, material_error_B=False, material_errors={s: dict(severity='none', reason='Preserved source.', quotes=quotes) for s in ('A', 'B')}, dimensions={d: dict(preference='NA' if d == 'proof' and not payload['is_proof'] else 'tie', reason='Equivalent artifacts.', quotes=quotes) for d in pairwise.DIMENSIONS}, overall='tie')
        return json.dumps(verdicts), meta

    def fixture_texts(self):
        plan, rubric, cases, texts = self.freeze()
        for cid in cases:
            for cfg in run.CONFIGS:
                texts[cid, cfg, 'v8-dev'] = 'candidate source statement'
        return plan, rubric, cases, texts

    def test_frozen_live_files_and_duplicate_freeze(self):
        plan, _, cases, _ = self.freeze()
        self.assertEqual(len(cases), 20)
        self.assertEqual(plan['generated_output_cap'], 80)
        self.assertEqual(plan['primary_judgments'], 320)
        self.assertEqual(plan['audit_judgments'], 64)
        self.assertEqual(len(plan['jobs']), 120)
        with self.assertRaises(ValueError):
            run.freeze('v8-dev', 'tune')
        self.assertEqual(self.call.call_count, 0)
        (self.public/'bundle.txt').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'hash'):
            run.load('v8-dev', 'tune')

    def test_proof_bytes_and_baseline_task_hash_required(self):
        self.write('evals/versions/v8-dev/references/proofs.md', 'Changed proof')
        with self.assertRaisesRegex(ValueError, 'Proof guidance'):
            run.freeze('v8-dev', 'tune')
        self.write('evals/versions/v8-dev/references/proofs.md', 'Keep every proof step.\n')
        refs = run.read(self.root/'evals/results/large-interim/responses.json')
        refs[0]['task_sha256'] = 'bad'
        self.save('evals/results/large-interim/responses.json', refs)
        with self.assertRaisesRegex(ValueError, 'Baseline task'):
            run.freeze('v8-dev', 'tune')

    def test_nonselected_rows_never_inspected_and_no_holdout_selection(self):
        class Poison(dict):
            def __getitem__(self, key):
                if key != 'case':
                    raise AssertionError('Nondevelopment data accessed')
                return 'not-a-selected-development-id'
        original = run.read
        def guarded(path):
            self.assertNotIn('holdout', str(path))
            value = original(path)
            if path.name == 'responses.json':
                return [Poison(), *value]
            return value
        with patch.object(run, 'read', side_effect=guarded):
            self.assertEqual(len(run.baselines(run.development('tune'))), 160)
            self.freeze()
        for subset in ('holdout', '../holdout', 'fresh'):
            with self.assertRaises(ValueError):
                run.development(subset)
            with self.assertRaises(ValueError):
                run.locations('v8-dev', subset)
        for version in ('../escape', 'none', 'v4'):
            with self.assertRaises(ValueError):
                run.locations(version, 'tune')

    def test_guard_blocks_claude_even_with_plausible_metadata(self):
        plan, _, cases, _ = self.freeze()
        case = next(iter(cases.values()))
        bundle = (self.public/'bundle.txt').read_text()
        with patch.dict(bench.CONFIGS, {'astra-medium': ('claude', 'gpt-6-astra', 'medium')}):
            with self.assertRaisesRegex(ValueError, 'Codex'):
                run.generation_one(plan, case, 'astra-medium', self.work, bundle)
        self.assertEqual(self.call.call_count, 0)
        with self.assertRaises(ValueError):
            run.guard('grader-opus', plan['configs'])

    def test_deterministic_balanced_orders_and_explicit_v4_reference(self):
        plan, rubric, cases, texts = self.fixture_texts()
        self.assertEqual(plan['jobs'], run.jobs_for(list(cases.values()), 'v8-dev'))
        audits = [j for j in plan['jobs'] if j['order'] == 'reversed']
        self.assertEqual({j['case'] for j in audits}, set(cases))
        primary = {(e['case'], e['config'], e['reference'], j['judge']): e['a_side'] for j in plan['jobs'] if j['order'] == 'primary' for e in j['pairs']}
        for j in audits:
            for e in j['pairs']:
                self.assertNotEqual(e['a_side'], primary[e['case'], e['config'], e['reference'], j['judge']])
        for job in plan['jobs']:
            self.assertLessEqual(len(job['pairs']), 4)
            prompt, _, pairs = run.request(job, rubric, cases, texts)
            for label in (*run.CONFIGS, *run.JUDGES, 'v8-dev'):
                self.assertNotIn(label, prompt)
            for e in job['pairs']:
                ref_label = 'A' if e['a_side'] == 'left' else 'B'
                self.assertEqual(pairs[e['label']][ref_label], texts[e['case'], e['config'], e['reference']])

    def test_writing_not_regenerated_for_quality_and_tampering_rejected(self):
        plan, _, cases, _ = self.freeze()
        case = next(iter(cases.values()))
        cfg = 'astra-medium'
        bundle = (self.public/'bundle.txt').read_text()
        with patch.object(bench, 'call', return_value=('Bad writing.', dict(model=run.CONFIGS[cfg][1], effort='medium', usage={}))) as call:
            run.generation_one(plan, case, cfg, self.work, bundle)
            run.generation_one(plan, case, cfg, self.work, bundle)
            self.assertEqual(call.call_count, 1)
            p = self.work/'runs'/case['id']/cfg/'v8-dev'/'response.md'
            p.write_text('Changed output')
            with self.assertRaisesRegex(ValueError, 'output changed'):
                run.generation_one(plan, case, cfg, self.work, bundle)
            self.assertEqual(call.call_count, 1)

    def test_transport_failure_cap_persistent_and_unknown_errors_no_retry(self):
        plan, _, cases, _ = self.freeze()
        case = next(iter(cases.values()))
        bundle = (self.public/'bundle.txt').read_text()
        with patch.object(bench, 'call', side_effect=RuntimeError('transport unavailable')) as call:
            for _ in range(2):
                with self.assertRaises(RuntimeError):
                    run.generation_one(plan, case, 'astra-medium', self.work, bundle)
            self.assertEqual(call.call_count, 4)
        with patch.object(bench, 'call', side_effect=ValueError('programming fault')) as call:
            with self.assertRaises(ValueError):
                run.generation_one(plan, case, 'sol-low', self.work, bundle)
            self.assertEqual(call.call_count, 1)

    def test_judge_accepts_first_valid_only_and_saves_invalid_raw(self):
        plan, rubric, cases, texts = self.fixture_texts()
        job = plan['jobs'][0]
        prompt, _, _ = run.request(job, rubric, cases, texts)
        valid, meta = self.fake_call(prompt, job['judge'])
        with patch.object(bench, 'call', side_effect=[('{invalid', meta), (valid, meta)]) as call:
            run.judge_one(job, plan, rubric, cases, texts, self.work)
            run.judge_one(job, plan, rubric, cases, texts, self.work)
            self.assertEqual(call.call_count, 2)
        directory = self.work/'judges'/job['id']
        self.assertEqual((directory/'1/raw.txt').read_text(), '{invalid')
        self.assertTrue((directory/'1/invalid.json').exists())
        records = run.read(directory/'records.json')
        self.assertTrue(all(r['attempt'] == 2 for r in records))
        records[0]['outcome'] = 'win'
        pairwise.save_json(directory/'records.json', records)
        with self.assertRaisesRegex(ValueError, 'first valid verdict'):
            run.judge_one(job, plan, rubric, cases, texts, self.work)

    def test_judge_guard_no_claude(self):
        plan, rubric, cases, texts = self.fixture_texts()
        job = plan['jobs'][0]
        with patch.dict(bench.CONFIGS, {job['judge']: ('claude', 'fake', 'high')}):
            with self.assertRaisesRegex(ValueError, 'Codex'):
                run.judge_one(job, plan, rubric, cases, texts, self.work)
        self.assertEqual(self.call.call_count, 0)

    def test_complete_matrix_missing_audit_duplicate_and_reference_tamper(self):
        plan, _, _, _ = self.freeze()
        rows = [dict(case=e['case'], config=e['config'], candidate=e['candidate'], reference=e['reference'], judge=j['judge'], order=j['order']) for j in plan['jobs'] for e in j['pairs']]
        run.complete_matrix(plan, rows)
        for bad in (rows[:-1], rows+rows[:1], [r for r in rows if r['order'] == 'primary']):
            with self.assertRaises(ValueError):
                run.complete_matrix(plan, bad)
        rows[0]['reference'] = 'v5a'
        with self.assertRaises(ValueError):
            run.complete_matrix(plan, rows)

    def test_neutral_ties_case_weighting_and_no_hidden_metrics(self):
        rows = [dict(case='one', outcome='tie') for _ in range(8)]
        stat = run.net_stats(rows)
        self.assertEqual(stat['net_pp'], 0)
        self.assertEqual(stat['net_ci95_pp'], [0, 0])
        self.assertNotIn('preference', stat)
        self.assertNotIn('ci95', stat)
        rows = [dict(case='one', outcome='win') for _ in range(8)] + [dict(case='two', outcome='loss')]
        self.assertEqual(run.net_stats(rows)['net_pp'], 0)
        self.assertEqual(run.net_stats([dict(case='one', outcome='win'), dict(case='one', outcome='tie')])['net_pp'], 50)

    def test_cli_capture_preserves_failed_and_timeout_final_message(self):
        directory = self.root/'private-attempt'
        directory.mkdir()
        final = self.root/'temporary-cli-output'
        content = 'Full output even on nonzero exit, never publish the envelope.'
        final.write_text(content)
        command = ['synthetic-cli', '-o', str(final)]
        result = run.subprocess.CompletedProcess(command, 1, 'stdout envelope', 'stderr envelope')
        with patch.object(run.subprocess, 'run', return_value=result):
            with run.capture_cli(directory):
                bench.subprocess.run(command)
        self.assertEqual((directory/'cli-last-message.txt').read_text(), content)
        self.assertEqual(run.read(directory/'cli.json')['returncode'], 1)
        timeout = run.subprocess.TimeoutExpired(command, 1, output='partial stdout', stderr='partial stderr')
        with patch.object(run.subprocess, 'run', side_effect=timeout):
            with self.assertRaises(run.subprocess.TimeoutExpired):
                with run.capture_cli(directory):
                    bench.subprocess.run(command)
        self.assertEqual((directory/'cli-last-message.txt').read_text(), content)
        self.assertTrue(run.read(directory/'cli.json')['timeout'])

    def test_resigned_plan_tampering_still_hits_private_anchor(self):
        plan, _, _, _ = self.freeze()
        plan['source_development_sha256'] = 'changed source claim'
        plan['plan_sha256'] = pairwise.digest({k: v for k, v in plan.items() if k != 'plan_sha256'})
        pairwise.save_json(self.public/'plan.json', plan)
        with self.assertRaisesRegex(ValueError, 'anchor'):
            run.load('v8-dev', 'tune')

    def test_publication_privacy_rejects_paths_and_tokens(self):
        for value in ('/Users/example/private', '/home/user/private', '.local/secret', 'Bearer abcdefghijklmnopqrstuvwxyz'):
            with self.assertRaises(ValueError):
                run.public_safe(value)

    def test_report_full_matrix_portable_no_calls_and_missing_rejection(self):
        plan, _, _, _ = self.freeze()
        def inline(function, args, workers, work):
            for a in args:
                function(*a)
        with patch.object(run, 'parallel', side_effect=inline), contextlib.redirect_stdout(io.StringIO()):
            run.run('v8-dev', 'tune', workers=8)
        self.assertEqual(self.call.call_count, 200)
        # Bootstrap mechanics are tested above; keep this 384-verdict integration fast.
        real_stats = run.net_stats
        with patch.object(run, 'net_stats', side_effect=lambda rows, dimension=None: real_stats(rows, dimension, samples=100)), patch.object(bench, 'call', side_effect=AssertionError('Report model call forbidden')), contextlib.redirect_stdout(io.StringIO()):
            summary = run.report('v8-dev', 'tune')
            self.assertEqual(summary['primary_judgments'], 320)
            self.assertEqual(summary['audit_judgments'], 64)
            self.assertEqual(summary['usage']['reported_tokens'], 1400)
            self.assertEqual(summary['comparisons']['none']['overall']['net_pp'], 0)
            self.assertEqual(summary['agreement']['cross_judge']['pairs'], 160)
            self.assertEqual(summary['agreement']['order']['pairs'], 64)
            self.assertEqual(run.report('v8-dev', 'tune', published=True), summary)
            all_public = '\n'.join(p.read_text() for p in self.public.iterdir() if p.is_file())
            self.assertNotIn(str(self.root), all_public)
            self.assertNotIn('"preference": 0.5', all_public)
            record_path = self.work/'judges'/plan['jobs'][0]['id']/'records.json'
            record_path.unlink()
            with self.assertRaises(FileNotFoundError):
                run.report('v8-dev', 'tune')
            responses = run.read(self.public/'responses.json')
            responses[-1]['response'] = 'tampered'
            pairwise.save_json(self.public/'responses.json', responses)
            with self.assertRaisesRegex(ValueError, 'hash changed'):
                run.report('v8-dev', 'tune', published=True)


if __name__ == '__main__':
    unittest.main()
