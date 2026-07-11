#!/usr/bin/env python3
"""Build complete drafts from extraction and explicit configs; canonical taxonomy is never read."""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'internal-content/0580/syllabus'; OUT=B/'drafts'; C=ROOT/'config'; TOPICS={1:'number',2:'algebra-and-graphs',3:'coordinate-geometry',4:'geometry',5:'mensuration',6:'trigonometry',7:'transformations-and-vectors',8:'probability',9:'statistics'}; TOPIC_LABELS={1:'Number',2:'Algebra and graphs',3:'Coordinate geometry',4:'Geometry',5:'Mensuration',6:'Trigonometry',7:'Transformations and vectors',8:'Probability',9:'Statistics'}
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
 OUT.mkdir(parents=True,exist_ok=True); raw=load(B/'extraction/raw-syllabus-points.json')['records']; pcfg=load(C/'0580-atomic-skills.json')['points']; defs=load(C/'0580-skill-definitions.json')['skills']; clauses=load(C/'0580-syllabus-clauses.json')['points']; refs=defaultdict(list); points=[]
 for r in raw:
  pid=r['rawSourceId']; placeholder=pid not in pcfg; title=r['rawTitle']; statement=r['rawStatement'] or 'Extended content only.'
  if pid=='E6.6': title='Pythagoras’ theorem and trigonometry in 3D'
  p={'id':pid,'officialCode':pid,'tier':r['tier'],'topicId':TOPICS[int(pid[1])],'officialTitle':title,'officialStatement':statement,'notes':[r['rawNotes']] if r['rawNotes'] else [],'examplesFromSyllabus':[],'extendedOnlyPlaceholder':placeholder,'sourceReferences':[{'page':r['page'],'section':f"{r['tier'].title()} subject content / {TOPIC_LABELS[int(pid[1])]}",'tableRow':pid}],'atomicSkillIds':pcfg.get(pid,{}).get('atomicSkills',[]),'syllabusCode':'0580','prerequisiteSyllabusPointIds':[],'relatedSyllabusPointIds':[],'origin':'official-syllabus','extraction':{'status':'needs-review' if r['extractionIssues'] else 'clean','confidence':r['confidence'],'confidenceBasis':r['confidenceBasis'],'signals':r['signals'],'rawSourceId':pid,'method':'coordinate-table-reconstruction','issues':r['extractionIssues'],'verifiedBy':None,'verifiedAt':None},'review':{'status':'pending-review','notes':''}}
  if not placeholder and pid not in clauses: raise SystemExit(f'Missing clause config for {pid}')
  points.append(p)
  for s in p['atomicSkillIds']: refs[s].append(pid)
 skills=[]
 for sid,d in sorted(defs.items()):
  pids=sorted(refs[sid]); topics=sorted({TOPICS[int(x[1])] for x in pids}); skills.append({'id':sid,'label':d['label'],'description':d['description'],'topicIds':topics,'syllabusPointIds':pids,'conceptIds':d['conceptIds'],'skillGroupIds':d['skillGroupIds'],'action':d['action'],'difficulty':{'minimumTier':'core' if any(x[0]=='C' for x in pids) else 'extended','relativeLevel':d['relativeLevel']},'prerequisiteSkillIds':d['prerequisiteSkillIds'],'relatedSkillIds':d['relatedSkillIds'],'origin':'lattice-derived','sourceBasis':[{'syllabusPointId':x,'reason':'Explicit clause mapping.'} for x in pids],'review':{'status':'pending-review','notes':''}})
 dump(OUT/'syllabus-points.draft.json',{'schemaVersion':'1.0','syllabusPoints':points}); dump(OUT/'atomic-skills.draft.json',{'schemaVersion':'1.0','atomicSkills':skills}); dump(OUT/'core-extended-map.draft.json',load(C/'0580-core-extended-map.json')); print(f'Built complete drafts from {len(raw)} raw records and explicit configs; canonical taxonomy was not read')
if __name__=='__main__': main()
