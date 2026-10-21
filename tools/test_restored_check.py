import unittest
import restored_check as r

class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.plan={'max_calls':100,'max_generations':60,'max_judges':40,'max_claude_calls':20,'token_guard':2500000,'codex_credit_guard':300,'writer_token_reservation':30000,'judge_token_reservation':40000,'credit_reservations':{'astra-high':8,'sol-low':3,'sol-high':5}}
        self.job={'stage':'generation','config':'astra-high'}
    def row(self,**kw):
        d=dict(stage='generation',config='astra-high',finished=True,known=True,charged_tokens=100,codex_credits=1);d.update(kw);return d
    def test_empty(self):self.assertTrue(r.allowed(self.plan,self.job,[]))
    def test_pending_reservations_count(self):self.assertFalse(r.allowed(self.plan,self.job,[self.row(finished=False,known=False)]*100))
    def test_generation_cap(self):self.assertFalse(r.allowed(self.plan,self.job,[self.row()]*60))
    def test_judge_cap(self):self.assertFalse(r.allowed(self.plan,{'stage':'judge'},[self.row(stage='judge')]*40))
    def test_claude_cap(self):self.assertFalse(r.allowed(self.plan,{'stage':'generation','config':'sonnet-high'},[self.row(config='sonnet-high')]*20))
    def test_token_reservation(self):self.assertFalse(r.allowed(self.plan,self.job,[self.row(charged_tokens=2470001)]))
    def test_credit_reservation(self):self.assertFalse(r.allowed(self.plan,self.job,[self.row(codex_credits=292.01)]))
    def test_unknown_stops(self):self.assertFalse(r.allowed(self.plan,self.job,[self.row(known=False)]))
    def test_cache_not_double_counted(self):self.assertAlmostEqual(r.credits({'input_tokens':1000000,'cached_input_tokens':400000,'output_tokens':100000},'astra-high'),285)
    def test_reservation_does_not_create_call_directory(self):
        j={'stage':'judge','id':'sample'}
        self.assertNotEqual(r.directory(j),r.reservation(j).parent)

if __name__=='__main__':unittest.main()
