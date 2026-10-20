import copy
import unittest
import small_repair as small
import grade_long_horizon as grading
import long_horizon as lh
import prose_repair as prior

class SmallRepairTests(unittest.TestCase):
    def test_frozen_scope(self):
        plan,cases,texts,rubric=small.load()
        self.assertEqual(set(cases),set(small.IDS))
        self.assertTrue(all(c['split']=='development' for c in cases.values()))
        self.assertEqual(len(texts),6)
        self.assertEqual(len(plan['jobs']),4)
        self.assertEqual(plan['retries'],0)
    def test_anonymous_orders(self):
        plan,cases,texts,rubric=small.load()
        for cid in cases:texts[cid,'astra-high','v9-dev']='synthetic candidate'
        primary={}
        for job in plan['jobs']:
            prompt,supplied,pairs=prior.request(job,rubric,cases,texts)
            payload=prompt.split('INPUT_JSON:\n',1)[1]
            self.assertNotIn('v9-dev',payload)
            self.assertNotIn('astra-high',payload)
            if job['order']=='primary':primary[job['case']]=pairs
            else:
                for key,pair in pairs.items():
                    self.assertEqual(pair['A'],primary[job['case']][key]['B'])
                    self.assertEqual(pair['B'],primary[job['case']][key]['A'])
    def test_no_future_feedback(self):
        case=lh.read(small.ROOT/'evals/long-horizon/development.json')['cases'][0]
        _,context,_=grading.load()
        supplied=grading.supplied(case,1,context)
        for instruction in case['feedback']:self.assertNotIn(instruction,supplied['task'])
        self.assertEqual(supplied['assertions'],[i['text'] for i in case['invariants'] if i['since_turn']==0])
    def test_proof_bytes_unchanged(self):
        for name in ['proofs.md','paper-voice.md']:
            root=small.ROOT/'evals/versions'
            self.assertEqual((root/'v4/references'/name).read_bytes(),(root/'v9-dev/references'/name).read_bytes())

if __name__=='__main__':unittest.main()
