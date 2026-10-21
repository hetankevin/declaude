#!/usr/bin/env python3
"""Case outcomes for the targeted dev repair; untested cells stay blank."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evals/results/prose-repair/v10-targeted'
LABELS={'large-dev-a-06':'Drainage study','large-dev-a-08':'Worksheet study','large-dev-a-10':'Warning signs','large-dev-a-12':'Excluded runs','large-dev-a-14':'Conditional proof','large-dev-b-02':'Travel invitation','large-dev-b-06':'Library survey','large-dev-b-14':'Variance proof','large-dev-b-16':'Projection bound','large-dev-b-20':'Maintenance note'}
def main():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.colors import ListedColormap,BoundaryNorm
 from matplotlib.patches import Rectangle,Patch
 assert json.loads((OUT/'coverage.json').read_text())['outputs']==13
 plan=json.loads((OUT/'plan.json').read_text());selected={(cid,cfg) for cfg,ids in plan['selection'].items() for cid in ids}
 rows=json.loads((OUT/'observations.json').read_text());lookup={(r['case'],r['config'],r['reference']):r['outcome'] for r in rows}
 for theme in ['light','dark']:
  bg,fg=('white','#20252b') if theme=='light' else ('#1a1a19','#f0efec')
  colors={'win':'#1c5cab','tie':'#f2f2f2','loss':'#b84a48'}
  with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':'v10-targeted','text.color':fg,'axes.labelcolor':fg,'xtick.color':fg,'ytick.color':fg,'figure.facecolor':bg,'axes.facecolor':bg}):
   fig,ax=plt.subplots(figsize=(9,6.4));fig.subplots_adjust(left=.25,bottom=.18,top=.80,right=.98)
   columns=[]
   for ci,cfg in enumerate(['sol-low','sonnet-high']):
    for ri,ref in enumerate(['none','v4','v9-restored-dev']):
     x=ci*3.4+ri;columns.append((x,{'none':'No skill','v4':'v4','v9-restored-dev':'Restored v9'}[ref]))
     for y,cid in enumerate(LABELS):
      outcome=lookup.get((cid,cfg,ref));color=colors.get(outcome,bg)
      ax.add_patch(Rectangle((x+.025,y+.025),.95,.95,facecolor=color,edgecolor='none'))
      ax.text(x+.5,y+.5,{'win':'+1','tie':'0','loss':'−1'}.get(outcome,'?' if (cid,cfg) in selected else '—'),ha='center',va='center',color=('#17212b' if outcome=='tie' else 'white') if outcome else fg)
    ax.text(ci*3.4+1.5,1.16,['Sol low','Sonnet high'][ci],transform=ax.get_xaxis_transform(),ha='center',va='bottom',fontsize=12)
   ax.set_xlim(0,6.4);ax.set_ylim(10,0);ax.set_xticks([x+.5 for x,_ in columns],[s for _,s in columns]);ax.xaxis.tick_top();ax.set_yticks([i+.5 for i in range(10)],list(LABELS.values()));ax.tick_params(length=0,pad=8)
   ax.set_xlabel('Comparator',labelpad=10);ax.set_ylabel('Development case')
   for spine in ax.spines.values():spine.set_visible(False)
   leg=fig.legend(handles=[Patch(facecolor=c,label=k.capitalize()) for k,c in colors.items()],loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.60,.025))
   for text in leg.get_texts():text.set_color(fg)
   for ext in ['svg','png']:
    path=OUT/f'cases-{theme}.{ext}';fig.savefig(path,dpi=150,bbox_inches='tight',metadata={'Date':None} if ext=='svg' else None)
    if ext=='svg':path.write_text('\n'.join(s.rstrip() for s in path.read_text().splitlines())+'\n')
   plt.close(fig)
if __name__=='__main__':main()
