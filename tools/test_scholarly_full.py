"""No-call regression checks for the approved shared budget and isolation."""
import json
import unittest
import scholarly_full as suite


class Guards(unittest.TestCase):
    def setUp(self):
        self.plan = dict(max_calls=1600, token_guard=50000000, max_claude_calls=557,
                         reservations={'generation': 60000, 'judge': 100000, 'long': 400000})
        self.job = dict(stage='generation', config='haiku')
        self.row = dict(finished=True, known=True, completed=True, failed=False,
                        claude=True, charged_tokens=100)

    def test_fresh(self):
        self.assertTrue(suite.allowed(self.plan, self.job, []))

    def test_all_claude_configs_share_limit(self):
        for cfg in suite.CONFIGS[:6]:
            self.assertFalse(suite.allowed(self.plan, dict(self.job, config=cfg), [self.row] * 557))
        self.assertTrue(suite.allowed(self.plan, dict(self.job, config='sol-low'), [self.row] * 557))

    def test_total_calls(self):
        self.assertFalse(suite.allowed(self.plan, dict(self.job, config='sol-low'), [dict(self.row, claude=False)] * 1600))

    def test_unknown_or_failed_stops(self):
        for change in (dict(known=False), dict(completed=False), dict(failed=True)):
            self.assertFalse(suite.allowed(self.plan, self.job, [dict(self.row, **change)]))

    def test_inflight_reservation_is_charged(self):
        self.assertFalse(suite.allowed(self.plan, self.job, [dict(self.row, finished=False, charged_tokens=49950000)]))
        self.assertTrue(suite.allowed(self.plan, self.job, [dict(self.row, finished=False, charged_tokens=49940000)]))

    def test_long_turn_uses_same_cap(self):
        self.assertFalse(suite.allowed(self.plan, dict(stage='long', config='astra-high'), [dict(self.row, charged_tokens=49700000)]))

    def test_dependencies(self):
        job = dict(stage='long', turn=2, id='long--example--none--2')
        self.assertFalse(suite.ready(job, {}, set()))
        self.assertTrue(suite.ready(job, {}, {'long--example--none--1'}))

    def test_no_skill_prompt_has_no_guidance(self):
        prompt = suite.generation_prompt({'task': 'source text'}, 'none')
        self.assertNotIn('editing-guidance', prompt)
        self.assertTrue(prompt.endswith('<task>\nsource text\n</task>'))

    def test_both_rollout_formats(self):
        formats = [dict(type='event_msg', payload=dict(type='user_message', message='hello')),
                   dict(type='response_item', payload=dict(role='user', content=[dict(type='input_text', text='hello')]))]
        for row in formats:
            raw = '\n'.join(map(json.dumps, [row, dict(type='turn_context')])).encode()
            suite.verify_delta(raw, 'hello')
            with self.assertRaises(ValueError): suite.verify_delta(raw, 'different')


if __name__ == '__main__': unittest.main()
