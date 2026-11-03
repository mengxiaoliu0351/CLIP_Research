"""Generate presentation figures from saved results; never runs a model."""
import argparse
import json
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':8,
                     'pdf.fonttype':42,'ps.fonttype':42})
GREEN='#17823b'
ORANGE='#d55e00'
GRAY='#333333'

def save(fig,name):
    for ext in ('pdf','png'):
        fig.savefig(OUT/f'{name}.{ext}',dpi=300,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def method_figure():
    fig,ax=plt.subplots(figsize=(7.2,2.0))
    fig.subplots_adjust(left=.01,right=.99,bottom=.03,top=.97)
    ax.set_xlim(-.15,8.35); ax.set_ylim(-.60,2.35); ax.axis('off')
    def box(x,y,w,h,label,trainable=False):
        patch=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.035',
            facecolor='#fff0e8' if trainable else '#edf2f5',
            edgecolor=ORANGE if trainable else '#455a64',linewidth=1)
        ax.add_patch(patch)
        ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=7.8)
    def arrow(x0,y0,x1,y1):
        ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1),arrowstyle='-|>',mutation_scale=9,linewidth=.85,color='#455a64'))
    box(0,1.35,.8,.65,'RGB\nimage')
    box(1.2,1.35,2.0,.65,'Image encoder\nViT-B/32 (frozen)')
    box(3.6,1.35,1.35,.65,'Visual projection\n(frozen)')
    box(5.35,1.35,.8,.65,'Image\nembedding\n(unit norm)')
    box(0,.05,.8,.65,'Caption\ntokens')
    box(1.2,.05,2.0,.65,'Text encoder\nfrozen base + Q/V LoRA',True)
    box(3.6,.05,1.35,.65,'Text projection\n(trainable)',True)
    box(5.35,.05,.8,.65,'Text\nembedding\n(unit norm)')
    for y in (1.675,.375):
        for a,b in ((.84,1.15),(3.24,3.55),(4.99,5.3)):
            arrow(a,y,b,y)
    box(6.7,.79,1.4,.75,'Cosine matrix\n+ contrastive loss')
    arrow(6.2,1.675,6.66,1.34)
    arrow(6.2,.375,6.66,.99)
    ax.text(2.5,-.36,'Trainable in C: 24 text Q/V LoRA modules and text projection',
            ha='center',fontsize=7.5,color=ORANGE)
    ax.text(4.3,2.20,'Image features are cached for training',ha='center',fontsize=7.3)
    save(fig,'method')

def tile(path):
    with Image.open(path) as image:
        image=image.convert('RGB')
        return ImageOps.pad(image,(360,260),method=Image.Resampling.LANCZOS,color='white')

def t2i_figure(cases,images):
    selected=[next(c for c in cases if c['direction']=='T2I' and c['case']==kind)
              for kind in ('lora_top1_improvement','lora_top5_failure')]
    fig=plt.figure(figsize=(7.2,3.25))
    grid=fig.add_gridspec(4,6,height_ratios=[.32,1,.32,1],hspace=.18,wspace=.09)
    for row,case in enumerate(selected):
        heading=fig.add_subplot(grid[row*2,:]); heading.axis('off')
        a=case['models']['A_baseline']['ground_truth_rank']
        c=case['models']['C_seed42']['ground_truth_rank']
        heading.text(0,.85,f"({'a' if row==0 else 'b'}) Query: {case['query_caption']}\nGT image rank: A={a}, C={c}; query index={case['query_index']}",
                     va='top',fontsize=7.6,transform=heading.transAxes)
        results=[{'filename':case['ground_truth_filename'],'is_ground_truth':True,'rank':0,'similarity':None}]+case['models']['C_seed42']['top5']
        for col,result in enumerate(results):
            ax=fig.add_subplot(grid[row*2+1,col]); ax.axis('off')
            ax.imshow(tile(images/result['filename']))
            title='GT image' if col==0 else f"#{result['rank']}  {result['similarity']:.3f}"+(' [GT]' if result['is_ground_truth'] else '')
            ax.set_title(title,fontsize=6.8,color=GREEN if result['is_ground_truth'] else GRAY,pad=2)
            if result['is_ground_truth']:
                ax.add_patch(Rectangle((0,0),359,259,fill=False,edgecolor=GREEN,linewidth=1))
    save(fig,'qualitative_t2i')

def i2t_figure(cases,images):
    selected=[next(c for c in cases if c['direction']=='I2T' and c['case']==kind)
              for kind in ('lora_top1_improvement','lora_top5_failure')]
    fig=plt.figure(figsize=(7.2,3.9))
    for row,case in enumerate(selected):
        bottom=.51 if row==0 else .01
        a=case['models']['A_baseline']['best_ground_truth_rank']
        c=case['models']['C_seed42']['best_ground_truth_rank']
        fig.text(.01,bottom+.46,
                 f"({'a' if row==0 else 'b'}) Image-to-text: best GT rank A={a}, C={c}; query index={case['query_index']}",
                 fontsize=8,va='top')
        ax=fig.add_axes([.01,bottom+.15,.18,.27]); ax.axis('off')
        ax.imshow(tile(images/case['query_filename']))
        example=min(case['ground_truth_captions'],key=len)
        fig.text(.01,bottom+.135,'One GT caption:\n'+textwrap.fill(example,width=25),
                 fontsize=6.8,va='top',color=GREEN)
        ax=fig.add_axes([.22,bottom+.025,.77,.375]); ax.axis('off')
        height_pt=.375*3.9*72
        strings=[]
        for result in case['models']['C_seed42']['top5']:
            prefix=f"{result['rank']}. "+('[GT] ' if result['is_ground_truth'] else '')+f"{result['similarity']:.3f}: "
            strings.append((textwrap.fill(prefix+result['caption'],width=103),result['is_ground_truth']))
        lines=sum(s.count('\n')+1 for s,_ in strings)
        fontsize=min(7.8,height_pt/(lines*1.2+5*.65))
        assert fontsize>=7.0
        y=.99
        for text,positive in strings:
            ax.text(0,y,text,va='top',fontsize=fontsize,linespacing=1.2,
                    color=GREEN if positive else GRAY,transform=ax.transAxes)
            y-=((text.count('\n')+1)*fontsize*1.2+fontsize*.65)/height_pt
        assert y>=-.04
    save(fig,'qualitative_i2t')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--images',type=Path,help='Original Flickr30k JPEG directory; required for qualitative figures')
    args=parser.parse_args()
    method_figure()
    if args.images:
        cases=json.loads((ROOT/'data/qualitative_cases.json').read_text(encoding='utf-8'))['cases']
        t2i_figure(cases,args.images)
        i2t_figure(cases,args.images)
    print('Presentation figures generated from real saved examples; no model inference.')

if __name__=='__main__':
    main()
