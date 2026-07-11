#!/usr/bin/env python3
"""Apply already-reviewed Gate 1C configs; never constructs descriptions, groups, clauses, or mapping categories."""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'internal-content/0580/syllabus'; T=B/'taxonomy'; C=ROOT/'config'
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
 pointsdoc=load(T/'syllabus-points.json'); points=pointsdoc['syllabusPoints']; pointcfg=load(C/'0580-atomic-skills.json')['points']; defs=load(C/'0580-skill-definitions.json')['skills']; groupcfg=load(C/'0580-skill-groups.json')['groups']; raw={x['rawSourceId']:x for x in load(B/'extraction/raw-syllabus-points.json')['records']}; refs=defaultdict(list); topic={p['id']:p['topicId'] for p in points}; tier={p['id']:p['tier'] for p in points}
 for p in points:
  p['atomicSkillIds']=pointcfg.get(p['id'],{}).get('atomicSkills',[]); r=raw[p['id']]
  # E6.6 was repaired from its coordinate evidence; all identity/provenance fields stay canonical.
  if p['id']=='E6.6': p['officialTitle']='Pythagoras’ theorem and trigonometry in 3D'; p['officialStatement']=r['rawStatement']
  p['extraction']={'status':'needs-review' if r['extractionIssues'] else 'clean','confidence':r['confidence'],'confidenceBasis':r['confidenceBasis'],'signals':r['signals'],'rawSourceId':p['id'],'method':'coordinate-table-reconstruction','issues':r['extractionIssues'],'verifiedBy':None,'verifiedAt':None}
  for sid in p['atomicSkillIds']: refs[sid].append(p['id'])
 skills=[]
 for sid,d in sorted(defs.items()):
  pids=sorted(refs[sid]); skills.append({'id':sid,'label':d['label'],'description':d['description'],'topicIds':sorted({topic[x] for x in pids}),'syllabusPointIds':pids,'conceptIds':d['conceptIds'],'skillGroupIds':d['skillGroupIds'],'action':d['action'],'difficulty':{'minimumTier':'core' if any(tier[x]=='core' for x in pids) else 'extended','relativeLevel':d['relativeLevel']},'prerequisiteSkillIds':d['prerequisiteSkillIds'],'relatedSkillIds':d['relatedSkillIds'],'origin':'lattice-derived','sourceBasis':[{'syllabusPointId':x,'reason':'Mapped by an explicit reviewed clause in config/0580-syllabus-clauses.json.'} for x in pids],'review':{'status':'pending-review','notes':''}})
 groups=[{'id':gid,'label':g['label'],'description':g['description'],'topicIds':g['topicIds'],'syllabusPointIds':g['syllabusPointIds'],'atomicSkillIds':g['atomicSkillIds'],'origin':'lattice-derived','review':g['review']} for gid,g in sorted(groupcfg.items())]
 rel=[]
 for p in points:
  rel.append({'type':'topic-contains-syllabus-point','from':p['topicId'],'to':p['id'],'origin':'official-syllabus'})
  for s in p['atomicSkillIds']: rel.append({'type':'syllabus-point-requires-atomic-skill','from':p['id'],'to':s,'origin':'lattice-derived'})
 for s in skills:
  for parent in s['prerequisiteSkillIds']: rel.append({'type':'atomic-skill-prerequisite-of','from':parent,'to':s['id'],'origin':'lattice-derived'})
 for m in load(C/'0580-core-extended-map.json')['mappings']: rel.append({'type':'core-point-extended-by','from':m['corePointId'],'to':m['extendedPointId'],'origin':'lattice-derived','relationship':m['relationship']})
 dump(T/'syllabus-points.json',pointsdoc); dump(T/'atomic-skills.json',{'schemaVersion':'1.0','atomicSkills':skills}); dump(T/'skill-groups.json',{'schemaVersion':'1.0','skillGroups':groups}); dump(T/'relationships.json',{'schemaVersion':'1.0','relationships':rel}); print(f'Applied explicit configs: {len(points)} points, {len(skills)} skills, {len(groups)} groups')
if __name__=='__main__': main()
