#!/usr/bin/env python3
"""Build normalized drafts from raw extraction and curated configs; never reads canonical taxonomy."""
from __future__ import annotations
import json,re
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'internal-content/0580/syllabus'; RAW=BASE/'extraction/raw-syllabus-points.json'; OUT=BASE/'drafts'; CONFIG=ROOT/'config'
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def normalize(s): return re.sub(r'[ \t]+',' ',s.replace('\x07','')).strip()
def main():
 OUT.mkdir(parents=True,exist_ok=True); raw=load(RAW)['records']; pointcfg=load(CONFIG/'0580-atomic-skills.json')['points']; defs=load(CONFIG/'0580-skill-definitions.json')['skills']; refs=defaultdict(list); points=[]
 for r in raw:
  ids=pointcfg.get(r['rawSourceId'],{}).get('atomicSkills',[]); placeholder='Extended content only' in r['rawTitle'] or 'Extended content only' in r['rawStatement']; issues=list(r['extractionIssues']); conf=.97 if not issues else .85
  p={'id':r['rawSourceId'],'officialCode':r['rawSourceId'],'tier':r['tier'],'officialTitle':normalize(r['rawTitle']),'officialStatement':normalize(r['rawStatement']) or 'Extended content only.','notes':[normalize(r['rawNotes'])] if r['rawNotes'] else [],'examplesFromSyllabus':[],'extendedOnlyPlaceholder':placeholder,'atomicSkillIds':ids,'extraction':{'status':'clean' if not issues else 'needs-review','confidence':conf,'rawSourceId':r['rawSourceId'],'method':'coordinate-table-reconstruction','issues':issues,'verifiedBy':None,'verifiedAt':None},'review':{'status':'pending-review','notes':''}}
  points.append(p)
  for s in ids: refs[s].append(p['id'])
 skills=[dict({'id':s,'syllabusPointIds':sorted(refs[s]),'origin':'lattice-derived','review':{'status':'pending-review','notes':''}},**d) for s,d in defs.items() if refs[s]]
 dump(OUT/'syllabus-points.draft.json',{'schemaVersion':'1.0','syllabusPoints':points}); dump(OUT/'atomic-skills.draft.json',{'schemaVersion':'1.0','atomicSkills':skills}); dump(OUT/'core-extended-map.draft.json',load(CONFIG/'0580-core-extended-map.json'))
 print(f'Built drafts from {len(raw)} raw records and curated configs; canonical taxonomy was not read')
if __name__=='__main__': main()
