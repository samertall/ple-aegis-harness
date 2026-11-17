"""Generate required Kaggle visuals. Plots never manufacture benchmark results.

Usage: python figures/build_figures.py
Provide metrics/dev_runs.csv, metrics/failures.csv with measured records first.
"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'
NAVY='#091529'; CYAN='#29bfd2'; CORAL='#ff9a78'; INK='#d9ebf7'; SOFT='#162c46'

def style(ax):
    ax.set_facecolor(NAVY)
    for spine in ax.spines.values(): spine.set_color('#42627d')
    ax.tick_params(colors=INK)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)
    ax.title.set_color(INK)
    ax.grid(True, color='#284765', alpha=.4)

def node(ax, x,y,w,h,title,sub,edge=CYAN):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012,rounding_size=0.02', facecolor=SOFT,edgecolor=edge,lw=1.8))
    ax.text(x+w/2,y+h*.61,title,ha='center',va='center',fontsize=13,color=INK,weight='bold')
    ax.text(x+w/2,y+h*.28,sub,ha='center',va='center',fontsize=9,color='#a1c4d3')

def arrow(ax,a,b,color=CYAN):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=20,color=color,lw=1.8))

def architecture():
    fig,ax=plt.subplots(figsize=(14,7.7),dpi=160)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
    ax.text(.5,.95,'AEGIS PLE  /  EVIDENCE-FIRST AGENT HARNESS',ha='center',color=INK,fontsize=19,weight='bold')
    ax.text(.5,.90,'Task protocol • autonomous model loop • engineering checks • delivered artifacts',ha='center',color='#a1c4d3',fontsize=11)
    node(ax,.02,.60,.18,.19,'PLE task','prompt + files')
    node(ax,.26,.60,.19,.19,'Evidence audit','inventory + specs')
    node(ax,.52,.60,.20,.19,'Reasoning agent','Claude Opus 5.5')
    node(ax,.79,.60,.19,.19,'Task tools','exec / files / MCP')
    arrow(ax,(.20,.69),(.26,.69))
    arrow(ax,(.45,.69),(.52,.69))
    arrow(ax,(.72,.69),(.79,.69))
    node(ax,.79,.25,.19,.18,'Engineering work','solvers + CAD + reports',CORAL)
    node(ax,.51,.25,.21,.18,'Independent checks','units / paths / integrity',CORAL)
    node(ax,.25,.25,.19,.18,'Deliverable gate','re-open + validate')
    node(ax,.02,.25,.18,.18,'PLE evaluator','done + file outputs')
    arrow(ax,(.88,.60),(.88,.43),CORAL)
    arrow(ax,(.79,.34),(.72,.34),CORAL)
    arrow(ax,(.51,.34),(.44,.34),CORAL)
    arrow(ax,(.25,.34),(.20,.34))
    ax.add_patch(FancyArrowPatch((.60,.43),(.61,.60),arrowstyle='-|>',connectionstyle='arc3,rad=.33',mutation_scale=17,color='#75aebd',lw=1.5,linestyle='--'))
    ax.text(.61,.48,'repair loop',color='#a1c4d3',fontsize=9,ha='left')
    ax.text(.5,.1,'All task I/O stays inside the evaluator protocol. No hidden-task answer templates.',ha='center',color='#a1c4d3',fontsize=10)
    fig.savefig(OUT/'01_architecture.png',dpi=180,bbox_inches='tight',facecolor=NAVY)
    plt.close(fig)

def records(name):
    p=ROOT/'metrics'/name
    with p.open(newline='',encoding='utf8') as f: return list(csv.DictReader(f))

def cost_plot():
    rows=[r for r in records('dev_runs.csv') if r.get('dev_score','').strip() and r.get('cost_usd','').strip()]
    fig,ax=plt.subplots(figsize=(11,6.8),dpi=160); fig.patch.set_facecolor(NAVY);style(ax)
    if rows:
        for r in rows:
            x,y=float(r['cost_usd']),float(r['dev_score'])
            ax.scatter(x,y,s=110,c=CORAL if 'verify' in r['variant'].lower() else CYAN,alpha=.9)
            ax.annotate(f"{r['model']} • {r['variant']}",(x,y),xytext=(7,7),textcoords='offset points',color=INK,fontsize=9)
        ax.set_ylabel('Mean score on 29 dev tasks (0–1)')
        ax.set_xlabel('Model inference cost per 29-task run (USD)')
        ax.set_ylim(0,1.03)
    else:
        ax.set_xlim(0,1);ax.set_ylim(0,1);ax.set_xlabel('Measured cost (USD)');ax.set_ylabel('Measured dev score')
        ax.text(.5,.55,'NO EVALUATION DATA YET',ha='center',va='center',color=CORAL,fontsize=20,weight='bold')
        ax.text(.5,.43,'Complete 29-task evaluations and metrics/dev_runs.csv',ha='center',color=INK,fontsize=11)
    ax.set_title('Stage 1 • Dev score versus inference cost',fontsize=16,pad=18)
    fig.savefig(OUT/'02_score_vs_cost.png',dpi=180,bbox_inches='tight',facecolor=NAVY)
    plt.close(fig)

def failures_plot():
    rows=[r for r in records('failures.csv') if r.get('failure_category','').strip()]
    counts={}
    for r in rows:
        cat=r['failure_category'].strip();counts[cat]=counts.get(cat,0)+1
    fig,ax=plt.subplots(figsize=(11,6.8),dpi=160);fig.patch.set_facecolor(NAVY);style(ax)
    if counts:
        labels=list(counts)
        values=[counts[k] for k in labels]
        ax.barh(labels,values,color=CYAN)
        ax.set_xlabel('Number of observed failures (dev set)')
        ax.invert_yaxis()
        ax.set_xlim(0,max(values)+2)
        for i,v in enumerate(values): ax.text(v+.1,i,str(v),color=INK,va='center')
    else:
        ax.set_xlim(0,1);ax.set_ylim(0,1)
        ax.text(.5,.55,'NO FAILURE AUDIT YET',ha='center',color=CORAL,fontsize=20,weight='bold')
        ax.text(.5,.43,'Classify observed failures in metrics/failures.csv',ha='center',color=INK,fontsize=11)
        ax.set_xticks([]);ax.set_yticks([])
    ax.set_title('Stage 1 • Failure breakdown on the public 29-task dev set',fontsize=16,pad=18)
    fig.savefig(OUT/'03_failure_breakdown.png',dpi=180,bbox_inches='tight',facecolor=NAVY)
    plt.close(fig)

if __name__ == '__main__':
    architecture();cost_plot();failures_plot()
    print('Generated architecture and two explicitly unscored figures in',OUT)
