#!/usr/bin/env python3
"""One-time explicit Gate 1C promotion from reviewed configuration to canonical files."""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'internal-content/0580/syllabus'; TAX=BASE/'taxonomy'; CONFIG=ROOT/'config'
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
 pointsdoc=load(TAX/'syllabus-points.json'); points=pointsdoc['syllabusPoints']; mapping=load(CONFIG/'0580-atomic-skills.json')['points']; defs=load(CONFIG/'0580-skill-definitions.json')['skills']; refs=defaultdict(list); topics={p['id']:p['topicId'] for p in points}; tiers={p['id']:p['tier'] for p in points}
 for p in points:
  p['atomicSkillIds']=mapping.get(p['id'],{}).get('atomicSkills',[])
  # Coordinate reconstruction confidence: strong rows 0.97; formula-heavy/known layout ambiguity 0.90.
  issues=[]; conf=.97
  if p['id'] in {'E2.4','E2.10','E6.5'}: conf=.90; issues=['Mathematical formula layout requires teacher comparison with source PDF.']
  p['extraction']={'status':'needs-review' if issues else 'clean','confidence':conf,'rawSourceId':p['id'],'method':'coordinate-table-reconstruction','issues':issues,'verifiedBy':None,'verifiedAt':None}
  for s in p['atomicSkillIds']: refs[s].append(p['id'])
 skills=[]
 for sid,d in sorted(defs.items()):
  pids=sorted(refs[sid]); skills.append({'id':sid,'label':d['label'],'description':d['description'],'topicIds':sorted({topics[p] for p in pids}),'syllabusPointIds':pids,'conceptIds':d['conceptIds'],'skillGroupIds':d['skillGroupIds'],'action':d['action'],'difficulty':{'minimumTier':'core' if any(tiers[p]=='core' for p in pids) else 'extended','relativeLevel':d['relativeLevel']},'prerequisiteSkillIds':d['prerequisiteSkillIds'],'relatedSkillIds':d['relatedSkillIds'],'origin':'lattice-derived','sourceBasis':[{'syllabusPointId':p,'reason':'Explicit curated decomposition in config/0580-atomic-skills.json.'} for p in pids],'review':{'status':'pending-review','notes':''}})
 groupdata=defaultdict(lambda:{'topicIds':set(),'syllabusPointIds':set(),'atomicSkillIds':set()})
 for pid,v in mapping.items():
  for gid in v['skillGroupIds']:
   groupdata[gid]['topicIds'].add(topics[pid]); groupdata[gid]['syllabusPointIds'].add(pid); groupdata[gid]['atomicSkillIds'].update(v['atomicSkills'])
 groups=[{'id':gid,'label':gid.replace('-skills','').replace('-',' ').capitalize(),'topicIds':sorted(x['topicIds']),'syllabusPointIds':sorted(x['syllabusPointIds']),'atomicSkillIds':sorted(x['atomicSkillIds']),'origin':'lattice-derived','review':{'status':'pending-review','notes':''}} for gid,x in sorted(groupdata.items())]
 # Explicit pair config includes actual skill-set semantics rather than wording comparison.
 byid={p['id']:p for p in points}; oldmap=load(BASE/'indexes/core-extended-map.json')['mappings']; cats={(m['corePointId'],m['extendedPointId']):m['relationship'] for m in oldmap}; pairs=[]
 for c in [p for p in points if p['tier']=='core']:
  e=byid['E'+c['id'][1:]]; cs=set(c['atomicSkillIds']); es=set(e['atomicSkillIds']); category='extended-only' if c.get('extendedOnlyPlaceholder') else cats.get((c['id'],e['id']),'needs-review')
  pairs.append({'corePointId':c['id'],'extendedPointId':e['id'],'relationship':category,'sharedSkillIds':sorted(cs&es),'extendedOnlySkillIds':sorted(es-cs),'coreOnlySkillIds':sorted(cs-es),'basis':{'coreSummary':c['officialTitle'],'extendedAddition':'Explicit difference of curated atomic-skill sets.'},'review':{'status':'pending-review','notes':''}})
 dump(CONFIG/'0580-core-extended-map.json',{'schemaVersion':'1.0','mappings':pairs})
 rel=[]
 for p in points:
  rel.append({'type':'topic-contains-syllabus-point','from':p['topicId'],'to':p['id'],'origin':'official-syllabus'})
  for s in p['atomicSkillIds']: rel.append({'type':'syllabus-point-requires-atomic-skill','from':p['id'],'to':s,'origin':'lattice-derived'})
 for s in skills:
  for parent in s['prerequisiteSkillIds']: rel.append({'type':'atomic-skill-prerequisite-of','from':parent,'to':s['id'],'origin':'lattice-derived'})
 for m in pairs: rel.append({'type':'core-point-extended-by','from':m['corePointId'],'to':m['extendedPointId'],'origin':'lattice-derived','relationship':m['relationship']})
 dump(TAX/'syllabus-points.json',pointsdoc); dump(TAX/'atomic-skills.json',{'schemaVersion':'1.0','atomicSkills':skills}); dump(TAX/'skill-groups.json',{'schemaVersion':'1.0','skillGroups':groups}); dump(TAX/'relationships.json',{'schemaVersion':'1.0','relationships':rel}); dump(BASE/'indexes/core-extended-map.json',{'schemaVersion':'3.0','mappings':pairs})
 print(f'Applied curated taxonomy: {len(points)} points, {len(skills)} skills, {len(groups)} groups, {sum(len(s["prerequisiteSkillIds"]) for s in skills)} prerequisites')
if __name__=='__main__': main()
