"""No model calls: verify author-regrade provenance and denominators."""
import copy,json,unittest
from unittest.mock import patch
import pairwise
import context_regrade as run
import report_context_regrade as report

class ContextRegradeTests(unittest.TestCase):
    def setUp(self):
        self.cases={'test':dict(id='test',task='source',assertions=[],user_context='Keep the original voice.',is_proof=False)}
        self.texts={('test','haiku','none'):'reference',('test','haiku','v4'):'candidate'}
        self.job=dict(id='batch',judge='sol-high',case='test',order='primary',pairs=[dict(case='test',config='haiku',candidate='v4',reference='none',a_side='right',label='P01')])
        self.rubric='frozen rubric'
        prompt,supplied,pairs=run.request(self.job,self.rubric,self.cases,self.texts)
        quotes=dict(source=['source'],A=['candidate'],B=['reference'])
        verdict=dict(is_proof=False,proof_reason='prose',material_error_A=False,material_error_B=False,overall='tie',material_errors={s:dict(severity='none',reason='faithful',quotes=quotes) for s in ['A','B']},dimensions={d:dict(preference='NA' if d=='proof' else 'tie',reason='equivalent',quotes=quotes) for d in pairwise.DIMENSIONS})
        self.raw=json.dumps(dict(P01=verdict))
        r=dict(version='context-regrade-v1',batch='batch',case='test',config='haiku',candidate='v4',reference='none',judge='sol-high',order='primary',candidate_position='A',raw_judgment=verdict,**pairwise.normalized(verdict,'A'),response_sha256={a:pairwise.text_hash(self.texts['test','haiku',a]) for a in ['none','v4']},prompt_sha256=pairwise.text_hash(prompt),rubric_sha256=pairwise.text_hash(self.rubric),context_sha256=pairwise.text_hash(supplied['user_context']),raw_sha256=pairwise.text_hash(self.raw),attempt=1,pair_id='P01',evidence_format_repairs=[])
        self.sign(r);self.records=[r]

    def sign(self,r):r['record_sha256']=pairwise.digest({k:v for k,v in r.items() if k!='record_sha256'})
    def validate(self,**changes):
        args=dict(job=self.job,records=self.records,raw=self.raw,attempt=1,rubric=self.rubric,cases=self.cases,texts=self.texts);args.update(changes)
        report.validate_batch(**args)

    def test_valid_and_no_model_calls(self):
        with patch.object(run.bench,'call',side_effect=AssertionError('Model call forbidden')):self.validate()

    def test_syntax_repair_changes_no_values_and_keeps_duplicate_checks(self):
        obj,repairs=run.parse_batch('{"value": "literal ,}", "array": [1,],}')
        self.assertEqual(obj,{'value':'literal ,}', 'array':[1]})
        self.assertEqual(len(repairs),2)
        with self.assertRaises(pairwise.SchemaError):run.parse_batch('{"value": 1, "value": 2,}')
        with self.assertRaises(pairwise.SchemaError):run.parse_batch('{"value": ')

    def test_opener_case_repair_never_changes_variables_or_words(self):
        v={'dimensions':{'voice':{'quotes':{'A':['The input stays fixed.','X is fixed.','The output stays fixed.']}}}}
        fixed,repairs=run.repair_evidence(v,dict(task='source',responses={'A':'Start here; the input stays fixed. x is fixed.','B':''}))
        self.assertEqual(fixed['dimensions']['voice']['quotes']['A'],['the input stays fixed.','X is fixed.','The output stays fixed.'])
        self.assertEqual(len(repairs),1)

    def test_resigned_verdict_metadata_and_response_tampering_rejected(self):
        for change in [dict(outcome='win'),dict(judge='astra-high'),dict(candidate_position='B'),dict(prompt_sha256='wrong'),dict(attempt=2)]:
            rs=copy.deepcopy(self.records);rs[0].update(change);self.sign(rs[0])
            with self.subTest(change=change),self.assertRaises(ValueError):self.validate(records=rs)
        texts=dict(self.texts);texts['test','haiku','none']='other'
        with self.assertRaises(ValueError):self.validate(texts=texts)

    def test_missing_extra_and_duplicate_pairs_rejected(self):
        for rs in [[],self.records*2]:
            with self.assertRaises(ValueError):self.validate(records=rs)
        with self.assertRaises(ValueError):self.validate(raw=json.dumps({}))

    def test_context_bound_and_not_identity(self):
        prompt,_,_=run.request(self.job,self.rubric,self.cases,self.texts)
        self.assertIn('Keep the original voice.',prompt)
        self.assertNotIn('haiku',prompt);self.assertNotIn('sol-high',prompt)
        cases=copy.deepcopy(self.cases);cases['test']['user_context']='changed'
        with self.assertRaises(ValueError):self.validate(cases=cases)

    def test_complete_coverage_requires_both_arms_models_and_judges(self):
        rs=[dict(case='one',config=c,candidate=a,judge=j,order='primary') for c in report.CONFIGS for a in ['v4','v5a'] for j in run.JUDGES]
        self.assertEqual(report.balanced_cases(rs),['one'])
        self.assertEqual(report.balanced_cases(rs[:-1]),[])
        rs[-1]['order']='reversed';self.assertEqual(report.balanced_cases(rs),[])

    def test_reliability_keeps_versions_distinct(self):
        rs=[dict(case='one',config='haiku',candidate=a,judge=j,order=o,outcome='win' if j=='astra-high' else 'loss') for a in ['v4','v5a'] for j in run.JUDGES for o in ['primary','reversed']]
        d=report.reliability(rs)
        self.assertEqual(d['cross_judge']['pairs'],2);self.assertEqual(d['cross_judge']['opposite'],2)
        self.assertEqual(d['order']['pairs'],4);self.assertEqual(d['order']['same'],4)

if __name__=='__main__':unittest.main()
