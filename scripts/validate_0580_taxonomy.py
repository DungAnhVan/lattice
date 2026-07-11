#!/usr/bin/env python3
"""Read-only Gate 1C structural, extraction, coverage and semantic validation."""
from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
from jsonschema import Draft202012Validator
from taxonomy_quality import official_content_issues,skill_issues
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'internal-content/0580/syllabus'; TAX=BASE/'taxonomy'; IDX=BASE/'indexes'; SCHEMA=BASE/'schemas'; REPORT=BASE/'reports'
COUNTS={1:18,2:13,3:7,4:8,5:5,6:6,7:4,8:4,9:7}; EXPECTED={f'{z}{t}.{n}' for z in 'CE' for t,c in COUNTS.items() for n in range(1,c+1)}; MAP_TYPES={'equivalent-requirement','extended-includes-core','extended-adds-scope','extended-only','core-only','related-but-not-equivalent','needs-review'}
BROAD={'apply-algebraic-manipulation','calculate-powers-and-roots','apply-area-and-perimeter','apply-averages-and-measures-of-spread','apply-functions-concepts','apply-percentages-concepts','solve-equations','apply-statistics','use-geometry'}
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def canonical_digest():
 import hashlib
 h=hashlib.sha256()
 for p in sorted(TAX.glob('*.json')): h.update(p.read_bytes())
 return h.hexdigest()
def validate(write_report=True):
 e=[]; w=[]; before=canonical_digest(); names={'syllabus.json':'syllabus.schema.json','topics.json':'topic.schema.json','syllabus-points.json':'syllabus-point.schema.json','atomic-skills.json':'atomic-skill.schema.json','skill-groups.json':'skill-group.schema.json','relationships.json':'relationships.schema.json'}; docs={n:load(TAX/n) for n in names}
 for n,schema in names.items(): e += [f'{n} schema: {x.message}' for x in list(Draft202012Validator(load(SCHEMA/schema)).iter_errors(docs[n]))[:40]]
 topics=docs['topics.json']['topics']; points=docs['syllabus-points.json']['syllabusPoints']; skills=docs['atomic-skills.json']['atomicSkills']; groups=docs['skill-groups.json']['skillGroups']; rels=docs['relationships.json']['relationships']; tids={x['id'] for x in topics}; pids={x['id'] for x in points}; sids={x['id'] for x in skills}; gids={x['id'] for x in groups}
 pcfg=load(ROOT/'config/0580-atomic-skills.json')['points']; defs=load(ROOT/'config/0580-skill-definitions.json')['skills']; nonplace={p['id'] for p in points if not p.get('extendedOnlyPlaceholder')}
 if pids!=EXPECTED: e.append('official code coverage mismatch')
 if len(tids)!=len(topics) or len(pids)!=len(points) or len(sids)!=len(skills) or len(gids)!=len(groups): e.append('duplicate canonical IDs')
 if set(pcfg)!=nonplace: e.append('curated point config does not exactly cover all non-placeholder points')
 configured={s for v in pcfg.values() for s in v['atomicSkills']}
 if configured!=set(defs) or configured!=sids: e.append('configured skills, definitions, and canonical skills differ')
 if any(v.get('unmappedClauses') for v in pcfg.values()): e.append('curated config contains unmapped assessable clauses')
 for p in points:
  if p['topicId'] not in tids or not p.get('sourceReferences'): e.append(f"{p['id']}: missing topic or source reference")
  if p.get('extendedOnlyPlaceholder'):
   if p.get('atomicSkillIds'): e.append(f"{p['id']}: placeholder has assessable skills")
  else:
   e += [f"{p['id']}: {x}" for x in official_content_issues(p.get('officialStatement',''),p.get('examplesFromSyllabus'))]
   if not p.get('atomicSkillIds'): e.append(f"{p['id']}: no atomic-skill coverage")
  ex=p.get('extraction',{})
  if ex.get('confidence')==1.0 and (not ex.get('verifiedBy') or not ex.get('verifiedAt')): e.append(f"{p['id']}: confidence 1.0 lacks verification metadata")
  if ex.get('status')=='clean' and ex.get('issues'): e.append(f"{p['id']}: extraction marked clean with issues")
  for sid in p.get('atomicSkillIds',[]):
   if sid not in sids: e.append(f"{p['id']}: missing skill {sid}")
 for s in skills:
  e += [f"{s['id']}: {x}" for x in skill_issues(s)]
  d=s.get('description','').lower()
  if s['id'] in BROAD: e.append(f"{s['id']}: broad deny-listed atomic skill")
  if 'in mathematical problems' in d or 'perform the specified operation' in d or len(d)<45: e.append(f"{s['id']}: generic or insufficient description")
  if not s.get('skillGroupIds'): e.append(f"{s['id']}: no skill group")
  for x in s.get('skillGroupIds',[]):
   if x not in gids: e.append(f"{s['id']}: missing group {x}")
  for x in s.get('syllabusPointIds',[]):
   if x not in pids: e.append(f"{s['id']}: missing point {x}")
  for x in s.get('prerequisiteSkillIds',[]):
   if x not in sids: e.append(f"{s['id']}: missing prerequisite {x}")
 for g in groups:
  for x in g['atomicSkillIds']:
   if x not in sids: e.append(f"{g['id']}: missing grouped skill {x}")
 for r in rels:
  if r['type']=='topic-contains-syllabus-point' and (r['from'] not in tids or r['to'] not in pids): e.append('invalid topic relationship')
  if r['type']=='syllabus-point-requires-atomic-skill' and (r['from'] not in pids or r['to'] not in sids): e.append('invalid point-skill relationship')
  if r['type']=='atomic-skill-prerequisite-of' and (r['from'] not in sids or r['to'] not in sids): e.append('invalid prerequisite relationship')
 # Disposable indexes must exactly match canonical records.
 bt={t['id']:{'syllabusPointIds':sorted(t['syllabusPointIds']),'atomicSkillIds':sorted({s for p in points if p['topicId']==t['id'] for s in p['atomicSkillIds']})} for t in topics}; bp={p['id']:{'topicId':p['topicId'],'atomicSkillIds':sorted(p['atomicSkillIds'])} for p in points}; bs={s['id']:{'topicIds':sorted(s['topicIds']),'syllabusPointIds':sorted(s['syllabusPointIds'])} for s in skills}; bg={g['id']:{'topicIds':sorted(g['topicIds']),'syllabusPointIds':sorted(g['syllabusPointIds']),'atomicSkillIds':sorted(g['atomicSkillIds'])} for g in groups}; pg={s['id']:{'prerequisiteSkillIds':sorted(s.get('prerequisiteSkillIds',[]))} for s in skills}
 for n,want in [('by-topic.json',bt),('by-syllabus-point.json',bp),('by-atomic-skill.json',bs),('by-skill-group.json',bg),('prerequisite-graph.json',pg)]:
  if load(IDX/n)!=want: e.append(f'index mismatch: {n}')
 maps=load(IDX/'core-extended-map.json').get('mappings',[]); byid={p['id']:p for p in points}
 if len(maps)!=72: e.append('Core/Extended mapping does not cover 72 pairs')
 for m in maps:
  c=byid.get(m.get('corePointId')); x=byid.get(m.get('extendedPointId'))
  if not c or not x or m.get('relationship') not in MAP_TYPES: e.append('invalid Core/Extended mapping'); continue
  cs=set(c['atomicSkillIds']); xs=set(x['atomicSkillIds'])
  if c.get('extendedOnlyPlaceholder') and m['relationship']=='equivalent-requirement': e.append(f"{c['id']}: placeholder classified equivalent")
  if not set(m.get('sharedSkillIds',[]))<=cs&xs or not set(m.get('extendedOnlySkillIds',[]))<=xs-cs: e.append(f"{c['id']}: invalid skill diff mapping")
 graph={s['id']:s.get('prerequisiteSkillIds',[]) for s in skills}; visiting=set(); done=set()
 def visit(n):
  if n in visiting:return False
  if n in done:return True
  visiting.add(n); ok=all(visit(x) for x in graph[n]); visiting.remove(n); done.add(n); return ok
 if not all(visit(n) for n in graph): e.append('prerequisite graph contains a cycle')
 if len({p['extraction']['confidence'] for p in points})==1:e.append('all extraction confidence values are identical')
 if canonical_digest()!=before:e.append('validation modified canonical taxonomy')
 statuses={'Structural':not any('schema:' in x or 'coverage mismatch' in x or 'duplicate' in x or 'index mismatch' in x for x in e),'Extraction':not any('extraction' in x or 'confidence' in x for x in e),'Atomic coverage':not any('coverage' in x or 'curated' in x or 'configured' in x or 'unmapped' in x or 'placeholder has' in x for x in e),'Semantic quality':not e,'Core/Extended mapping':not any('mapping' in x or 'skill diff' in x for x in e),'Prerequisite graph':not any('prerequisite' in x for x in e)}; pending=sum(x.get('review',{}).get('status')=='pending-review' for x in points+skills+groups)+sum(x.get('review',{}).get('status')=='pending-review' for x in maps); w.append(f'{pending} records or mappings await teacher review')
 if write_report:
  lines=['# Validation Report — Gate 1C','',f'- Validation date: {datetime.now(timezone.utc).isoformat()}']+[f"- {k}: {'PASS' if v else 'FAIL'}" for k,v in statuses.items()]+[f"- Final Gate 1C: {'PASS' if not e else 'FAIL'}",'','## Errors','']+([f'- {x}' for x in e] or ['- None'])+['','## Warnings','']+[f'- {x}' for x in w]; (REPORT/'validation-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8'); (REPORT/'semantic-validation-report.md').write_text('# Semantic Validation Report\n\n'+('PASS\n' if not e else 'FAIL\n\n'+'\n'.join(f'- {x}' for x in e)+'\n'),encoding='utf-8')
 return e,w,statuses,pending
def main():
 e,w,s,p=validate(); [print(f"{k}: {'PASS' if v else 'FAIL'}") for k,v in s.items()]; print(f"Errors: {len(e)}\nPending teacher review: {p}\nFinal Gate 1C: {'PASS' if not e else 'FAIL'}"); [print('ERROR:',x) for x in e[:30]]; return 0 if not e else 1
if __name__=='__main__': raise SystemExit(main())
