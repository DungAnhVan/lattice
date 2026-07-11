#!/usr/bin/env python3
"""Coordinate-table extraction with reproducible evidence-based confidence."""
from __future__ import annotations
import json,re
from datetime import datetime,timezone
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'internal-content/0580/syllabus'; OUT=B/'extraction'; PDF=B/'sources/2025-2027-syllabus.pdf'; HEADER=re.compile(r'^([CE][1-9]\.\d+)\s+(.+?)(?:\s+Notes and examples)?\s*$',re.S); FOOT=('back to contents','cambridgeinternational.org','cambridge igcse mathematics')
def dump(n,x): (OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def norm(s): return re.sub(r'[ \t]+',' ',s.replace('\x07','')).strip()
def score(signals):
 value=1.0; basis=[]
 checks=[('codeDetected',.20,'code detected'),('titleDetected',.10,'title detected'),('statementDetected',.20,'statement detected')]
 for key,penalty,label in checks:
  if signals[key]: basis.append(label)
  else: value-=penalty; basis.append('missing '+label)
 for key,penalty,label in [('controlCharactersFound',.10,'control character found'),('footerLeakageFound',.10,'footer leakage found'),('detachedTitleFragmentFound',.10,'detached title fragment repaired'),('formulaLayoutAmbiguity',.07,'formula layout ambiguity'),('continuationAmbiguity',.08,'continuation ambiguity')]:
  if signals[key]: value-=penalty; basis.append(label)
 if signals['notesColumnDetected']: basis.append('notes column detected')
 else: value-=.03; basis.append('no notes-column block detected')
 return round(min(.99,max(0,value)),2),basis
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
   m=HEADER.match(norm(b['text']))
   if m and b['x0']<100: headers.append((i,m.group(1),m.group(2).replace('Notes and examples','').strip(),b))
  for pos,(_,code,title,h) in enumerate(headers):
   if code in records: continue
   yend=headers[pos+1][3]['y0'] if pos+1<len(headers) else 790; row=[b for b in blocks if b['y0']>=h['y0'] and b['y0']<yend and b['y0']<790]; left=[b for b in row[1:] if b['x0']<300]; right=[b for b in row[1:] if b['x0']>=300]; raw='\n'.join(b['text'] for b in left).strip(); statement=norm(raw); repaired=False
   detached=re.match(r'^((?:in|and|of)\s+[^\n]{1,24})\n(.+)$',statement,re.I|re.S)
   if detached and re.search(r'\b(carry|calculate|solve|use|construct|recognise|represent|find|draw)\b',detached.group(2),re.I): title=f"{title} {detached.group(1)}"; statement=detached.group(2).strip(); repaired=True
   title_continuation='\n' in title; title=' '.join(title.split())
   alltext=' '.join(b['text'] for b in row); formula=bool(re.search(r'(?:\n\s*[A-Za-z0-9]{1,2}\s*){4,}',raw)) or any(x in alltext for x in ('J\nL\nKK','N\nP\nOO'))
   signals={'codeDetected':True,'titleDetected':bool(title),'statementDetected':bool(statement),'notesColumnDetected':bool(right),'continuationMerged':repaired or title_continuation,'continuationAmbiguity':False,'controlCharactersFound':any(ord(c)<32 and c not in '\n\t' for c in alltext),'footerLeakageFound':any(x in alltext.lower() for x in FOOT),'detachedTitleFragmentFound':repaired or title_continuation,'formulaLayoutAmbiguity':formula,'codePageAligned':True}
   confidence,basis=score(signals); issues=[]
   if signals['controlCharactersFound']: issues.append('Control character removed during normalization.')
   if repaired or title_continuation: issues.append('Detached or multiline title fragment normalized into the title.')
   if formula: issues.append('Formula layout requires comparison with the source PDF.')
   if signals['footerLeakageFound']: issues.append('Footer leakage detected in row blocks.')
   records[code]={'rawSourceId':code,'page':pi+1,'tier':'core' if code[0]=='C' else 'extended','boundingRegions':[{'page':pi+1,'x0':min(b['x0'] for b in row),'y0':min(b['y0'] for b in row),'x1':max(b['x1'] for b in row),'y1':max(b['y1'] for b in row)}],'rawTitle':norm(title),'rawStatement':statement,'rawNotes':norm('\n'.join(b['text'] for b in right)),'rawBlocks':row,'signals':signals,'confidence':confidence,'confidenceBasis':basis,'extractionIssues':issues}
 doc.close(); rows=[records[k] for k in sorted(records,key=lambda x:(x[0],int(x[1]),int(x.split('.')[1])))]
 dump('raw-pages.json',{'schemaVersion':'1.0','pages':pages}); dump('raw-syllabus-points.json',{'schemaVersion':'3.0','records':rows}); dump('extraction-metadata.json',{'source':'../sources/2025-2027-syllabus.pdf','method':'PyMuPDF coordinate-table-reconstruction','confidenceModel':'signal penalties documented in scripts/extract_0580_syllabus.py','pageNumbering':'one-based','extractedAt':datetime.now(timezone.utc).isoformat(),'pageCount':len(pages),'recordCount':len(rows)})
 print(f"Extracted {len(rows)} records; issues={sum(bool(x['extractionIssues']) for x in rows)} below-0.95={sum(x['confidence']<.95 for x in rows)}")
 return 0 if len(rows)==144 else 1
if __name__=='__main__': raise SystemExit(main())
