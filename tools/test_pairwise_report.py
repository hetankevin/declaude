"""Synthetic reporting tests only: no models, skills, or benchmark artifacts."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pairwise
import pairwise_report as report


class StrictReportTests(unittest.TestCase):
    def setUp(self):
        self.seed = 'declaude-pairwise-v1'
        # Include both an audited and an unaudited task under the real schedule.
        ids = {}
        for i in range(100):
            case = f'synthetic-{i}'
            audited = int(pairwise.digest([self.seed, case, 'haiku', 'audit']), 16) / 2**256 < .2
            ids.setdefault(audited, case)
        self.cases = {c: dict(id=c, task='source', assertions=[], is_proof=False,
                             split='development', category='ordinary') for c in ids.values()}
        self.responses = {(c, 'haiku', a): text for c in self.cases
                          for a, text in [('none', 'reference'), ('v5a', 'candidate')]}
        self.rubric = 'frozen synthetic rubric'
        self.records = []
        for case in self.cases:
            audited = int(pairwise.digest([self.seed, case, 'haiku', 'audit']), 16) / 2**256 < .2
            for judge in ['grader-opus', 'astra-high']:
                base = ('left', 'right')[int(pairwise.digest([self.seed, case, 'haiku', judge, 'side']), 16) % 2]
                for reverse in ([False, True] if audited else [False]):
                    side = ('right' if base == 'left' else 'left') if reverse else base
                    other = 'right' if side == 'left' else 'left'
                    texts = dict(left='reference', right='candidate')
                    quotes = dict(source=['source'], A=[texts[side]], B=[texts[other]])
                    verdict = dict(is_proof=False, proof_reason='prose', material_error_A=False,
                                   material_error_B=False, overall='tie',
                                   material_errors={x:dict(severity='none', reason='faithful', quotes=quotes) for x in ['A','B']},
                                   dimensions={d:dict(preference='NA' if d=='proof' else 'tie', reason='equivalent', quotes=quotes) for d in pairwise.DIMENSIONS})
                    provider, model, effort = pairwise.bench.CONFIGS[judge]
                    meta = dict(case=case, config='haiku', judge=judge, provider=provider, model=model,
                                effort=effort, left_id='none', right_id='v5a', candidate_side='right',
                                seed=self.seed, reverse=reverse, base_a_side=base, order={'A':side,'B':other})
                    supplied = pairwise.supplied_case(self.cases[case])
                    supplied['responses'] = {'A':texts[side], 'B':texts[other]}
                    prompt = self.rubric + '\n\nINPUT_JSON:\n' + pairwise.canonical(supplied)
                    request = dict(version=pairwise.VERSION, rubric=self.rubric, prompt=prompt, responses=texts, metadata=meta)
                    label = 'A' if side == 'right' else 'B'
                    r = dict(version=pairwise.VERSION, fingerprint=pairwise.digest(request), metadata=meta,
                             case=case, config='haiku', candidate='v5a', reference='none', judge=judge,
                             order='reversed' if reverse else 'primary', candidate_position=label,
                             rubric_sha256=pairwise.text_hash(self.rubric), prompt_sha256=pairwise.text_hash(prompt),
                             response_sha256={k:pairwise.text_hash(v) for k,v in texts.items()},
                             raw_judgment=verdict, **pairwise.normalized(verdict,label))
                    self.sign(r)
                    self.records.append(r)

    @staticmethod
    def sign(r):
        r['record_sha256'] = pairwise.digest({k:v for k,v in r.items() if k!='record_sha256'})

    def validate(self, records=None, **overrides):
        args = dict(records=self.records if records is None else records, cases=self.cases,
                    configs=['haiku'], judges=['grader-opus','astra-high'], seed=self.seed,
                    audit=.2, candidate='v5a', reference='none', rubric=self.rubric, responses=self.responses)
        args.update(overrides)
        report.validate_records(**args)

    def test_complete_matrix(self):
        self.validate()

    def test_missing_primary_judge_config_and_audit(self):
        for order in ['primary','reversed']:
            with self.subTest(order=order):
                rows = copy.deepcopy(self.records)
                rows.pop(next(i for i,r in enumerate(rows) if r['order']==order))
                with self.assertRaisesRegex(ValueError,'matrix'):self.validate(rows)
        with self.assertRaisesRegex(ValueError,'matrix'):
            self.validate(configs=['haiku','sonnet-low'])

    def test_duplicate_and_unexpected_audit(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.validate(self.records+[self.records[0]])
        r = copy.deepcopy(next(r for r in self.records if not any(x['case']==r['case'] and x['order']=='reversed' for x in self.records)))
        r['order']='reversed'
        with self.assertRaisesRegex(ValueError,'matrix'):self.validate(self.records+[r])

    def test_record_hash_and_resigned_semantic_tampering(self):
        mutations = [lambda r:r.update(reference='v4'), lambda r:r['metadata'].update(seed='wrong'),
                     lambda r:r['metadata'].update(base_a_side='wrong'), lambda r:r.update(candidate_position='wrong'),
                     lambda r:r.update(rubric_sha256='wrong'), lambda r:r.update(prompt_sha256='wrong'),
                     lambda r:r['response_sha256'].update(left='wrong'), lambda r:r.update(fingerprint='wrong'),
                     lambda r:r.update(outcome='win'), lambda r:r['dimensions'].pop('meaning')]
        for resign in [False,True]:
            for mutation in mutations:
                with self.subTest(resign=resign,mutation=mutation):
                    rows=copy.deepcopy(self.records);mutation(rows[0])
                    if resign:self.sign(rows[0])
                    with self.assertRaises(ValueError):self.validate(rows)

    def test_response_and_task_binding(self):
        responses=dict(self.responses);responses[next(iter(responses))]='changed response'
        with self.assertRaises(ValueError):self.validate(responses=responses)
        cases=copy.deepcopy(self.cases);cases[next(iter(cases))]['task']='changed task'
        with self.assertRaises(ValueError):self.validate(cases=cases)

    def test_case_bootstrap_does_not_gain_precision_from_judge_repeats(self):
        rows=[dict(case='one',outcome='win'),dict(case='two',outcome='loss')]
        a=report.aggregate(rows,samples=1000);b=report.aggregate(rows*20,samples=1000)
        self.assertEqual(a['preference'],.5)
        self.assertEqual(a['ci95'],b['ci95'])
        self.assertEqual(b['cases'],2)

    def test_signed_net_advantage_and_neutral_ties(self):
        from plot_pairwise import _percentage
        for outcomes,expected in [(['tie']*4,0),(['win'],100),(['loss'],-100),(['win','win','tie','loss'],25)]:
            rows=[dict(case=str(i),outcome=o) for i,o in enumerate(outcomes)]
            result=report.aggregate(rows,samples=1000)
            self.assertEqual(result['net_pp'],expected)
            self.assertEqual(_percentage(result),expected)
            self.assertEqual(result['net_ci95_pp'],[200*x-100 for x in result['ci95']])
            self.assertEqual(result['judgments'],sum(result[k] for k in ['wins','ties','losses']))

    def test_reversed_audits_do_not_affect_performance(self):
        class Sink:
            def mkdir(self,**kwargs):pass
            def __truediv__(self,name):return self
            def write_text(self,text):pass
        rows=copy.deepcopy(self.records)
        for r in rows:
            if r['order']=='reversed':r['outcome']='win'
        result=report.report(rows,self.cases,Sink())
        overall=result['development']['all']['overall']
        self.assertEqual(overall['preference'],.5)
        self.assertEqual(overall['judgments'],4)

    def test_strict_cli_rejection_writes_nothing_and_legacy_still_works(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);cases=root/'cases.json';records=root/'records.json';out=root/'out'
            cases.write_text(json.dumps({'cases':list(self.cases.values())}))
            records.write_text(json.dumps(self.records[:1]))
            args=['--inputs',str(records),'--cases',str(cases),'--out',str(out)]
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                report.main(args+['--strict'])
            self.assertFalse(out.exists())
            matrix=root/'matrix.json';matrix.write_text('{}')
            with patch.object(report,'validate_manifest',return_value=self.responses), contextlib.redirect_stdout(io.StringIO()), self.assertRaises(ValueError):
                report.main(args+['--strict','--matrix',str(matrix),'--runs',str(root),'--candidate','v5a','--reference','none','--configs','haiku'])
            self.assertFalse(out.exists())
            with contextlib.redirect_stdout(io.StringIO()):report.main(args)
            self.assertTrue((out/'summary.json').exists())

    def test_manifest_hashes_and_generation_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);path=root/'renamed.json'
            path.write_text(json.dumps({'cases':list(self.cases.values())}))
            matrix=dict(configs={'haiku':dict(model='model',effort=None)}, pairwise_seed=self.seed,
                        selected='v5a',conditions=['none','v5a'],pairwise_grader_sha256=pairwise.text_hash(self.rubric),
                        dataset_sha256={'development':hashlib.sha256(path.read_bytes()).hexdigest()},
                        cases_per_split=2,skill_sha256_by_arm={'none':None,'v5a':'frozen'})
            for (c,cfg,arm),text in self.responses.items():
                dest=root/c/cfg/arm;dest.mkdir(parents=True)
                (dest/'response.md').write_text(text)
                (dest/'meta.json').write_text(json.dumps(dict(case=c,config=cfg,arm=arm,model='model',effort=None,
                    task_sha256=pairwise.text_hash('source'),skill_sha256=matrix['skill_sha256_by_arm'][arm])))
            def run(m=matrix):
                return report.validate_manifest(m,[path],self.cases,['haiku'],self.seed,'v5a','none',root,self.rubric)
            self.assertEqual(run(),self.responses)
            for key,value in [('pairwise_seed','wrong'),('pairwise_grader_sha256','wrong'),('cases_per_split',40),('dataset_sha256',{'development':'wrong'})]:
                with self.subTest(key=key),self.assertRaises(ValueError):run(dict(matrix,**{key:value}))
            meta=next(root.glob('*/*/*/meta.json'));data=json.loads(meta.read_text());data['skill_sha256']='wrong';meta.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'metadata'):run()


if __name__=='__main__':unittest.main()
