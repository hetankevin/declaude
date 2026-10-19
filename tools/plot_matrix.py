"""Stratified IS/OOS heatmaps: models and effort across columns, paired splits by metric."""
from pathlib import Path

ORDER=['haiku','sonnet-low','sonnet-high','opus-low','opus-xhigh','fable','claude-all','astra-medium','astra-high','sol-low','luna-medium','codex-all','all']
LABELS=['Haiku 5.5\ndefault','Sonnet 5.5\nlow','Sonnet 5.5\nhigh','Opus 5.5\nlow','Opus 5.5\nxhigh','Fable 5.1\ndefault','All\nClaude','Astra\nmedium','Astra\nhigh','6.1 Sol\nlow','Luna\nmedium','All\nCodex','All\nconfigs']
METRICS=[('all','All assertions'),('fidelity','Meaning preserved'),('style','Natural prose'),('argument','Argument and purpose'),('proof','Proof exposition'),('holistic','Holistic score'),('words','Median reply words')]


def plot_matrix(groups, selected, out, reference='none'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap,Normalize
    from matplotlib.cm import ScalarMappable
    import numpy as np
    out=Path(out)
    splits=list(groups)
    if len(splits)!=2:raise ValueError('Heatmap requires exactly two splits')
    assertion_limit=max(10,10*__import__('math').ceil(max(abs(v[selected]-v[reference])*100 for d in groups.values() for c in d.values() for m,v in c.items() if m not in ['holistic','words'])/10))
    holistic_limit=max(.5,.5*__import__('math').ceil(max(abs(c['holistic'][selected]-c['holistic'][reference]) for d in groups.values() for c in d.values())/.5))
    for mode in ['light','dark']:
        bg,fg,grid=('#ffffff','#20252b','#dddddd') if mode=='light' else ('#1a1a19','#f0efec','#555550')
        neutral='#ececea' if mode=='light' else '#44443f'
        seq=LinearSegmentedColormap.from_list('rate',['#f6f8fa','#86b6ef','#1c5cab'])
        div=LinearSegmentedColormap.from_list('difference',['#b84a48','#f2f2f2','#1c5cab'])
        for kind,filename in [('difference','assertions'),(reference,'levels-none'),(selected,'levels-skill')]:
            with plt.rc_context({'font.size':10,'font.family':'DejaVu Sans','svg.fonttype':'none','text.color':fg,'axes.labelcolor':fg,'xtick.color':fg,'ytick.color':fg,'figure.facecolor':bg,'axes.facecolor':bg}):
                fig=plt.figure(figsize=(16.5,9.1))
                ax=fig.add_axes([.18,.16,.80,.73])
                xs=[];x=0
                for config in ORDER:
                    if config.endswith('-all') or config=='all':x+=.22
                    xs.append(x);x+=1
                    if config.endswith('-all'):x+=.22
                ys=[];yticks=[];ylabels=[]
                for i,(metric,label) in enumerate(METRICS):
                    for si,split in enumerate(splits):
                        y=i*2.6+si;ys.append(y);yticks.append(y+.5);ylabels.append(('IS' if si==0 else 'OOS'))
                        for ci,config in enumerate(ORDER):
                            cell=groups[split][config][metric];base=cell[reference];skill=cell[selected]
                            v=skill-base if kind=='difference' else cell[kind]
                            if metric=='words':
                                color=neutral;labeltext=f'{v:+.0f}' if kind=='difference' else f'{v:.0f}'
                            elif metric=='holistic':
                                color=div(Normalize(-holistic_limit,holistic_limit)(v)) if kind=='difference' else seq(Normalize(1,5)(v))
                                labeltext=f'{v:+.2f}' if kind=='difference' else f'{v:.2f}'
                            else:
                                v*=100
                                color=div(Normalize(-assertion_limit,assertion_limit)(v)) if kind=='difference' else seq(Normalize(0,100)(v))
                                labeltext=f'{v:+.1f}' if kind=='difference' else f'{v:.0f}'
                            ax.add_patch(plt.Rectangle((xs[ci]+.025,y+.025),.95,.95,facecolor=color,edgecolor='none'))
                            rgba=matplotlib.colors.to_rgba(color);lum=.2126*rgba[0]+.7152*rgba[1]+.0722*rgba[2]
                            ink='#ffffff' if lum<.5 else '#17212b'
                            ax.text(xs[ci]+.5,y+.5,labeltext,ha='center',va='center',fontsize=9.2,color=ink,fontweight='bold' if config.endswith('-all') or config=='all' else 'normal')
                    ax.text(-.65,i*2.6+1,label,ha='right',va='center',fontsize=10,color=fg)
                ax.set_xlim(-.04,x+.04);ax.set_ylim(ys[-1]+1.1,-.2)
                ax.set_xticks([v+.5 for v in xs],LABELS);ax.xaxis.tick_top();ax.tick_params(length=0,pad=9)
                ax.set_yticks(yticks,ylabels);ax.tick_params(axis='y',pad=5)
                ax.set_xlabel('Model and reasoning effort',labelpad=12);ax.xaxis.set_label_position('top')
                for spine in ax.spines.values():spine.set_visible(False)
                cax=fig.add_axes([.24,.065,.38,.018]);hax=fig.add_axes([.71,.065,.24,.018])
                if kind=='difference':
                    cb=fig.colorbar(ScalarMappable(norm=Normalize(-assertion_limit,assertion_limit),cmap=div),cax=cax,orientation='horizontal');cb.set_label('Assertion-weighted difference (percentage points)')
                    hb=fig.colorbar(ScalarMappable(norm=Normalize(-holistic_limit,holistic_limit),cmap=div),cax=hax,orientation='horizontal');hb.set_label('Holistic difference (points)')
                else:
                    cb=fig.colorbar(ScalarMappable(norm=Normalize(0,100),cmap=seq),cax=cax,orientation='horizontal');cb.set_label('Assertion-weighted pass rate (%)')
                    hb=fig.colorbar(ScalarMappable(norm=Normalize(1,5),cmap=seq),cax=hax,orientation='horizontal');hb.set_label('Holistic score (1–5)')
                svg = out/f'{filename}-{mode}.svg'
                fig.savefig(svg,facecolor=bg)
                svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
                if mode=='light':fig.savefig(out/f'{filename}.png',dpi=140,facecolor=bg)
                plt.close(fig)
