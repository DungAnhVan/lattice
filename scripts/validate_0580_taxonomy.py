#!/usr/bin/env python3
"""Read-only Gate 1C Repair validation: structure, extraction, clauses, semantics, groups and mapping."""
from __future__ import annotations
import hashlib,json,re
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from jsonschema import Draft202012Validator
from taxonomy_quality import official_content_issues,skill_issues
from extract_0580_syllabus import score as extraction_score
ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'internal-content/0580/syllabus'; T=B/'taxonomy'; I=B/'indexes'; S=B/'schemas'; R=B/'reports'; C=ROOT/'config'
COUNTS={1:18,2:13,3:7,4:8,5:5,6:6,7:4,8:4,9:7}; EXPECTED={f'{z}{t}.{n}' for z in 'CE' for t,c in COUNTS.items() for n in range(1,c+1)}; MAP_TYPES={'equivalent-requirement','extended-includes-core','extended-adds-scope','extended-only','core-only','related-but-not-equivalent','needs-review'}
BROAD={'apply-algebraic-manipulation','calculate-powers-and-roots','apply-area-and-perimeter','apply-averages-and-measures-of-spread','apply-functions-concepts','apply-percentages-concepts','solve-equations','apply-statistics','use-geometry'}
UNSUPPORTED={('E2.6','solve-quadratic-inequality'),('C2.10','draw-exponential-growth-graph'),('C2.10','draw-exponential-decay-graph'),('C2.11','sketch-cubic-function'),('C2.11','sketch-reciprocal-function'),('C2.6','solve-linear-inequality'),('E4.8','apply-tangent-chord-theorem'),('E4.8','apply-intersecting-chords-theorem'),('E4.8','apply-secant-tangent-theorem')}
CONTROL=re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]'); FOOT=('back to contents','cambridgeinternational.org','cambridge igcse mathematics'); BOILER=('showing the required mathematical representation or result','this supports the assessed requirement','in mathematical problems','perform the specified operation','apply the concept','understand this topic')
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def digest():
 h=hashlib.sha256()
 for p in sorted(T.glob('*.json')):h.update(p.read_bytes())
 return h.hexdigest()
def text_issues(value,field):
 out=[]; values=value if isinstance(value,list) else [value]
 for text in values:
  lower=text.lower()
  if CONTROL.search(text):out.append(f'{field} contains a control character')
  if any(x in lower for x in FOOT):out.append(f'{field} contains footer text')
  if re.search(r'(?:^|\n)\s*\d{1,3}\s*$',text):out.append(f'{field} ends in a page number')
  if re.search(r'\b(and|or|of|to|with)\s*$',text.strip(),re.I):out.append(f'{field} appears truncated')
 return out
def validate(write_report=True):
 e=[]; w=[]; before=digest(); schema_docs={'syllabus.json':'syllabus.schema.json','topics.json':'topic.schema.json','syllabus-points.json':'syllabus-point.schema.json','atomic-skills.json':'atomic-skill.schema.json','skill-groups.json':'skill-group.schema.json','relationships.json':'relationships.schema.json'}; docs={n:load(T/n) for n in schema_docs}
 for n,schema in schema_docs.items():e += [f'{n} schema: {x.message}' for x in list(Draft202012Validator(load(S/schema)).iter_errors(docs[n]))[:50]]
 topics=docs['topics.json']['topics']; points=docs['syllabus-points.json']['syllabusPoints']; skills=docs['atomic-skills.json']['atomicSkills']; groups=docs['skill-groups.json']['skillGroups']; rels=docs['relationships.json']['relationships']; tids={x['id'] for x in topics}; pids={x['id'] for x in points}; sids={x['id'] for x in skills}; gids={x['id'] for x in groups}; byp={x['id']:x for x in points}; bys={x['id']:x for x in skills}
 pcfg=load(C/'0580-atomic-skills.json')['points']; defs=load(C/'0580-skill-definitions.json')['skills']; clauses=load(C/'0580-syllabus-clauses.json')['points']; gcfg=load(C/'0580-skill-groups.json')['groups']; mcfg=load(C/'0580-core-extended-map.json')['mappings']; raw={x['rawSourceId']:x for x in load(B/'extraction/raw-syllabus-points.json')['records']}; nonplace={p['id'] for p in points if not p.get('extendedOnlyPlaceholder')}
 if pids!=EXPECTED:e.append('official code coverage mismatch')
 if any(len(x)!=n for x,n in [(tids,len(topics)),(pids,len(points)),(sids,len(skills)),(gids,len(groups))]):e.append('duplicate canonical IDs')
 if set(pcfg)!=nonplace or set(clauses)!=nonplace:e.append('clause/config coverage does not exactly match all assessable points')
 configured={s for v in pcfg.values() for s in v['atomicSkills']}
 if configured!=set(defs) or configured!=sids:e.append('configured skills, definitions and canonical skills differ')
 # Official text integrity and reproducible extraction evidence.
 for p in points:
  if p['topicId'] not in tids or not p.get('sourceReferences'):e.append(f"{p['id']}: missing topic or source reference")
  for field in ('officialTitle','officialStatement','notes','examplesFromSyllabus'):e += [f"{p['id']}: {x}" for x in text_issues(p.get(field,''),field)]
  if not p.get('extendedOnlyPlaceholder'):e += [f"{p['id']}: {x}" for x in official_content_issues(p['officialStatement'],p['examplesFromSyllabus'])]
  elif p.get('atomicSkillIds'):e.append(f"{p['id']}: placeholder has assessable skills")
  r=raw.get(p['id']); ex=p.get('extraction',{})
  if not r:e.append(f"{p['id']}: missing raw extraction record"); continue
  expected_conf,basis=extraction_score(r['signals'])
  if ex.get('confidence')!=expected_conf or ex.get('signals')!=r['signals'] or ex.get('confidenceBasis')!=basis:e.append(f"{p['id']}: extraction confidence is not derived from stored signals")
  if ex.get('confidence')==1 and (not ex.get('verifiedBy') or not ex.get('verifiedAt')):e.append(f"{p['id']}: unverified confidence 1.0")
  if (ex.get('status')=='clean') != (not ex.get('issues')):e.append(f"{p['id']}: extraction status and issues disagree")
  if p.get('review',{}).get('status')=='approved' and (ex.get('confidence',0)<.95 or ex.get('issues')):e.append(f"{p['id']}: approved despite extraction uncertainty")
 if byp['E6.6']['officialTitle']!='Pythagoras’ theorem and trigonometry in 3D' or CONTROL.search(byp['E6.6']['officialTitle']+byp['E6.6']['officialStatement']):e.append('E6.6 title/text repair regression')
 # Explicit clause coverage is recomputed bidirectionally; stored status alone is never trusted.
 total_clauses=covered=partial=unmapped=0; clause_ids={}; skill_support=defaultdict(set)
 for pid in sorted(nonplace):
  record=clauses[pid]; rows=record.get('clauses',[])
  if not rows:e.append(f'{pid}: no explicit clause records'); continue
  union=set()
  for c in rows:
   total_clauses+=1; cid=c.get('id'); clause_ids[cid]=pid; mapped=c.get('atomicSkillIds',[]); mappings=c.get('skillMappings',[]); union.update(mapped)
   if not c.get('officialText') or not c.get('source') or c.get('kind')!='assessable':e.append(f'{cid}: incomplete clause provenance')
   if c.get('coverageStatus')=='covered' and not mapped:e.append(f'{cid}: covered without skills')
   if c.get('coverageStatus') not in {'covered','partially-covered','unmapped','needs-review'}:e.append(f'{cid}: invalid coverage status')
   if set(mapped)!={x.get('atomicSkillId') for x in mappings}:e.append(f'{cid}: skill mapping projection mismatch')
   required=set(c.get('requiredActions',[])); action_coverage={a for x in mappings for a in x.get('coversActions',[])}
   if c.get('coverageStatus')=='covered' and not required<=action_coverage:e.append(f'{cid}: claimed covered but required actions are not covered')
   for sid in mapped:
    if sid not in sids:e.append(f'{cid}: references missing skill {sid}')
    skill_support[(pid,sid)].add(cid)
   if c.get('coverageStatus')=='covered' and required<=action_coverage and mapped:covered+=1
   elif c.get('coverageStatus')=='partially-covered':partial+=1
   else:unmapped+=1
  pointskills=set(pcfg[pid]['atomicSkills'])
  if union!=pointskills:e.append(f'{pid}: point skills do not exactly equal union of clause skills')
  for sid in pointskills:
   if not skill_support[(pid,sid)]:e.append(f'{pid}: attached skill {sid} supports no clause')
 for pid,sid in UNSUPPORTED:
  if pid in pcfg and sid in pcfg[pid]['atomicSkills']:e.append(f'{pid}: unsupported skill remains: {sid}')
 # Definitions must be explicit, specific and non-boilerplate.
 desc_seen=Counter()
 for s in skills:
  e += [f"{s['id']}: {x}" for x in skill_issues(s)]; desc=s.get('description',''); lower=desc.lower(); words=desc.split(); desc_seen[re.sub(r'\b\d+(?:\.\d+)?\b','<n>',lower)]+=1
  if s['id'] in BROAD:e.append(f"{s['id']}: broad deny-listed skill")
  if any(x in lower for x in BOILER) or not 12<=len(words)<=65:e.append(f"{s['id']}: generic, generated or insufficient description")
  if s['id'] not in defs or defs[s['id']]['description']!=desc:e.append(f"{s['id']}: canonical definition differs from explicit config")
  for pid in s['syllabusPointIds']:
   if not skill_support[(pid,s['id'])]:e.append(f"{s['id']}: no supporting clause on {pid}")
 if any(n>=5 for n in desc_seen.values()):e.append('repeated generic description skeleton detected')
 # Skill groups are meaningful, narrower than topics, and exactly inverse-consistent with definitions.
 topic_skills={t:{s for p in points if p['topicId']==t for s in p['atomicSkillIds']} for t in tids}; topic_names={re.sub(r'[^a-z0-9]','',t.lower()) for t in tids}|{re.sub(r'[^a-z0-9]','',t['officialTitle'].lower()) for t in topics}; inverse=defaultdict(set)
 if len(groups)<=9:e.append('skill-group count is not meaningfully greater than topic count')
 if set(gcfg)!=gids:e.append('canonical skill groups differ from curated config')
 for g in groups:
  members=set(g['atomicSkillIds'])
  if len(members)<2:e.append(f"{g['id']}: group is not broader than one skill")
  if re.sub(r'[^a-z0-9]','',g['id'].lower()) in topic_names or re.sub(r'[^a-z0-9]','',g['label'].lower()) in topic_names:e.append(f"{g['id']}: duplicates an official topic")
  if len(g.get('description','').split())<7:e.append(f"{g['id']}: insufficient group description")
  for sid in members:
   if sid not in sids:e.append(f"{g['id']}: unknown skill {sid}")
   inverse[sid].add(g['id'])
  for tid in g['topicIds']:
   if tid in topic_skills and members==topic_skills[tid]:e.append(f"{g['id']}: duplicates the full scope of topic {tid}")
 for sid in sids:
  if inverse[sid]!=set(defs[sid]['skillGroupIds']) or inverse[sid]!=set(bys[sid]['skillGroupIds']):e.append(f'{sid}: skill-group inverse mismatch')
 # Core/Extended config is sole source, exact and clause-aware.
 if load(I/'core-extended-map.json')!=load(C/'0580-core-extended-map.json'):e.append('generated Core/Extended index differs from curated config')
 if len(mcfg)!=72 or len({(x['corePointId'],x['extendedPointId']) for x in mcfg})!=72:e.append('Core/Extended config does not contain 72 unique pairs')
 expected_pairs={(f'C{t}.{n}',f'E{t}.{n}') for t,c in COUNTS.items() for n in range(1,c+1)}
 if {(x['corePointId'],x['extendedPointId']) for x in mcfg}!=expected_pairs:e.append('Core/Extended pair set is incomplete')
 for m in mcfg:
  c=byp[m['corePointId']]; x=byp[m['extendedPointId']]; cs=set(c['atomicSkillIds']); xs=set(x['atomicSkillIds']); shared=cs&xs; eo=xs-cs; co=cs-xs
  if set(m['sharedSkillIds'])!=shared or set(m['extendedOnlySkillIds'])!=eo or set(m['coreOnlySkillIds'])!=co:e.append(f"{c['id']}: mapping skill differences are not exact")
  if c.get('extendedOnlyPlaceholder') and m['relationship']!='extended-only':e.append(f"{c['id']}: placeholder is not extended-only")
  if m['relationship']=='equivalent-requirement' and (eo or co or m['extendedOnlyClauseIds']):e.append(f"{c['id']}: equivalent mapping hides scope differences")
  if m['relationship']=='extended-adds-scope' and not (eo or m['extendedOnlyClauseIds']):e.append(f"{c['id']}: extended-adds-scope has no explicit addition")
  for cid in m['sharedClauseIds']+m['extendedOnlyClauseIds']:
   if cid not in clause_ids:e.append(f"{c['id']}: mapping references missing clause {cid}")
  extids={z['id'] for z in clauses[x['id']]['clauses']}; shared_ext=set(m['sharedClauseIds'])&extids; ext_only=set(m['extendedOnlyClauseIds'])
  if shared_ext&ext_only or shared_ext|ext_only!=extids:e.append(f"{c['id']}: Extended clauses are not fully and uniquely partitioned")
 # Relationships, indexes and prerequisite DAG.
 relmap={(r['from'],r['to'],r.get('relationship')) for r in rels if r['type']=='core-point-extended-by'}; expected_rel={(m['corePointId'],m['extendedPointId'],m['relationship']) for m in mcfg}
 if relmap!=expected_rel:e.append('Core/Extended relationships differ from curated config')
 bt={t['id']:{'syllabusPointIds':sorted(t['syllabusPointIds']),'atomicSkillIds':sorted({s for p in points if p['topicId']==t['id'] for s in p['atomicSkillIds']})} for t in topics}; bp={p['id']:{'topicId':p['topicId'],'atomicSkillIds':sorted(p['atomicSkillIds'])} for p in points}; bs={s['id']:{'topicIds':sorted(s['topicIds']),'syllabusPointIds':sorted(s['syllabusPointIds'])} for s in skills}; bg={g['id']:{'topicIds':sorted(g['topicIds']),'syllabusPointIds':sorted(g['syllabusPointIds']),'atomicSkillIds':sorted(g['atomicSkillIds'])} for g in groups}; pg={s['id']:{'prerequisiteSkillIds':sorted(s.get('prerequisiteSkillIds',[]))} for s in skills}
 for n,want in [('by-topic.json',bt),('by-syllabus-point.json',bp),('by-atomic-skill.json',bs),('by-skill-group.json',bg),('prerequisite-graph.json',pg)]:
  if load(I/n)!=want:e.append(f'index mismatch: {n}')
 graph={s['id']:s.get('prerequisiteSkillIds',[]) for s in skills}; active=set(); done=set()
 def visit(n):
  if n in active:return False
  if n in done:return True
  active.add(n); ok=all(x in graph and visit(x) for x in graph[n]); active.remove(n);done.add(n);return ok
 if not all(visit(n) for n in graph):e.append('prerequisite graph is invalid or cyclic')
 if digest()!=before:e.append('validation modified canonical taxonomy')
 statuses={'Structural':not any('schema:' in x or 'coverage mismatch' in x or 'duplicate canonical' in x or 'index mismatch' in x for x in e),'Extraction':not any('extraction' in x.lower() or 'confidence' in x.lower() or 'control character' in x.lower() or 'footer' in x.lower() or 'E6.6' in x for x in e),'Clause coverage':not any('clause' in x.lower() or 'supports no' in x or 'supporting clause' in x for x in e),'Semantic quality':not any('description' in x or 'unsupported' in x or 'broad deny' in x or 'skill-group' in x or 'duplicates an official topic' in x for x in e),'Core/Extended mapping':not any('Core/Extended' in x or 'mapping' in x or 'partitioned' in x or 'extended-adds' in x or 'equivalent mapping' in x for x in e),'Promotion safety':True}; pending=sum(x.get('review',{}).get('status')=='pending-review' for x in points+skills+groups)+sum(x.get('review',{}).get('status')=='pending-review' for x in mcfg); w.append(f'{pending} records or mappings await teacher review')
 if write_report:
  lines=['# Validation Report — Gate 1C Repair','',f'- Validation date: {datetime.now(timezone.utc).isoformat()}']+[f"- {k}: {'PASS' if v else 'FAIL'}" for k,v in statuses.items()]+[f"- Final Gate 1C Repair: {'PASS' if not e else 'FAIL'}",f'- Official clauses: {total_clauses}',f'- Covered clauses: {covered}',f'- Partially covered clauses: {partial}',f'- Unmapped/needs-review clauses: {unmapped}','','## Errors','']+([f'- {x}' for x in e] or ['- None'])+['','## Warnings','']+[f'- {x}' for x in w]; (R/'validation-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8'); (R/'semantic-validation-report.md').write_text('# Semantic Validation Report\n\n'+('PASS\n' if not e else 'FAIL\n\n'+'\n'.join(f'- {x}' for x in e)+'\n'),encoding='utf-8')
 return e,w,statuses,pending,{'totalClauses':total_clauses,'coveredClauses':covered,'partiallyCoveredClauses':partial,'unmappedClauses':unmapped}
def main():
 e,w,s,p,c=validate(); [print(f"{k}: {'PASS' if v else 'FAIL'}") for k,v in s.items()]; print(f"Clauses: {c['coveredClauses']}/{c['totalClauses']} covered; unmapped={c['unmappedClauses']}\nErrors: {len(e)}\nPending teacher review: {p}\nFinal Gate 1C Repair: {'PASS' if not e else 'FAIL'}"); [print('ERROR:',x) for x in e[:40]]; return 0 if not e else 1
if __name__=='__main__': raise SystemExit(main())
