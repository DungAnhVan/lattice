#!/usr/bin/env python3
"""Coordinate-aware raw table extraction; writes extraction/ only."""
from __future__ import annotations
import json,re
from datetime import datetime,timezone
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'internal-content/0580/syllabus'; OUT=BASE/'extraction'; PDF=BASE/'sources/2025-2027-syllabus.pdf'
HEADER=re.compile(r'^([CE][1-9]\.\d+)\s+(.+?)(?:\s+Notes and examples)?\s*$',re.S)
def dump(n,x): (OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def clean(s): return re.sub(r'[ \t]+',' ',s.replace('\x07','')).strip()
def main():
 OUT.mkdir(parents=True,exist_ok=True); doc=fitz.open(PDF); pages=[]; records={}
 for pi,page in enumerate(doc):
  blocks=[]
  for b in page.get_text('blocks'):
   x0,y0,x1,y1,text,*_=b; blocks.append({'x0':round(x0,2),'y0':round(y0,2),'x1':round(x1,2),'y1':round(y1,2),'text':text})
  pages.append({'page':pi+1,'width':page.rect.width,'height':page.rect.height,'blocks':blocks})
  if pi+1<12: continue
  headers=[]
  for i,b in enumerate(blocks):
   m=HEADER.match(clean(b['text']))
   if m and b['x0']<100: headers.append((i,m.group(1),m.group(2).replace('Notes and examples','').strip(),b))
  for pos,(i,code,title,h) in enumerate(headers):
   if code in records: continue
   yend=headers[pos+1][3]['y0'] if pos+1<len(headers) else 790; row=[b for b in blocks if b['y0']>=h['y0'] and b['y0']<yend and b['y0']<790]
   left=[b for b in row[1:] if b['x0']<300]; right=[b for b in row[1:] if b['x0']>=300]
   statement='\n'.join(clean(b['text']) for b in left).strip(); notes='\n'.join(clean(b['text']) for b in right).strip(); issues=[]
   if not statement: issues.append('No left-column statement reconstructed.')
   records[code]={'rawSourceId':code,'page':pi+1,'tier':'core' if code[0]=='C' else 'extended','boundingRegions':[{'page':pi+1,'x0':min(b['x0'] for b in row),'y0':min(b['y0'] for b in row),'x1':max(b['x1'] for b in row),'y1':max(b['y1'] for b in row)}],'rawTitle':title,'rawStatement':statement,'rawNotes':notes,'rawBlocks':row,'extractionIssues':issues}
 doc.close(); rows=[records[k] for k in sorted(records,key=lambda x:(x[0],int(x[1]),int(x.split('.')[1])))]
 dump('raw-pages.json',{'schemaVersion':'1.0','pages':pages}); dump('raw-syllabus-points.json',{'schemaVersion':'2.0','records':rows}); dump('extraction-metadata.json',{'source':'../sources/2025-2027-syllabus.pdf','method':'PyMuPDF coordinate-table-reconstruction','pageNumbering':'one-based','extractedAt':datetime.now(timezone.utc).isoformat(),'pageCount':len(pages),'recordCount':len(rows)})
 print(f'Extracted {len(pages)} pages and {len(rows)} complete raw point records')
 return 0 if len(rows)==144 else 1
if __name__=='__main__': raise SystemExit(main())
