#!/usr/bin/env python3
"""Read-only structural and semantic validation for Cambridge 0580."""
from __future__ import annotations
import json, re
from datetime import datetime, timezone
from pathlib import Path
from jsonschema import Draft202012Validator
from taxonomy_quality import official_content_issues, skill_issues

ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'internal-content/0580/syllabus'; TAX=BASE/'taxonomy'; IDX=BASE/'indexes'; SCHEMA=BASE/'schemas'; REPORT=BASE/'reports'
COUNTS={1:18,2:13,3:7,4:8,5:5,6:6,7:4,8:4,9:7}; EXPECTED={f'{tier}{t}.{n}' for tier in 'CE' for t,count in COUNTS.items() for n in range(1,count+1)}
ALLOWED_MAP={'equivalent-requirement','extended-includes-core','extended-adds-scope','extended-only','core-only','related-but-not-equivalent','needs-review'}
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def compute(topics,points,skills):
 return ({t['id']:{'syllabusPointIds':sorted(t['syllabusPointIds']),'atomicSkillIds':sorted({s for p in points if p['topicId']==t['id'] for s in p['atomicSkillIds']})} for t in topics},{p['id']:{'topicId':p['topicId'],'atomicSkillIds':sorted(p['atomicSkillIds'])} for p in points},{s['id']:{'topicIds':sorted(s['topicIds']),'syllabusPointIds':sorted(s['syllabusPointIds'])} for s in skills})
def validate(write_report=True):
 errors=[]; warnings=[]; passed=[]
 docs={n:load(TAX/n) for n in ['syllabus.json','topics.json','syllabus-points.json','atomic-skills.json','relationships.json']}
 for name,schema in [('syllabus.json','syllabus.schema.json'),('topics.json','topic.schema.json'),('syllabus-points.json','syllabus-point.schema.json'),('atomic-skills.json','atomic-skill.schema.json'),('relationships.json','relationships.schema.json')]:
  es=list(Draft202012Validator(load(SCHEMA/schema)).iter_errors(docs[name])); errors += [f'{name} schema: {e.message}' for e in es[:30]]
 topics=docs['topics.json']['topics']; points=docs['syllabus-points.json']['syllabusPoints']; skills=docs['atomic-skills.json']['atomicSkills']; rels=docs['relationships.json']['relationships']
 tids={x['id'] for x in topics}; pids={x['id'] for x in points}; sids={x['id'] for x in skills}
 if len(tids)!=len(topics) or len(pids)!=len(points) or len(sids)!=len(skills): errors.append('duplicate canonical IDs')
 if pids!=EXPECTED: errors.append(f'official code coverage mismatch: missing={sorted(EXPECTED-pids)} extra={sorted(pids-EXPECTED)}')
 for p in points:
  if p['topicId'] not in tids: errors.append(f"{p['id']}: missing topic")
  if not p.get('sourceReferences'): errors.append(f"{p['id']}: no source reference")
  if p.get('review',{}).get('status') not in {'pending-review','approved','rejected','needs-revision'}: errors.append(f"{p['id']}: invalid review status")
  if not p.get('extendedOnlyPlaceholder'):
   errors += [f"{p['id']}: {x}" for x in official_content_issues(p.get('officialStatement',''),p.get('examplesFromSyllabus'))]
  if p.get('review',{}).get('status')=='approved' and (p.get('extraction',{}).get('status')!='clean' or p.get('extraction',{}).get('issues')): errors.append(f"{p['id']}: approved with extraction issues")
  for sid in p.get('atomicSkillIds',[]):
   if sid not in sids: errors.append(f"{p['id']}: missing skill {sid}")
 for s in skills:
  errors += [f"{s['id']}: {x}" for x in skill_issues(s)]
  for pid in s.get('syllabusPointIds',[]):
   if pid not in pids: errors.append(f"{s['id']}: missing point {pid}")
 for rel in rels:
  if rel['type']=='topic-contains-syllabus-point' and (rel['from'] not in tids or rel['to'] not in pids): errors.append(f'invalid relationship {rel}')
  if rel['type']=='syllabus-point-requires-atomic-skill' and (rel['from'] not in pids or rel['to'] not in sids): errors.append(f'invalid relationship {rel}')
  if rel['type']=='core-point-extended-by' and (rel['from'] not in pids or rel['to'] not in pids): errors.append(f'invalid relationship {rel}')
 expected=compute(topics,points,skills)
 for name,want in zip(['by-topic.json','by-syllabus-point.json','by-atomic-skill.json'],expected):
  if load(IDX/name)!=want: errors.append(f'index mismatch: {name}')
 mapping=load(IDX/'core-extended-map.json').get('mappings',[]); seen=set()
 for m in mapping:
  pair=(m.get('corePointId'),m.get('extendedPointId'))
  if pair in seen: errors.append(f'duplicate Core/Extended mapping {pair}')
  seen.add(pair)
  if pair[0] not in pids or pair[1] not in pids or m.get('relationship') not in ALLOWED_MAP: errors.append(f'invalid Core/Extended mapping {pair}')
  if next(x for x in points if x['id']==pair[0]).get('extendedOnlyPlaceholder') and m.get('relationship')=='equivalent-requirement': errors.append(f'{pair}: placeholder classified equivalent')
 if len(mapping)!=72: errors.append(f'expected 72 Core/Extended mappings, found {len(mapping)}')
 pending=sum(x.get('review',{}).get('status')=='pending-review' for x in points+skills)+sum(x.get('review',{}).get('status')=='pending-review' for x in mapping)
 structural=not any('schema:' in e or 'coverage' in e or 'missing' in e or 'index mismatch' in e for e in errors); semantic=not errors
 if pending: warnings.append(f'{pending} records or mappings await teacher review')
 if write_report:
  lines=['# Validation Report — Gate 1B','',f"- Validation date: {datetime.now(timezone.utc).isoformat()}",f"- Structural status: {'PASS' if structural else 'FAIL'}",f"- Semantic status: {'PASS' if semantic else 'FAIL'}",f"- Gate status: {'PASS' if semantic else 'FAIL'}",'', '## Errors','']+([f'- {x}' for x in errors] or ['- None'])+['','## Warnings','']+([f'- {x}' for x in warnings] or ['- None'])
  (REPORT/'validation-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8'); (REPORT/'semantic-validation-report.md').write_text('\n'.join(['# Semantic Validation Report','',f"Status: {'PASS' if semantic else 'FAIL'}",'']+([f'- {x}' for x in errors] or ['- No semantic defects detected.']))+'\n',encoding='utf-8')
 return errors,warnings,structural,semantic,pending
def main():
 e,w,st,se,p=validate(); print(f"Structural: {'PASS' if st else 'FAIL'}\nSemantic: {'PASS' if se else 'FAIL'}\nErrors: {len(e)}\nWarnings: {len(w)}\nPending teacher review: {p}"); [print('ERROR:',x) for x in e[:20]]; return 0 if se else 1
if __name__=='__main__': raise SystemExit(main())
