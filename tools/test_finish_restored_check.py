import unittest
from finish_restored_check import repair_initial_case
class CaseRepairTests(unittest.TestCase):
    def v(self,q):return {'material_errors':{'B':{'reason':'unchanged','severity':'none','quotes':{'source':[q],'A':[],'B':[]}}},'dimensions':{},'overall':'tie'}
    def source(self,s):return {'task':s,'responses':{'A':'','B':''}}
    def test_unique_initial_case(self):
        v,c=repair_initial_case(self.v('Those exchanges'),self.source('We did not record those exchanges.'))
        self.assertEqual(c[0]['after'],'those exchanges');self.assertEqual(v['overall'],'tie')
    def test_no_paraphrase(self):self.assertFalse(repair_initial_case(self.v('Those conversations'),self.source('We did not record those exchanges.'))[1])
    def test_ambiguous_rejected(self):self.assertFalse(repair_initial_case(self.v('Those exchanges'),self.source('those exchanges, those exchanges'))[1])
    def test_internal_case_rejected(self):self.assertFalse(repair_initial_case(self.v('Those Exchanges'),self.source('those exchanges'))[1])
    def test_verbatim_unchanged(self):self.assertFalse(repair_initial_case(self.v('Those exchanges'),self.source('Those exchanges'))[1])
if __name__=='__main__':unittest.main()
