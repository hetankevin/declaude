#!/usr/bin/env python3
"""Render the complete restored-v9 check using the established heatmap style."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evals/results/prose-repair/v9-restored-20'

def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap,TwoSlopeNorm,to_rgba
    from matplotlib.patches import Rectangle
    from matplotlib.cm import ScalarMappable
    assert json.loads((OUT/'coverage.json').read_text())['complete'],'No partial heatmap'
    s=json.loads((OUT/'summary.json').read_text())
    cmap=LinearSegmentedColormap.from_list('repair',['#b84a48','#f2f2f2','#1c5cab'],N=257)
    norm=TwoSlopeNorm(vmin=-100,vcenter=0,vmax=100)
    configs=['astra-high','sol-low','sonnet-high','all'];labels=['Astra\nhigh','Sol\nlow','Sonnet\nhigh','All']
    for theme in ('light','dark'):
        bg,fg=('white','#20252b') if theme=='light' else ('#1a1a19','#f0efec')
        with plt.rc_context({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none','svg.hashsalt':'restored-v9','text.color':fg,'axes.labelcolor':fg,'xtick.color':fg,'ytick.color':fg,'figure.facecolor':bg,'axes.facecolor':bg}):
            for section,metrics in [('categories',['nonproof','ordinary','research','argument','proof','control']),('dimensions',['meaning','naturalness','progression','voice','proof','overall'])]:
                fig=plt.figure(figsize=(11.2,5.8));ax=fig.add_axes([.19,.20,.77,.60])
                columns=[]
                for ri,ref in enumerate(('none','v4')):
                    for ci,(cfg,label) in enumerate(zip(configs,labels)):
                        x=ri*4.6+ci;columns.append((x,label))
                        for y,metric in enumerate(metrics):
                            cell=s[ref][cfg];stat=(cell['nonproof'] if metric=='nonproof' else cell['categories'][metric]) if section=='categories' else cell['dimensions'][metric]
                            v=stat['net_pp'] if stat else None;color=cmap(norm(v)) if v is not None else '#aaa'
                            ax.add_patch(Rectangle((x+.025,y+.025),.95,.95,facecolor=color,edgecolor='none'))
                            c=to_rgba(color);lum=.2126*c[0]+.7152*c[1]+.0722*c[2]
                            ax.text(x+.5,y+.5,'NA' if v is None else f'{v:+.1f}',ha='center',va='center',color='white' if lum<.5 else '#17212b',fontsize=10,fontweight='bold' if cfg=='all' else 'normal')
                    ax.text(ri*4.6+2,1.20,'Versus no skill' if ref=='none' else 'Versus v4',transform=ax.get_xaxis_transform(),ha='center',va='bottom',fontsize=11)
                ax.set_xlim(0,8.6);ax.set_ylim(6,0)
                ax.set_xticks([x+.5 for x,_ in columns],[label for _,label in columns]);ax.xaxis.tick_top();ax.tick_params(length=0,pad=8)
                ax.set_yticks([y+.5 for y in range(6)],[{'nonproof':'All prose','ordinary':'Ordinary prose','research':'Research prose'}.get(m,m.capitalize()) for m in metrics])
                ax.set_xlabel('Model and reasoning effort',labelpad=12);ax.set_ylabel('Writing category' if section=='categories' else 'Judge dimension',labelpad=12)
                for spine in ax.spines.values():spine.set_visible(False)
                cax=fig.add_axes([.31,.075,.53,.025]);bar=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation='horizontal',ticks=[-100,-50,0,50,100]);bar.set_label('Win rate − loss rate (percentage points)');bar.outline.set_edgecolor(fg)
                for ext in ('svg','png'):
                    p=OUT/f'{section}-{theme}.{ext}';fig.savefig(p,dpi=150,bbox_inches='tight',pad_inches=.12,metadata={'Date':None} if ext=='svg' else None)
                    if ext=='svg':p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
                plt.close(fig)
if __name__=='__main__':main()
