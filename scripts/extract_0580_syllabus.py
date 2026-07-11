#!/usr/bin/env python3
"""Coordinate-aware raw PDF extraction. Writes extraction/ only."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'internal-content/0580/syllabus'; OUT=BASE/'extraction'; PDF=BASE/'sources/2025-2027-syllabus.pdf'
def dump(name,data): (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 OUT.mkdir(parents=True,exist_ok=True); doc=fitz.open(PDF); pages=[]; rows=[]
 for index,page in enumerate(doc):
  blocks=[]
  for b in page.get_text('blocks'):
   x0,y0,x1,y1,text,*_=b
   blocks.append({'x0':round(x0,2),'y0':round(y0,2),'x1':round(x1,2),'y1':round(y1,2),'text':text})
   first=text.strip().splitlines()[0] if text.strip() else ''
   if first.startswith(('C','E')) and len(first)>3 and first[1].isdigit() and '.' in first[:6]: rows.append({'rawSourceId':first.split()[0],'page':index+1,'headerBlock':blocks[-1]})
  pages.append({'page':index+1,'width':page.rect.width,'height':page.rect.height,'blocks':blocks})
 doc.close(); dump('raw-pages.json',{'schemaVersion':'1.0','pages':pages}); dump('raw-syllabus-points.json',{'schemaVersion':'1.0','rows':rows}); dump('extraction-metadata.json',{'source':'../sources/2025-2027-syllabus.pdf','method':'PyMuPDF coordinate blocks','pageNumbering':'one-based','extractedAt':datetime.now(timezone.utc).isoformat(),'pageCount':len(pages)})
 print(f'Extracted {len(pages)} pages and {len(rows)} row headers to extraction/ only')
if __name__=='__main__': main()
