#!/usr/bin/env python3
"""README dev figures, strictly versus no skill; reads published results only."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'evals/results/prose-repair'
OUT = ROOT / 'docs/img'
DIMENSIONS = ['overall', 'meaning', 'naturalness', 'progression', 'voice', 'proof']
LABELS = {'overall': 'Overall', 'meaning': 'Meaning', 'naturalness': 'Naturalness',
          'progression': 'Argument flow', 'voice': 'Author voice', 'proof': 'Proof exposition',
          'nonproof': 'All prose', 'ordinary': 'Ordinary prose', 'research': 'Research prose',
          'argument': 'Argument', 'control': 'Controls'}


def read(path):
    return json.loads(path.read_text())


def render(name, matrix, rows, columns, categorical=False):
    for theme in ('light', 'dark'):
        bg, fg = ('#ffffff', '#20252b') if theme == 'light' else ('#1a1a19', '#f0efec')
        with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 12,
                             'svg.fonttype': 'none', 'svg.hashsalt': 'readme-no-skill',
                             'text.color': fg, 'axes.labelcolor': fg,
                             'xtick.color': fg, 'ytick.color': fg}):
            fig, ax = plt.subplots(figsize=(8.3, 5.4), facecolor=bg)
            ax.set_facecolor(bg)
            fig.subplots_adjust(left=.29, right=.98, top=.76, bottom=.19)
            cmap = LinearSegmentedColormap.from_list('signed', ['#b84a48', '#f2f2f2', '#1c5cab'])
            bound = 1 if categorical else 100
            norm = TwoSlopeNorm(vmin=-bound, vcenter=0, vmax=bound)
            for y, values in enumerate(matrix):
                for x, value in enumerate(values):
                    color = cmap(norm(value)) if value is not None else ('#ececea' if theme == 'light' else '#44443f')
                    ax.add_patch(plt.Rectangle((x+.025, y+.025), .95, .95, facecolor=color))
                    text = ('NA' if value is None else
                            ({1: 'Win', 0: 'Tie', -1: 'Loss'}[value] if categorical else f'{value:+.1f}'))
                    lum = .2126*color[0]+.7152*color[1]+.0722*color[2] if not isinstance(color, str) else None
                    ink = fg if value is None else ('white' if lum < .5 else '#17212b')
                    ax.text(x+.5, y+.5, text, ha='center', va='center', color=ink,
                            fontweight='bold' if columns[x] == 'All' else 'normal')
            ax.set_xlim(0, len(columns)); ax.set_ylim(len(rows), 0)
            ax.set_xticks([x+.5 for x in range(len(columns))], columns)
            ax.xaxis.tick_top(); ax.xaxis.set_label_position('top')
            ax.set_xlabel('Model and reasoning effort', labelpad=12)
            ax.set_yticks([y+.5 for y in range(len(rows))], rows)
            ax.tick_params(length=0, pad=8)
            for spine in ax.spines.values(): spine.set_visible(False)
            if categorical:
                fig.legend(handles=[Patch(facecolor=cmap(norm(v)), label=t) for v,t in [(1,'Win'),(0,'Tie'),(-1,'Loss')]],
                           loc='lower center', ncol=3, frameon=False, labelcolor=fg,
                           bbox_to_anchor=(.62,.02))
            else:
                cax = fig.add_axes([.34,.08,.57,.025])
                cb = fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=cax,
                                  orientation='horizontal',ticks=[-100,-50,0,50,100])
                cb.set_label('Win rate − loss rate (percentage points)')
                cb.outline.set_edgecolor(fg)
            for ext in ('svg','png'):
                path=OUT/f'{name}-{theme}.{ext}'
                fig.savefig(path, dpi=150, bbox_inches='tight',pad_inches=.15,
                            metadata={'Date':None} if ext=='svg' else None)
                if ext=='svg': path.write_text('\n'.join(s.rstrip() for s in path.read_text().splitlines())+'\n')
            plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    summary=read(RES/'v9-restored-20/summary.json')['none']
    configs=['astra-high','sol-low','sonnet-high','all']
    cols=['Astra\nhigh','6.1 Sol\nlow','Sonnet 5.5\nhigh','All']
    for section,metrics in [('categories',['nonproof','ordinary','research','argument','proof','control']),('dimensions',DIMENSIONS)]:
        matrix=[]
        for metric in metrics:
            row=[]
            for cfg in configs:
                cell=summary[cfg]
                stat=(cell['nonproof'] if metric=='nonproof' else cell['categories'][metric]) if section=='categories' else cell['dimensions'][metric]
                row.append(stat['net_pp'] if stat else None)
            matrix.append(row)
        labels=[('Proofs' if m=='proof' and section=='categories' else LABELS[m]) for m in metrics]
        render('restored-dev-'+section,matrix,labels,cols)
    observations=read(RES/'v11-targeted/validated-observations.json')+read(RES/'v12-targeted/observations.json')
    chosen=[]
    for cfg,version in [('sol-low','v11-dev'),('sonnet-high','v12-dev')]:
        matches=[r for r in observations if r['config']==cfg and r['candidate']==version and r['reference']=='none']
        assert len(matches)==1 and not matches[0]['candidate_material_error']
        chosen.append(matches[0])
    values={'win':1,'tie':0,'loss':-1,'NA':None}
    matrix=[[values[r['dimensions'][m]] for r in chosen] for m in DIMENSIONS]
    render('focused-dev',matrix,[LABELS[m] for m in DIMENSIONS],
           ['6.1 Sol low\nv11 · excluded runs','Sonnet 5.5 high\nv12 · variance proof'],True)

if __name__=='__main__': main()
