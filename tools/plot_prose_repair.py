#!/usr/bin/env python3
"""Plot published development repair judgments; never invokes models."""
import argparse
import json
from pathlib import Path
from pairwise_report import aggregate

CONFIGS = ['astra-medium', 'astra-high', 'sol-low', 'luna-medium', 'all']
LABELS = ['Astra\nmedium', 'Astra\nhigh', 'Sol\nlow', 'Luna\nmedium', 'All']
CATEGORIES = ['nonproof', 'ordinary', 'research', 'argument', 'proof', 'control']
DIMENSIONS = ['meaning', 'naturalness', 'progression', 'voice', 'proof', 'overall']


def plot(directories, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
    import numpy as np

    inputs = []
    for directory in directories:
        plan = json.loads((directory/'plan.json').read_text())
        rows = json.loads((directory/'observations.json').read_text())
        rows = [r for r in rows if r['order'] == 'primary']
        cases = {c['id']: c for c in json.loads((directory/'cases.json').read_text())}
        expected = {(c, cfg, ref, judge) for c in cases for cfg in CONFIGS[:-1]
                    for ref in ('none', 'v4') for judge in ('astra-high', 'sol-high')}
        keys = [(r['case'], r['config'], r['reference'], r['judge']) for r in rows]
        if len(keys) != len(expected) or set(keys) != expected:
            raise ValueError('Incomplete primary matrix')
        inputs.append((plan, rows, cases))
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import to_rgba
    from matplotlib.patches import Rectangle

    cmap = LinearSegmentedColormap.from_list('repair', ['#b84a48','#f2f2f2','#1c5cab'], N=257)
    norm = TwoSlopeNorm(vmin=-100, vcenter=0, vmax=100)
    out.mkdir(parents=True, exist_ok=True)
    columns, x = [], 0
    for ref in ('none', 'v4'):
        for config, label in zip(CONFIGS, LABELS):
            if config == 'all': x += .22
            columns.append((ref, config, label, x))
            x += 1
        x += .65
    width = columns[-1][-1] + 1
    for theme in ('light', 'dark'):
        bg, fg = ('white','#20252b') if theme == 'light' else ('#1a1a19','#f0efec')
        with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,
                             'svg.fonttype':'none','svg.hashsalt':'prose-repair-v2',
                             'text.color':fg,'axes.labelcolor':fg,
                             'xtick.color':fg,'ytick.color':fg,'figure.facecolor':bg,
                             'axes.facecolor':bg}):
            for section, metrics in [('categories', CATEGORIES), ('dimensions', DIMENSIONS)]:
                fig = plt.figure(figsize=(13.6, 7.7))
                ax = fig.add_axes([.20, .18, .78, .67])
                yticks, ylabels = [], []
                stride = len(inputs) + .55
                for mi, metric in enumerate(metrics):
                    label = {'nonproof':'All prose', 'ordinary':'Ordinary prose',
                             'research':'Research prose'}.get(metric, metric.capitalize())
                    ax.text(-1.23, mi*stride + len(inputs)/2, label,
                            ha='right', va='center', color=fg)
                    for si, (plan, records, cases) in enumerate(inputs):
                        y = mi*stride + si
                        phase = 'Tune' if plan['subset']=='tune' else 'Check'
                        n = sum(c['category']!='proof' if metric=='nonproof' else c['category']==metric
                                for c in cases.values()) if section=='categories' else (
                                    sum(c['category']=='proof' for c in cases.values()) if metric=='proof' else len(cases))
                        yticks.append(y+.5); ylabels.append(f'{phase} ({n})')
                        for ref, cfg, _, cx in columns:
                            selected = [r for r in records if r['reference']==ref and
                                        (cfg=='all' or r['config']==cfg)]
                            if section=='categories':
                                selected = [r for r in selected if
                                    (cases[r['case']]['category']!='proof' if metric=='nonproof'
                                     else cases[r['case']]['category']==metric)]
                                value = aggregate(selected, samples=1)
                            else:
                                value = aggregate(selected, None if metric=='overall' else metric, samples=1)
                            v = None if value is None else value['net_pp']
                            color = '#aaa' if v is None else cmap(norm(v))
                            ax.add_patch(Rectangle((cx+.025,y+.025),.95,.95,
                                                   facecolor=color,edgecolor='none'))
                            rgba=to_rgba(color)
                            lum=.2126*rgba[0]+.7152*rgba[1]+.0722*rgba[2]
                            ax.text(cx+.5,y+.5,'NA' if v is None else f'{v:+.1f}',
                                    ha='center',va='center',color='white' if lum<.5 else '#17212b',
                                    fontsize=9.5,fontweight='bold' if cfg=='all' else 'normal')
                ax.set_xlim(-.04,width+.04)
                ax.set_ylim((len(metrics)-1)*stride+len(inputs)+.1,-.2)
                ax.set_xticks([c[3]+.5 for c in columns],[c[2] for c in columns])
                ax.xaxis.tick_top(); ax.tick_params(length=0,pad=8)
                ax.set_yticks(yticks,ylabels); ax.tick_params(axis='y',pad=6)
                ax.set_xlabel('Model and reasoning effort',labelpad=10)
                for ref, title in [('none','Versus no skill'),('v4','Versus v4')]:
                    positions=[c[3]+.5 for c in columns if c[0]==ref]
                    ax.text(sum(positions)/len(positions),1.135,title,
                            transform=ax.get_xaxis_transform(),ha='center',va='bottom',fontsize=11)
                for spine in ax.spines.values():spine.set_visible(False)
                cax=fig.add_axes([.34,.075,.48,.018])
                bar=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=cax,
                                orientation='horizontal',ticks=[-100,-50,0,50,100])
                bar.set_label('Win rate − loss rate (percentage points)')
                bar.outline.set_edgecolor(fg)
                for ext in ('svg','png'):
                    target=out/f'{inputs[0][0]["candidate"]}-{section}-{theme}.{ext}'
                    fig.savefig(target,dpi=150,bbox_inches='tight',pad_inches=.12,
                                metadata={'Date':None} if ext=='svg' else None)
                    if ext=='svg':
                        target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
                plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directories',type=Path,nargs='+')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    plot(args.directories,args.out)
