#!/usr/bin/env python3
"""No-call reporting for the reconciled skill. Incomplete pairs never become ties."""
import argparse, collections, json
from pathlib import Path
import scholarly_full as suite
import long_horizon as lh
import prose_repair as stats
import pairwise
import plot_pairwise as plot
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evals/results/scholarly-full'
EXT=ROOT/'evals/results/scholarly-antigravity'
CONFIGS=list(suite.CONFIGS)+['argon-high','flash-high']
GROUPS={**{c:[c] for c in CONFIGS},'claude-all':list(suite.CONFIGS[:6]),'codex-all':list(suite.CONFIGS[6:]),'antigravity-all':['argon-high','flash-high'],'all':CONFIGS}

def read_if(p,default):return lh.read(p) if p.exists() else default

def paired(records):
    groups=collections.defaultdict(list)
    for r in records:
        if r['order']=='primary' and r['stage']=='judge':groups[r['case'],r['config']].append(r)
    out=[]
    for key,rows in groups.items():
        lh.require(len(rows)<=2 and len({r['judge'] for r in rows})==len(rows),'Duplicate judge')
        if {r['judge'] for r in rows}=={'astra-high','sol-high'}:out+=rows
    return out

def metrics(rows,cases):
    return dict(overall=stats.net_stats(rows),categories={k:stats.net_stats([r for r in rows if cases[r['case']]['category']==k]) for k in stats.CATEGORIES},
                dimensions={k:stats.net_stats(rows,k) for k in pairwise.DIMENSIONS if k!='overall'},
                material_error_flags={arm:sum(r[arm+'_material_error'] for r in rows) for arm in ('candidate','reference')})

def summary(records,cases):
    complete=paired(records);result={}
    for split in ('development','holdout'):
        result[split]={}
        splitrows=[r for r in complete if cases[r['case']]['split']==split]
        for group,configs in GROUPS.items():
            # Same case set and both judges for every pooled configuration.
            keys={(r['case'],r['config']) for r in splitrows}
            ids={cid for cid in cases if all((cid,cfg) in keys for cfg in configs)}
            result[split][group]=metrics([r for r in splitrows if r['case'] in ids and r['config'] in configs],cases)
    return result

def plot_input(value):
    # Compatibility with established renderer only; stored statistics remain signed pp.
    if isinstance(value,dict):
        out={k:plot_input(v) for k,v in value.items()}
        if 'net_pp' in value:out['preference']=(value['net_pp']+100)/200
        return out
    return value

def run(make_plots=False):
    cases={c['id']:c for c in lh.read(OUT/'cases.json')}
    original=read_if(OUT/'observations.json',[]);extra=read_if(EXT/'observations.json',[])
    records=original+extra
    short=[r for r in records if r['stage']=='judge'];s=summary(short,cases)
    long=[r for r in records if r['stage']=='long-judge']
    usage=read_if(OUT/'usage.json',{});extension=read_if(EXT/'usage.json',{})
    totals=dict(calls=usage.get('calls',0)+extension.get('allocation_calls',0),max_calls=2400,
                known_reported_tokens=usage.get('known_reported_tokens',0)+extension.get('known_tokens',0),
                charged_tokens=usage.get('charged_tokens',0)+extension.get('charged_tokens',0),token_guard=75000000,
                claude_writing_calls=usage.get('claude_calls',0),max_claude_writing_calls=557,
                unknown_attempts=usage.get('unknown_attempts',0)+extension.get('unknown',0))
    complete=len(paired(short))==1920
    payload=dict(complete_primary_matrix=complete,expected_primary_judgments=1920,
                 valid_primary_judgments=sum(r['order']=='primary' for r in short),paired_primary_judgments=len(paired(short)),
                 summary=s,agreement=stats.agreement(short),usage=totals,
                 long_horizon={str(t):stats.net_stats([r for r in long if r['order']=='primary' and r['turn']==t]) for t in (1,6)},
                 notes='Only pairs with both judges enter metrics. Pooled groups require the same cases for every constituent configuration. Ties contribute zero. 3000 case-level bootstrap replicates. Existing OOS is retrospective; fresh holdouts sealed. No inference from incomplete cells.')
    lh.public_safe(payload);lh.write(OUT/'summary-current.json',payload)
    lines=['# Reconciled skill versus no skill','', 'COMPLETE primary short-task matrix.' if complete else 'INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.', '',
           f'Valid paired primary judgments: {len(paired(short))}/1920. Both judges must be present for a case/model pair to enter the table.', '',
           '| Split | Model / effort | Cases | Win − loss (pp) | 95% case-bootstrap interval |', '|---|---|---:|---:|---:|']
    for split,groups in s.items():
        for cfg in CONFIGS+['claude-all','codex-all','antigravity-all','all']:
            v=groups[cfg]['overall']
            if v:lines.append(f'| {split} | {cfg} | {v["cases"]} | {v["net_pp"]:+.1f} | [{v["net_ci95_pp"][0]:+.1f}, {v["net_ci95_pp"][1]:+.1f}] |')
    lines+=['',f'Combined spend so far: {totals["calls"]}/2400 attempts, {totals["known_reported_tokens"]:,} known reported tokens, {totals["claude_writing_calls"]}/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.', '',
            'Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.']
    lh.write(OUT/'summary-current.md',('\n'.join(lines)+'\n').encode())
    if make_plots:
        old_order,old_labels=plot.ORDER,plot.LABELS
        plot.ORDER=old_order[:-1]+['argon-high','flash-high','antigravity-all','all']
        plot.LABELS=old_labels[:-1]+['Argon 4\nhigh','3.8 Flash\nhigh','All\nAntigravity','All\nconfigs']
        plot.plot_pairwise(plot_input(s),ROOT/'docs/img/scholarly-full',show_counts=True,figsize=(20.5,8.2))
        plot.ORDER,plot.LABELS=old_order,old_labels
    print(json.dumps(dict(primary_paired=len(paired(short)),expected=1920,**totals)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plots',action='store_true');a=p.parse_args();run(a.plots)
