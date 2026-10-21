import copy
import unittest
from finalize_restored_results import repair_optional_source

class OptionalQuoteTests(unittest.TestCase):
    def fixture(self):
        quotes={'source':['Different wording.'],'A':['Response A'],'B':['Response B']}
        item={'preference':'A','reason':'Keep this reasoning.','quotes':quotes}
        return {'overall':'A','dimensions':{k:copy.deepcopy(item) for k in ('meaning','naturalness','progression','voice','proof','overall')},'material_errors':{'A':{'severity':'minor','reason':'Keep error.','quotes':copy.deepcopy(quotes)}}}, {'task':'Exact source.','assertions':['Different wording.'],'responses':{'A':'Response A','B':'Response B'}}
    def test_optional_only_and_preserves_decision(self):
        original,source=self.fixture();before=copy.deepcopy(original)
        value,changes=repair_optional_source(original,source)
        self.assertEqual(original,before)
        self.assertEqual(value['overall'],before['overall'])
        self.assertEqual(value['material_errors'],before['material_errors'])
        for k in ('meaning','proof'):self.assertEqual(value['dimensions'][k],before['dimensions'][k])
        for k in ('naturalness','progression','voice','overall'):
            self.assertEqual(value['dimensions'][k]['quotes']['source'],[])
            for f in ('reason','preference'):self.assertEqual(value['dimensions'][k][f],before['dimensions'][k][f])
            for f in ('A','B'):self.assertEqual(value['dimensions'][k]['quotes'][f],before['dimensions'][k]['quotes'][f])
        self.assertEqual(len(changes),4)
        self.assertTrue(all('supplied assertions' in x['reason'] for x in changes))
    def test_verbatim_optional_unchanged(self):
        v,s=self.fixture();s['task']='Different wording.'
        result,changes=repair_optional_source(v,s)
        self.assertEqual(result,v);self.assertFalse(changes)
    def test_paraphrase_disclosed_not_replaced(self):
        v,s=self.fixture();s['assertions']=[]
        result,changes=repair_optional_source(v,s)
        self.assertTrue(all(x['after'] is None and 'Nonverbatim' in x['reason'] for x in changes))
if __name__=='__main__':unittest.main()
