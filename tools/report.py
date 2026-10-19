#!/usr/bin/env python3
"""Publish anonymized observations, paired summaries, and optional heatmaps."""
import argparse
import json
from pathlib import Path
import random
import statistics as st


def value(rows, metric):
    if metric=='holistic': return st.mean(r['score'] for r in rows)
    if metric=='words': return st.median(r['words'] for r in rows)
    items=[a['passed'] for r in rows for a in r['assertions'] if metric=='all' or a['group']==metric]
    return st.mean(items) if items else None


def difference(rows, arm, reference, metric, samples=3000):
    by={}
    for row in rows: by.setdefault(row['case'],{}).setdefault(row['config'],{})[row['arm']]=row
    cases=[c for c in by if any(arm in v and reference in v for v in by[c].values())]
    def paired(cs):
        pairs=[v for c in cs for v in by[c].values() if arm in v and reference in v]
        a=value([v[arm] for v in pairs],metric);b=value([v[reference] for v in pairs],metric)
        return None if a is None or b is None else a-b
    rng=random.Random(20261019)
    ds=[paired(rng.choices(cases,k=len(cases))) for _ in range(samples)]
    ds=sorted(d for d in ds if d is not None)
    return [paired(cases),ds[int(.025*len(ds))],ds[int(.975*len(ds))-1]] if ds else None


def fmt(metric,x):
    if x is None:return '—'
    return f'{x:.2f}' if metric=='holistic' else (f'{x:.0f}' if metric=='words' else f'{100*x:.1f}%')


def plot(rows,selected,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    import numpy as np
    cfgs=['sonnet-low','sonnet-high','astra-medium','pooled']
    labels=['Sonnet\nlow','Sonnet\nhigh','Astra\nmedium','Pooled']
    metrics=['fidelity','style','argument','proof']
    for mode in ['light','dark']:
        bg='#ffffff' if mode=='light' else '#14191f';fg='#20252b' if mode=='light' else '#e7edf4'
        with plt.rc_context({'font.size':11,'font.family':'DejaVu Sans','svg.fonttype':'none','text.color':fg,'axes.labelcolor':fg,'xtick.color':fg,'ytick.color':fg,'figure.facecolor':bg,'axes.facecolor':bg}):
            fig,axs=plt.subplots(2,3,figsize=(15,6.7),layout='constrained')
            seq=LinearSegmentedColormap.from_list('rate',['#f6f8fa','#86b6ef','#1c5cab'])
            div=LinearSegmentedColormap.from_list('diff',['#b84a48','#f2f2f2','#1c5cab'])
            for i,split in enumerate(['development','heldout']):
                rs=[r for r in rows if r['split']==split]
                for j,kind in enumerate(['none',selected,'difference']):
                    ax=axs[i,j];data=[]
                    for metric in metrics:
                        vals=[]
                        for cfg in cfgs:
                            cr=[r for r in rs if cfg=='pooled' or r['config']==cfg]
                            a=value([r for r in cr if r['arm']==selected],metric)
                            b=value([r for r in cr if r['arm']=='none'],metric)
                            v=(a-b if a is not None and b is not None else None) if kind=='difference' else (b if kind=='none' else a)
                            vals.append(float('nan') if v is None else 100*v)
                        data.append(vals)
                    data=np.array(data);im=ax.imshow(data,cmap=div if j==2 else seq,vmin=-30 if j==2 else 0,vmax=30 if j==2 else 100,aspect='auto')
                    ax.set_xticks(range(4),labels);ax.set_yticks(range(4),[m.capitalize() for m in metrics]);ax.tick_params(length=0,pad=7)
                    if i==0:ax.set_title(['No skill','Declaude','Difference (pp)'][j],fontsize=12)
                    if j==0:ax.set_ylabel('In sample' if i==0 else 'Held out',labelpad=14)
                    for y in range(4):
                        for x in range(4):
                            v=data[y,x];label='—' if np.isnan(v) else (f'{v:+.0f}' if j==2 else f'{v:.0f}')
                            color='#ffffff' if (j!=2 and v>65) or (j==2 and abs(v)>18) else '#17212b'
                            ax.text(x,y,label,ha='center',va='center',color=color,fontsize=11)
                    for spine in ax.spines.values():spine.set_visible(False)
                    if i==0 and j==1:rate_im=im
                    if i==0 and j==2:diff_im=im
            fig.colorbar(rate_im,ax=axs[:,:2].ravel().tolist(),shrink=.75,label='Assertion pass rate (%)')
            fig.colorbar(diff_im,ax=axs[:,2].ravel().tolist(),shrink=.75,label='Difference (percentage points)')
            fig.savefig(out/f'assertions-{mode}.svg',facecolor=bg)
            if mode=='light':fig.savefig(out/'assertions.png',dpi=140,facecolor=bg)
            plt.close(fig)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--runs',nargs='*',type=Path,default=[])
    ap.add_argument('--cases',nargs='+',type=Path,required=True)
    ap.add_argument('--observations',type=Path)
    ap.add_argument('--selected',default='v2')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--plot',action='store_true')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    cases={c['id']:c for p in a.cases for c in json.loads(p.read_text())['cases']}
    rows=json.loads(a.observations.read_text()) if a.observations else []
    for root in a.runs:
        for p in sorted(root.glob('*/*/*/grading.json')):
            case,cfg,arm=p.parts[-4:-1];g=json.loads(p.read_text());meta=json.loads(p.with_name('meta.json').read_text());response=p.with_name('response.md').read_text()
            rows.append(dict(case=case,split=cases[case]['split'],subset=cases[case].get('subset'),config=cfg,arm=arm,score=g['score'],assertions=g['assertions'],note=g['note'],grader=g['grader'],response=response,words=len(response.split()),model=meta['model'],effort=meta['effort'],task_sha256=meta['task_sha256'],skill_sha256=meta['skill_sha256']))
    keys=[(r['case'],r['config'],r['arm']) for r in rows]
    assert len(set(keys))==len(keys),'Duplicate observations; do not select a preferred repeat'
    (a.out/'observations.json').write_text(json.dumps(rows,indent=2)+'\n')
    final=[r for r in rows if r['arm'] in ['none',a.selected]]
    # A complete paired matrix is required before an overall benchmark is reported.
    configs=sorted({r['config'] for r in final})
    assert set(r['case'] for r in final)==set(cases),'Cases are missing'
    assert set((r['case'],r['config'],r['arm']) for r in final)=={(c,cfg,arm) for c in cases for cfg in configs for arm in ['none',a.selected]},'Incomplete paired matrix'
    parts=['# Evaluation results','',f'Selected skill: {a.selected}. One run per case, configuration, and condition. Intervals resample paired cases, not individual assertions.','']
    summary={}
    for split in ['development','heldout']:
        rs=[r for r in final if r['split']==split]
        parts += [f'## {split}','', '| Metric | No skill | Declaude | Difference [95% interval] |','|---|---:|---:|---:|']
        summary[split]={}
        for m in ['all','fidelity','style','argument','proof','holistic','words']:
            b=value([r for r in rs if r['arm']=='none'],m);s=value([r for r in rs if r['arm']==a.selected],m)
            d=difference(rs,a.selected,'none',m) if m!='words' else None
            scale=1 if m=='holistic' else 100
            ds='—' if d is None else f'{scale*d[0]:+.2f} [{scale*d[1]:+.2f}, {scale*d[2]:+.2f}]'+('' if m=='holistic' else ' pp')
            parts.append(f'| {m} | {fmt(m,b)} | {fmt(m,s)} | {ds} |')
            summary[split][m]={'none':b,a.selected:s,'difference_ci':d}
        parts += ['', '| Configuration | No skill assertions / holistic | Declaude assertions / holistic |','|---|---:|---:|']
        for cfg in configs:
            br=[r for r in rs if r['config']==cfg and r['arm']=='none'];sr=[r for r in rs if r['config']==cfg and r['arm']==a.selected]
            parts.append(f'| {cfg} | {fmt("all",value(br,"all"))} / {value(br,"holistic"):.2f} | {fmt("all",value(sr,"all"))} / {value(sr,"holistic"):.2f} |')
        parts.append('')
    parts += ['## Development A/B selection','', 'The initial and revised skill versions were compared on Sonnet low and Astra medium only. These cases were available for selection and are not held out.','', '| Subset | Version | Assertions | Holistic |','|---|---|---:|---:|']
    for subset in ['tune','validation']:
        for arm in ['none','v1','v2','v3']:
            rs=[r for r in rows if r['subset']==subset and r['arm']==arm and r['config'] in ['sonnet-low','astra-medium']]
            if rs:parts.append(f'| {subset} | {arm} | {fmt("all",value(rs,"all"))} | {value(rs,"holistic"):.2f} |')
    (a.out/'report.md').write_text('\n'.join(parts)+'\n')
    (a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    if a.plot:plot(final,a.selected,a.out)
    print('\n'.join(parts))


if __name__=='__main__':main()
