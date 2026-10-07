from pathlib import Path
import argparse, csv, io, json, os, subprocess, time, html, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageOps

BASE=Path(__file__).resolve().parents[1]; SOURCE=BASE.parent; OUTPUT=BASE/'tesseract'; OUTPUT.mkdir(exist_ok=True)
for folder in ['text','json','pages']: (OUTPUT/folder).mkdir(exist_ok=True)
ENV=dict(os.environ,OMP_THREAD_LIMIT='1')

def recognize(n):
 started=time.monotonic();stem=f'Chanda_Mama_{n:02d}';source=SOURCE/'image'/f'{stem}.jpg'
 image=Image.open(source).convert('RGB');w,h=image.size
 segmented=BASE/'segmentation'/f'{stem}.json'
 if segmented.exists():
  layout=json.loads(segmented.read_text());blocks=layout['blocks'];mode=layout['reading_order'];psm=6
 else:
  blocks=[{'column':'page','bbox':[0,0,w,h]}];mode='Tesseract automatic page layout';psm=3
 languages='eng+san' if n in (3,65,66) else 'san'
 all_lines=[];block_results=[];warnings=[]
 for block in blocks:
  x,y,r,b=block['bbox']; crop=image.crop((x,y,r,b)).convert('L')
  # White padding gives line detection space at each text-block edge.
  crop=ImageOps.expand(crop,border=16,fill=255)
  payload=io.BytesIO();crop.save(payload,format='PNG')
  command=['tesseract','stdin','stdout','--tessdata-dir',str(BASE/'.cache/tessdata'),'-l',languages,'--psm',str(psm),'--dpi','300','-c','tessedit_create_tsv=1']
  process=subprocess.run(command,input=payload.getvalue(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=ENV,timeout=240)
  if process.returncode:raise RuntimeError(f'{stem}/{block["column"]}: {process.stderr.decode(errors="replace")}')
  if psm==3 and not any(row.get('level')=='5' and row.get('text','').strip() for row in csv.DictReader(io.StringIO(process.stdout.decode('utf-8')),delimiter='\t',quoting=csv.QUOTE_NONE)):
   # Covers and decorative pages need sparse-text detection when automatic
   # page layout returns no recognized words.
   command[command.index('--psm')+1]='11';psm=11
   process=subprocess.run(command,input=payload.getvalue(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=ENV,timeout=240)
   if process.returncode:raise RuntimeError(f'{stem}: sparse-text fallback failed')
  if process.stderr.strip():warnings.append(process.stderr.decode(errors='replace').strip())
  groups={}
  for row in csv.DictReader(io.StringIO(process.stdout.decode('utf-8')),delimiter='\t',quoting=csv.QUOTE_NONE):
   if row['level']!='5' or not row.get('text','').strip():continue
   key=(row['block_num'],row['par_num'],row['line_num']);groups.setdefault(key,[]).append(row)
  lines=[]
  for words in groups.values():
   text=' '.join(q['text'] for q in words)
   l=min(int(q['left']) for q in words)+x-16;t=min(int(q['top']) for q in words)+y-16
   right=max(int(q['left'])+int(q['width']) for q in words)+x-16;bottom=max(int(q['top'])+int(q['height']) for q in words)+y-16
   confidence=sum(float(q['conf'])*len(q['text']) for q in words)/sum(len(q['text']) for q in words)
   lines.append({'reading_order':len(all_lines)+len(lines)+1,'column':block['column'],'text':text,'bbox':[max(0,l),max(0,t),min(w,right),min(h,bottom)],'confidence':round(confidence,2),'confidence_scale':'0-100; character-weighted Tesseract word confidence'})
  block_results.append({**block,'text':'\n'.join(q['text'] for q in lines),'line_count':len(lines)})
  all_lines.extend(lines)
 text='\n\n'.join(q['text'] for q in block_results)
 result={'page':n,'source_image':'image/'+source.name,'engine':'Tesseract 5.5.0','languages':languages,'model':'tessdata_best/san; system eng','psm':psm,
         'reading_order':mode,'blocks':block_results,'lines':all_lines,'text':text,'warnings':warnings,
         'limitations':'Machine OCR, not proofread. Hand-selected text blocks may omit headings or marginal text; automatic layouts on covers and tables need review.'}
 (OUTPUT/'json'/f'{stem}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 (OUTPUT/'text'/f'{stem}.txt').write_text(text+'\n',encoding='utf-8')
 shapes=''.join(f'<rect x="{q["bbox"][0]}" y="{q["bbox"][1]}" width="{q["bbox"][2]-q["bbox"][0]}" height="{q["bbox"][3]-q["bbox"][1]}" fill="none" stroke="{"#007aff" if q["column"] in ("left","panel-1","panel-3") else "#ed5800"}" stroke-width="3"/>' for q in all_lines)
 parts=''.join('<h3>'+html.escape(q['column'])+'</h3><pre>'+html.escape(q['text'])+'</pre>' for q in block_results)
 page=f'<!doctype html><meta charset="utf-8"><title>{stem} new OCR</title><style>body{{font-family:system-ui}}main{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}svg{{width:100%}}pre{{white-space:pre-wrap;line-height:1.8;font-size:18px}}@media(max-width:800px){{main{{display:block}}}}</style><h1>{stem} — new OCR</h1><p>{html.escape(mode)}. Tesseract Sanskrit/English; unproofread.</p><main><svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"><image href="../../../image/{stem}.jpg" width="{w}" height="{h}"/>{shapes}</svg><article>{parts}</article></main>'
 (OUTPUT/'pages'/f'{stem}.html').write_text(page)
 confidences=[q['confidence'] for q in all_lines]
 return {'page':n,'line_count':len(all_lines),'characters':len(text),'mean_line_confidence':round(sum(confidences)/len(confidences),2) if confidences else None,'seconds':round(time.monotonic()-started,1),'blocks':len(blocks)}

parser=argparse.ArgumentParser();parser.add_argument('--pages',type=int,nargs='*',default=list(range(1,69)));parser.add_argument('--workers',type=int,default=4);args=parser.parse_args()
results=[];failed=[]
with ThreadPoolExecutor(max_workers=args.workers) as pool:
 futures={pool.submit(recognize,n):n for n in args.pages}
 for future in as_completed(futures):
  n=futures[future]
  try:
   result=future.result();results.append(result);print('PASS',result,flush=True)
  except Exception as e:
   failed.append({'page':n,'error':str(e)});print('FAIL',n,str(e),flush=True)
results.sort(key=lambda q:q['page'])
(OUTPUT/'run-summary.json').write_text(json.dumps({'requested_pages':args.pages,'completed':results,'failed':failed,'model_sha256':hashlib.sha256((BASE/'.cache/tessdata/san.traineddata').read_bytes()).hexdigest()},indent=2)+'\n')
if len(args.pages)==68 and not failed:
 combined='\n\n'.join(f'===== PAGE {n:02d} =====\n'+(OUTPUT/'text'/f'Chanda_Mama_{n:02d}.txt').read_text() for n in range(1,69))
 (OUTPUT/'combined_transcription_68_pages.txt').write_text(combined)
 links=''.join(f'<li><a href="pages/Chanda_Mama_{q["page"]:02d}.html">Page {q["page"]:02d}</a> — {q["line_count"]} OCR lines</li>' for q in results)
 (OUTPUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>New column-aware OCR</title><h1>New column-aware OCR: 68 pages</h1><p>Tesseract Sanskrit/English. 53 pages use separate text columns or comic panels; other pages use automatic layout. Text is unproofread; some headings and marginal text may be omitted.</p><ul>'+links+'</ul>')
if failed:raise SystemExit(1)
