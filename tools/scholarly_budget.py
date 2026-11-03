#!/usr/bin/env python3
"""Budget-only amendment; original frozen prompts, jobs and outputs are unchanged.

Disjoint allocations guarantee the two runners cannot spend each other's budget.
The original eleven attempts are included, not reset. No calls during freeze.
"""
import argparse
from pathlib import Path
import scholarly_runtime as runtime
import scholarly_full as suite
import long_horizon as lh
import pairwise
ORIGINAL_LOAD = runtime.load
AMENDMENT = suite.OUT / 'combined-budget.json'

def freeze():
    lh.require(not AMENDMENT.exists(), 'Already frozen')
    plan, _ = ORIGINAL_LOAD()
    doc = dict(parent_runtime_plan_sha256=plan['plan_sha256'],
        authorization='User approved 2,400 combined calls / 75M reported tokens, with 557 Claude writing calls unchanged, covering both skills and both added Antigravity models.',
        combined=dict(max_calls=2400, token_guard=75000000, max_claude_writing_calls=557),
        allocations=dict(original=dict(max_calls=1450, token_guard=45000000, max_claude_writing_calls=557),
                         antigravity_extension=dict(max_calls=950, token_guard=30000000, max_claude_writing_calls=0)),
        accounting='Original allocation includes all prior attempts and tokens. Independent allocations sum to combined limits; tokens reserve in-flight calls but a response can exceed its reservation. No reset, automatic retry or fresh-holdout access.',
        script_sha256=lh.hashed(Path(__file__)))
    doc['sha256'] = pairwise.digest(doc)
    lh.write(AMENDMENT, doc)

def load():
    plan, cases = ORIGINAL_LOAD()
    doc = lh.read(AMENDMENT)
    lh.require(doc['sha256'] == pairwise.digest({k:v for k,v in doc.items() if k!='sha256'}), 'Budget changed')
    lh.require(doc['parent_runtime_plan_sha256']==plan['plan_sha256'] and doc['script_sha256']==lh.hashed(Path(__file__)), 'Budget provenance changed')
    a=doc['allocations']['original']
    return dict(plan,max_calls=a['max_calls'],token_guard=a['token_guard'],budget_amendment_sha256=doc['sha256']),cases

def report():
    runtime.load=load; runtime.install_adapter(); suite.report()
    path=suite.OUT/'report.md'
    text=path.read_text().replace('/1600 calls','/1450 allocated calls').replace('guard: 50M','guard: 45M')
    text+='\nCombined authorization across both skills: 2,400 calls / 75M reported tokens / 557 Claude writing calls. This original matrix is allocated 1,450 calls / 45M tokens; the Antigravity extension is allocated 950 calls / 30M tokens. See combined-budget.json.\n'
    path.write_text(text)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('action',choices=['freeze','run','report']); a=p.parse_args()
    if a.action=='freeze': freeze()
    elif a.action=='report': report()
    else:
        runtime.load=load
        runtime.run()
        report()
