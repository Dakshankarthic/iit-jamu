from pathlib import Path
import json
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'ocr_results/segmentation'; OUT.mkdir(exist_ok=True)
# Layouts reviewed against all 68 source scans. Each pair is the normalized
# top/bottom of the left and right narrative text columns, excluding artwork.
BANDS={
7:(.35,.89,.35,.89),8:(.50,.94,.10,.94),9:(.08,.52,.08,.52),10:(.08,.72,.08,.72),11:(.52,.89,.52,.89),
12:(.49,.90,.08,.90),13:(.08,.94,.53,.94),14:(.08,.55,.08,.55),15:(.08,.55,.08,.55),16:(.52,.94,.09,.94),
17:(.08,.94,.49,.94),18:(.08,.68,.08,.68),20:(.52,.94,.10,.94),21:(.08,.92,.51,.92),22:(.50,.92,.08,.92),
23:(.08,.90,.49,.90),24:(.50,.91,.08,.91),25:(.08,.71,.08,.71),27:(.39,.89,.39,.89),28:(.08,.52,.08,.52),
29:(.08,.52,.08,.52),30:(.52,.94,.08,.94),31:(.08,.75,.08,.75),32:(.375,.90,.375,.90),33:(.08,.91,.56,.91),
34:(.05,.62,.05,.62),39:(.35,.88,.35,.88),40:(.505,.91,.08,.91),41:(.08,.76,.08,.76),43:(.37,.90,.37,.90),
44:(.55,.93,.08,.93),45:(.044,.67,.044,.67),46:(.40,.92,.40,.92),47:(.08,.54,.08,.54),48:(.08,.72,.08,.72),
49:(.40,.88,.40,.88),50:(.08,.61,.08,.61),51:(.46,.89,.46,.89),52:(.46,.91,.08,.91),53:(.08,.92,.49,.92),
54:(.50,.90,.08,.90),55:(.08,.92,.51,.92),56:(.54,.92,.08,.92),58:(.08,.61,.08,.61),59:(.38,.89,.38,.89),
60:(.48,.92,.08,.92),61:(.09,.92,.50,.92),62:(.50,.92,.10,.92),63:(.07,.71,.07,.71)}
# Alternating comic panels follow panel order, not whole-page column order.
PANELS={35:[(.59,.052,.91,.325),(.065,.38,.38,.615),(.58,.718,.91,.925)],
36:[(.62,.10,.94,.305),(.10,.38,.408,.635),(.62,.712,.94,.94)],
37:[(.065,.082,.395,.305),(.599,.40,.925,.627),(.069,.69,.398,.945)],
38:[(.618,.061,.937,.325),(.093,.379,.414,.635),(.616,.70,.947,.945)]}

def groups(positions,gap):
 result=[]
 for y in positions:
  if not result or y-result[-1][-1]>gap: result.append([int(y)])
  else: result[-1].append(int(y))
 return result

summary=[]
for n in sorted(set(BANDS)|set(PANELS)):
 stem=f'Chanda_Mama_{n:02d}'; rgb=np.asarray(Image.open(ROOT/'image'/f'{stem}.jpg').convert('RGB'));h,w=rgb.shape[:2]
 gray=np.asarray(Image.fromarray(rgb).convert('L')); dark=gray<110
 # Choose the sustained whitespace gutter using the portion containing both columns.
 if n in BANDS:
  a,b,c,d=BANDS[n]; ys=int(max(a,c)*h);ye=int(min(b,d)*h)
  projection=dark[ys:ye].sum(axis=0).astype(float)
  width=max(7,int(w*.009)); smooth=np.convolve(projection,np.ones(width)/width,mode='same')
  lo,hi=int(w*.47),int(w*.54);mid=lo+int(np.argmin(smooth[lo:hi]))
  # Protect all text by locating the edges of the blank central gutter.
  limit=max(3,(ye-ys)*.025);left=mid;right=mid
  while left>lo and smooth[left]<limit:left-=1
  while right<hi-1 and smooth[right]<limit:right+=1
  if right-left<w*.004:left,right=mid-3,mid+3
  else:
   left=min(mid-2,left+width//2+4)
   right=max(mid+2,right-width//2-4)
  rects=[('left',int(w*.065),int(a*h),left,int(b*h)),('right',right,int(c*h),int(w*.945),int(d*h))]
  mode='left column top-to-bottom, then right column top-to-bottom'
 else:
  rects=[(f'panel-{i}',int(x*w),int(y*h),int(r*w),int(b*h)) for i,(x,y,r,b) in enumerate(PANELS[n],1)]
  mode='alternating panel text blocks top-to-bottom'
 lines=[]
 for label,x0,y0,x1,y1 in rects:
  block=dark[y0:y1,x0:x1].copy()
  # Remove persistent vertical frame strokes before grouping horizontal rows.
  block[:, block.mean(axis=0)>.55]=False
  counts=block.sum(axis=1)
  occupied=np.flatnonzero(counts>max(10,(x1-x0)*.015))+y0
  for g in groups(occupied,max(7,int(h*.0042))):
   if g[-1]-g[0]<h*.004:continue
   top=max(y0,g[0]-5);bottom=min(y1,g[-1]+6)
   if bottom-top>h*.05: # Large connected areas are artwork or a border, never text lines.
    continue
   xs=np.flatnonzero(dark[top:bottom,x0:x1].sum(axis=0)>=3)
   if not len(xs):continue
   l=max(x0,x0+int(xs[0])-4);r=min(x1,x0+int(xs[-1])+5)
   lines.append({'id':f'{label}-{sum(q["column"]==label for q in lines)+1:02d}','column':label,'reading_order':len(lines)+1,
                 'bbox':[l,top,r,bottom],'boundary':[[l,top],[r,top],[r,bottom],[l,bottom]],'text':None,'requires_recognition':True})
 assert lines,stem
 assert all(0<=l['bbox'][0]<l['bbox'][2]<=w and 0<=l['bbox'][1]<l['bbox'][3]<=h for l in lines)
 if n in BANDS:
  assert all(l['bbox'][2]<=left if l['column']=='left' else l['bbox'][0]>=right for l in lines)
  assert set(l['column'] for l in lines)=={'left','right'}
 result={'source_image':f'image/{stem}.jpg','image_size':[w,h],'method':'manually reviewed layout blocks; column-constrained ink projection',
         'reading_order':mode,'status':'segmentation only; recognition pending','blocks':[{'column':label,'bbox':[x,y,r,b]} for label,x,y,r,b in rects],'lines':lines}
 (OUT/f'{stem}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 shapes=[]
 for l in lines:
  x,y,r,b=l['bbox'];color='#007aff' if l['column'] in ('left','panel-1','panel-3') else '#ed5800'
  shapes.append(f'<rect x="{x}" y="{y}" width="{r-x}" height="{b-y}" fill="{color}" fill-opacity=".06" stroke="{color}" stroke-width="3"/><text x="{x}" y="{y-2}" fill="{color}" font-size="24">{l["reading_order"]}</text>')
 for label,x,y,r,b in rects:
  shapes.append(f'<rect x="{x}" y="{y}" width="{r-x}" height="{b-y}" fill="none" stroke="#159b42" stroke-dasharray="12 8" stroke-width="4"/>')
 html=f'<!doctype html><meta charset="utf-8"><title>{stem} segmentation</title><style>body{{font-family:system-ui}}svg{{width:100%;max-width:1100px}}</style><h2>{stem}: corrected segmentation</h2><p>{mode}. OCR text has not been rerun.</p><svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"><image href="../../image/{stem}.jpg" width="{w}" height="{h}"/>'+''.join(shapes)+'</svg>'
 (OUT/f'{stem}.html').write_text(html)
 summary.append({'page':n,'lines':len(lines),'layout':mode,'columns':{label:sum(l['column']==label for l in lines) for label,*_ in rects}})
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
links=''.join(f'<li><a href="segmentation/Chanda_Mama_{s["page"]:02d}.html">Page {s["page"]:02d}</a> — {s["lines"]} line regions; {s["columns"]}</li>' for s in summary)
(OUT.parent/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Corrected column segmentation</title><h1>Corrected column segmentation</h1><p>49 narrative two-column pages and 4 alternating-panel pages. Green: text block bounds. Blue/orange: independent line regions and reading order. OCR recognition pending. Single-column pages, covers, and vocabulary tables are excluded.</p><ul>'+links+'</ul>')
print(f'Generated {len(summary)} page layouts, {sum(s["lines"] for s in summary)} line regions')
for s in summary:print(s['page'],s['columns'])
