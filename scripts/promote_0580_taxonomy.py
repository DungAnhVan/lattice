#!/usr/bin/env python3
"""Schema-safe, review-preserving, transactional draft promotion."""
from __future__ import annotations
import argparse,copy,json,os,shutil,subprocess,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'internal-content/0580/syllabus'; T=B/'taxonomy'; D=B/'drafts'; I=B/'indexes'; S=B/'schemas'; R=B/'reports/promotion-field-diff.md'
POINT_REQUIRED={'id','officialCode','tier','topicId','officialTitle','officialStatement','notes','examplesFromSyllabus','extendedOnlyPlaceholder','sourceReferences','atomicSkillIds','syllabusCode','origin','review','extraction','prerequisiteSyllabusPointIds','relatedSyllabusPointIds'}
SKILL_REQUIRED={'id','label','description','topicIds','syllabusPointIds','conceptIds','skillGroupIds','action','difficulty','prerequisiteSkillIds','relatedSkillIds','origin','sourceBasis','review'}
POINT_MUTABLE={'officialTitle','officialStatement','notes','examplesFromSyllabus','extendedOnlyPlaceholder','atomicSkillIds','extraction'}; SKILL_MUTABLE={'label','description','topicIds','syllabusPointIds','conceptIds','skillGroupIds','action','difficulty','prerequisiteSkillIds','relatedSkillIds','sourceBasis'}
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def duplicates(rows):
 seen=set(); return sorted({x['id'] for x in rows if x['id'] in seen or seen.add(x['id'])})
def merge_collection(canonical,draft,key,required,mutable):
 rows=draft[key]
 if duplicates(rows): raise ValueError(f'duplicate draft IDs: {duplicates(rows)}')
 ci={x['id']:x for x in canonical[key]}; di={x['id']:x for x in rows}; missing=[(x['id'],sorted(required-set(x))) for x in rows if required-set(x)]
 if missing: raise ValueError(f'incomplete draft records: {missing[:5]}')
 out=[]; changes=[]
 for old in canonical[key]:
  new=di.get(old['id'])
  if not new: out.append(copy.deepcopy(old)); continue
  for field in (required-mutable-{'review'}) & {'id','officialCode','tier','topicId','syllabusCode','origin'}:
   if field in old and new.get(field)!=old.get(field): raise ValueError(f"{old['id']}: protected field changed: {field}")
  merged=copy.deepcopy(old)
  for field in mutable:
   if new.get(field)!=old.get(field): changes.append({'id':old['id'],'field':field,'before':old.get(field),'after':new.get(field)}); merged[field]=copy.deepcopy(new[field])
  merged['review']=copy.deepcopy(old['review']); out.append(merged)
 for ident,new in di.items():
  if ident not in ci: raise ValueError(f'new canonical record requires a separate explicit workflow: {ident}')
 return {**canonical,key:out},changes
def validate_schema(doc,schema):
 errors=list(Draft202012Validator(load(S/schema)).iter_errors(doc))
 if errors: raise ValueError(f'candidate schema failure: {errors[0].message} at {list(errors[0].path)}')
def relationships(points,skills):
 rel=[]
 for p in points:
  rel.append({'type':'topic-contains-syllabus-point','from':p['topicId'],'to':p['id'],'origin':'official-syllabus'})
  rel += [{'type':'syllabus-point-requires-atomic-skill','from':p['id'],'to':x,'origin':'lattice-derived'} for x in p['atomicSkillIds']]
 for s in skills: rel += [{'type':'atomic-skill-prerequisite-of','from':x,'to':s['id'],'origin':'lattice-derived'} for x in s.get('prerequisiteSkillIds',[])]
 for m in load(ROOT/'config/0580-core-extended-map.json')['mappings']: rel.append({'type':'core-point-extended-by','from':m['corePointId'],'to':m['extendedPointId'],'origin':'lattice-derived','relationship':m['relationship']})
 return {'schemaVersion':'1.0','relationships':rel}
def plan():
 cp=load(T/'syllabus-points.json'); cs=load(T/'atomic-skills.json'); dp=load(D/'syllabus-points.draft.json'); ds=load(D/'atomic-skills.draft.json'); mp,pc=merge_collection(cp,dp,'syllabusPoints',POINT_REQUIRED,POINT_MUTABLE); ms,sc=merge_collection(cs,ds,'atomicSkills',SKILL_REQUIRED,SKILL_MUTABLE); validate_schema(mp,'syllabus-point.schema.json'); validate_schema(ms,'atomic-skill.schema.json'); rel=relationships(mp['syllabusPoints'],ms['atomicSkills']); validate_schema(rel,'relationships.schema.json'); return mp,ms,rel,pc+sc
def report(changes):
 lines=['# Promotion Field Diff','',f'- Generated: {datetime.now(timezone.utc).isoformat()}',f'- Changed fields: {len(changes)}','','| ID | Field | Before | After |','|---|---|---|---|']
 for x in changes: lines.append(f"| {x['id']} | {x['field']} | `{json.dumps(x['before'],ensure_ascii=False)[:160]}` | `{json.dumps(x['after'],ensure_ascii=False)[:160]}` |")
 R.write_text('\n'.join(lines)+'\n',encoding='utf-8')
def main(argv=None):
 ap=argparse.ArgumentParser(); ap.add_argument('--confirm',action='store_true'); ap.add_argument('--simulate-post-validation-failure',action='store_true',help=argparse.SUPPRESS); a=ap.parse_args(argv)
 try: mp,ms,rel,changes=plan(); report(changes)
 except Exception as exc: print(f'Promotion preflight failed: {exc}'); return 3
 if not a.confirm: print('Refusing to write canonical taxonomy without --confirm; field-level diff created'); return 2
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); backup=B/'backups'/stamp; backup.mkdir(parents=True); files=list(T.glob('*.json'))+list(I.glob('*.json'))
 for p in files: shutil.copy2(p,backup/p.name)
 try:
  for path,doc in [(T/'syllabus-points.json',mp),(T/'atomic-skills.json',ms),(T/'relationships.json',rel)]:
   fd,tmp=tempfile.mkstemp(dir=path.parent,suffix='.tmp'); os.close(fd); Path(tmp).write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); os.replace(tmp,path)
  subprocess.run([sys.executable,str(ROOT/'scripts/generate_0580_indexes.py')],cwd=ROOT,check=True,capture_output=True)
  if a.simulate_post_validation_failure: raise RuntimeError('simulated post-merge validation failure')
  subprocess.run([sys.executable,str(ROOT/'scripts/validate_0580_taxonomy.py')],cwd=ROOT,check=True,capture_output=True)
 except Exception as exc:
  for p in files:
   saved=backup/p.name
   if saved.exists(): shutil.copy2(saved,p)
  print(f'Promotion failed and was rolled back: {exc}'); return 4
 print(f'Promotion complete; backup={backup}; changed fields={len(changes)}'); return 0
if __name__=='__main__': raise SystemExit(main())
