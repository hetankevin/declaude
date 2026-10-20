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
    cmap = LinearSegmentedColormap.from_list('repair', ['#b84a48','#f2f2f2','#1c5cab'], N=257)
    norm = TwoSlopeNorm(vmin=-100, vcenter=0, vmax=100)
    out.mkdir(parents=True, exist_ok=True)
    for theme in ('light', 'dark'):
        bg, fg = ('white','#20252b') if theme == 'light' else ('#1a1a19','#f0efec')
        with plt.rc_context({'font.family':'DejaVu Sans','font.size':11,
                             'svg.fonttype':'none','svg.hashsalt':'prose-repair-v1',
                             'text.color':fg,'axes.labelcolor':fg,
                             'xtick.color':fg,'ytick.color':fg,'figure.facecolor':bg,
                             'axes.facecolor':bg}):
            for section, metrics in [('categories', CATEGORIES), ('dimensions', DIMENSIONS)]:
                fig, axs = plt.subplots(len(inputs), 2, figsize=(12, 4.9*len(inputs)), squeeze=False,
                                        layout='constrained')
                for row, (plan, records, cases) in enumerate(inputs):
                    for col, ref in enumerate(('none','v4')):
                        ax = axs[row,col]
                        data = np.full((len(metrics),len(CONFIGS)),np.nan)
                        for y, metric in enumerate(metrics):
                            for x, cfg in enumerate(CONFIGS):
                                selected = [r for r in records if r['reference']==ref and
                                            (cfg=='all' or r['config']==cfg)]
                                if section=='categories':
                                    selected = [r for r in selected if
                                        (cases[r['case']]['category']!='proof' if metric=='nonproof'
                                         else cases[r['case']]['category']==metric)]
                                    value = aggregate(selected, samples=1)
                                else:
                                    value = aggregate(selected, None if metric=='overall' else metric, samples=1)
                                if value is not None: data[y,x] = value['net_pp']
                        image = ax.imshow(data,cmap=cmap,norm=norm,aspect='auto')
                        for y in range(len(metrics)):
                            for x in range(len(CONFIGS)):
                                v=data[y,x]
                                ax.text(x,y,'NA' if np.isnan(v) else f'{v:+.0f}' if v else '0',
                                        ha='center',va='center',color='white' if abs(v)>60 else '#20252b',fontsize=11)
                        ax.set_xticks(range(len(CONFIGS)), LABELS)
                        ax.set_yticks(range(len(metrics)), [m.capitalize() if m!='nonproof' else 'All prose' for m in metrics])
                        for spine in ax.spines.values(): spine.set_visible(False)
                        ax.tick_params(length=0)
                        ax.set_xlabel('Generator / effort')
                        ax.set_ylabel('Writing category' if section=='categories' else 'Judged dimension')
                        phase='Tuning' if plan['subset']=='tune' else 'Development check'
                        ax.set_title(f'{phase} · versus {"no skill" if ref=="none" else "v4"}',fontsize=12,pad=10)
                bar=fig.colorbar(image,ax=axs,orientation='horizontal',fraction=.055,pad=.06,ticks=[-100,-50,0,50,100])
                bar.set_label('Win rate − loss rate (percentage points)')
                bar.outline.set_visible(False)
                for ext in ('svg','png'):
                    target = out/f'{inputs[0][0]["candidate"]}-{section}-{theme}.{ext}'
                    fig.savefig(target,dpi=170)
                    if ext == 'svg':
                        target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
                plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directories',type=Path,nargs='+')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    plot(args.directories,args.out)
