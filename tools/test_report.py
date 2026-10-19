"""Reporting-only integration tests with synthetic files and model calls disabled."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import bench
import report
import pairwise_report
import plot_pairwise


class AbsoluteReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.runs = self.root/'runs'
        self.case = dict(id='synthetic-pool', task='Synthetic source.', split='development', subset='validation',
                         assertions=[dict(group='style',text='Preserves voice')])
        self.cases = {self.case['id']: self.case}
        self.captured = []
        # Ten configs, varying arm counts, enough for several pools and a tail.
        for cfg in [f'config-{i:02}' for i in range(10)]:
            for arm in (['none','v4','v5a'] if cfg!='config-09' else ['none','v5a']):
                path=self.runs/self.case['id']/cfg/arm
                path.mkdir(parents=True)
                (path/'response.md').write_bytes(f'{cfg} {arm} café\r\nexact bytes\r\n'.encode())
                (path/'meta.json').write_text(json.dumps(dict(model='synthetic-model',effort=None,
                    task_sha256=hashlib.sha256(self.case['task'].encode()).hexdigest(),skill_sha256=None)))
        # Capture the runner's actual grouping/fingerprint without invoking grade_pool.
        def capture(case, pool, pool_id, fingerprint, rubric_hash, version):
            self.captured.append((list(pool),pool_id,fingerprint))
            for i,path in enumerate(pool):
                grade=dict(score=4,assertions=[dict(self.case['assertions'][0],passed=True,evidence='synthetic')],note='',
                    rubric_sha256=rubric_hash,pool_sha256=fingerprint,
                    grader=dict(version=version,pool_id=pool_id,pool_size=len(pool),blind_label=f'R{i+1:02}'))
                path.with_name('grading.json').write_text(json.dumps(grade))
        with patch.object(bench,'call',side_effect=AssertionError('No model calls')), patch.object(bench,'grade_pool',side_effect=capture):
            bench.grade_one(self.case,self.runs)

    def rows(self):
        return report.load_rows([self.runs],None,self.cases)

    def test_matches_runner_pools_and_exact_bytes(self):
        rows=self.rows()
        self.assertEqual(len(rows),29)
        self.assertGreater(len(self.captured),1)
        self.assertTrue(all('\r\n' in r['response'] for r in rows))
        expected={str(p.relative_to(self.runs)):fingerprint for pool,_,fingerprint in self.captured for p in pool}
        for row in rows:
            self.assertEqual(row['pool_sha256'],expected[f"{row['case']}/{row['config']}/{row['arm']}/response.md"])
        exported=self.root/'observations.json';exported.write_text(json.dumps(rows))
        self.assertEqual(report.load_rows([],exported,self.cases),rows)

    def test_import_derives_and_rejects_split_subset(self):
        rows=self.rows()
        for r in rows:r.pop('split');r.pop('subset')
        report.derive_case_metadata(rows,self.cases)
        self.assertTrue(all(r['split']=='development' and r['subset']=='validation' for r in rows))
        for key,value in [('split','holdout'),('subset','tune'),('subset',None)]:
            bad=copy.deepcopy(rows);bad[0][key]=value
            with self.subTest(key=key,value=value),self.assertRaisesRegex(ValueError,key):
                report.derive_case_metadata(bad,self.cases)

    def test_independently_graded_sources_survive_export(self):
        import shutil
        roots=[]
        for index,configs in enumerate([['config-00','config-01'],['config-02','config-03']]):
            root=self.root/f'source-{index}';roots.append(root)
            for cfg in configs:
                shutil.copytree(self.runs/self.case['id']/cfg,root/self.case['id']/cfg)
            def capture(case,pool,pool_id,fingerprint,rubric_hash,version):
                for i,path in enumerate(pool):
                    grade=json.loads(path.with_name('grading.json').read_text())
                    grade.update(pool_sha256=fingerprint,rubric_sha256=rubric_hash)
                    grade['grader'].update(pool_id=pool_id,pool_size=len(pool),blind_label=f'R{i+1:02}')
                    path.with_name('grading.json').write_text(json.dumps(grade))
            with patch.object(bench,'call',side_effect=AssertionError('No models')),patch.object(bench,'grade_pool',side_effect=capture):
                bench.grade_one(self.case,root)
        rows=report.load_rows(roots,None,self.cases)
        self.assertEqual(len({r['grading_source'] for r in rows}),2)
        exported=self.root/'separate.json';exported.write_text(json.dumps(rows))
        self.assertEqual(report.load_rows([],exported,self.cases),rows)
        # Removing the source boundary must not silently accept a different pool.
        for r in rows:r.pop('grading_source')
        with self.assertRaises(ValueError):report.verify_pools(rows,self.cases)

    def test_stale_response_and_ungraded_pool_member_rejected(self):
        pool=self.captured[0][0]
        pool[0].write_bytes(pool[0].read_bytes()+b'changed')
        # Even without its grade, this changed member must affect peer fingerprints.
        pool[0].with_name('grading.json').unlink()
        with self.assertRaisesRegex(ValueError,'pool_sha256'):self.rows()

    def test_import_tampering_missing_arm_and_labels(self):
        original=self.rows()
        for kind in ['response','missing-arm','label','pool-id','rubric','missing-hash']:
            rows=copy.deepcopy(original)
            if kind=='response':rows[0]['response']=rows[0]['response'].replace('\r\n','\n')
            elif kind=='missing-arm':rows=[r for r in rows if r['arm']!='v4']
            elif kind=='label':rows[0]['grader']['blind_label']='R99'
            elif kind=='pool-id':rows[0]['grader']['pool_id']=99
            elif kind=='rubric':rows[0]['rubric_sha256']='wrong'
            else:rows[0].pop('pool_sha256')
            with self.subTest(kind=kind),self.assertRaises(ValueError):report.verify_pools(rows,self.cases)

    def test_changed_rubric_or_prompt_rejected(self):
        rows=self.rows();cases=copy.deepcopy(self.cases);cases[self.case['id']]['task']='different'
        with self.assertRaises(ValueError):report.verify_pools(rows,cases)
        # Patch only the grader prompt bytes; no file changes.
        with patch.object(Path,'read_bytes',return_value=b'changed prompt'),self.assertRaises(ValueError):
            report.verify_pools(rows,self.cases)

    def test_cli_rejects_before_writing_and_labels_unchanged_estimand(self):
        # CLI display needs only two arms, but verification uses all source pool rows.
        observations=self.root/'observations.json';observations.write_text(json.dumps(self.rows()))
        cases=self.root/'cases.json';cases.write_text(json.dumps({'cases':[self.case]}))
        out=self.root/'report'
        args=['--observations',str(observations),'--cases',str(cases),'--selected','v5a','--out',str(out)]
        # Use a single-config fixture for successful CLI publication; independent
        # helper verification above exercises the ten-config, three-arm layout.
        one_root=self.root/'single'
        for arm in ['none','v5a']:
            dest=one_root/self.case['id']/'haiku'/arm;dest.mkdir(parents=True)
            (dest/'response.md').write_bytes(arm.encode())
        def capture(case,pool,pool_id,fingerprint,rubric_hash,version):
            self.single_rows=[]
            for i,path in enumerate(pool):
                self.single_rows.append(dict(case=case['id'],config='haiku',arm=path.parent.name,response=path.read_text(),
                    score=4,assertions=[dict(case['assertions'][0],passed=True)],note='',model='synthetic',effort=None,
                    pool_sha256=fingerprint,rubric_sha256=rubric_hash,
                    grader=dict(version=version,pool_id=pool_id,pool_size=len(pool),blind_label=f'R{i+1:02}')))
        with patch.object(bench,'call',side_effect=AssertionError('No models')),patch.object(bench,'grade_pool',side_effect=capture):
            bench.grade_one(self.case,one_root)
        observations.write_text(json.dumps(self.single_rows))
        with contextlib.redirect_stdout(io.StringIO()):report.main(args)
        before={p.name:p.read_bytes() for p in out.iterdir()}
        self.assertIn('assertion-weighted',before['report.md'].decode())
        self.single_rows[0]['split']='holdout';observations.write_text(json.dumps(self.single_rows))
        with self.assertRaisesRegex(ValueError,'split'):report.main(args)
        self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()})

    def test_assertion_weighted_estimand_and_cluster_bootstrap_unchanged(self):
        rows=[]
        for case,n in [('short',1),('long',9)]:
            for arm in ['none','v5a']:
                rows.append(dict(case=case,config='haiku',arm=arm,
                    assertions=[dict(group='style',passed=(arm=='v5a')==(case=='short'))]*n))
        result=report.difference(rows,'v5a','none','all',samples=1000)
        self.assertAlmostEqual(result[0],-.8)
        self.assertEqual(report.value([r for r in rows if r['arm']=='v5a'],'all'),.1)
        doubled=[dict(r,config='second') for r in rows]
        self.assertEqual(result,report.difference(rows+doubled,'v5a','none','all',samples=1000))


class DiagnosticsTests(unittest.TestCase):
    def test_unique_cases_split_judge_counts_and_empty_audits(self):
        cases={'a':{'split':'development'},'b':{'split':'holdout'},'c':{'split':'unused'}}
        records=[]
        for case in ['a','b']:
            for cfg in ['haiku','astra-high']:
                for judge in ['grader-opus','astra-high']:
                    for order in ['primary','reversed']:
                        records.append(dict(case=case,config=cfg,judge=judge,order=order,
                            outcome='loss' if (case,cfg,judge,order)==('a','haiku','grader-opus','reversed') else 'win'))
        checks=pairwise_report.order_diagnostics(records,cases)
        self.assertEqual((checks['cases'],checks['case_config_pairs'],checks['pairs']),(2,4,8))
        self.assertEqual(checks['opposite_non_tie'],1)
        dev=checks['by_split']['development']
        self.assertEqual((dev['cases'],dev['case_config_pairs'],dev['pairs']),(1,2,4))
        self.assertEqual(dev['by_judge']['grader-opus']['opposite_non_tie'],1)
        self.assertEqual(dev['by_judge']['astra-high']['opposite_non_tie'],0)
        self.assertEqual(checks['by_split']['unused']['cases'],0)
        empty=pairwise_report.order_diagnostics([r for r in records if r['order']=='primary'],cases)
        self.assertEqual(empty['pairs'],0)
        self.assertEqual(empty['by_judge']['grader-opus']['cases'],0)

    def test_validation_not_oos_and_semantic_order_preserved(self):
        with self.assertRaisesRegex(ValueError,'Unknown split'):plot_pairwise._split_rows({'validation':{}})
        self.assertEqual(plot_pairwise._split_rows({'holdout':{'h':1},'development':{'d':2}}),
                         [('IS',{'d':2}),('OOS',{'h':1})])


if __name__=='__main__':unittest.main()
