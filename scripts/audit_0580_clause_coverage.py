#!/usr/bin/env python3
"""Gate 1C Repair pre-change audit: compare official clauses with current skills."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'internal-content/0580/syllabus'; T=B/'taxonomy'; OUT=B/'reports/pre-repair-clause-audit.json'
ACTIONS=r'identify|recognise|represent|interpret|construct|solve|list|calculate|use|understand|know|read|write|compare|order|classify|convert|estimate|round|simplify|expand|factorise|draw|plot|find|determine|prove|evaluate|differentiate|sketch|describe|give|apply|continue|change|complete|express|make|enter|measure'
STOP={'the','and','with','from','into','including','following','given','using','use','understand','calculate','find','apply','interpret','represent','construct','solve','know'}
def clauses(text):
 text=text.replace('\x07','').strip(); chunks=re.split(r'(?m)(?=^\s*\d+\s+)',text); chunks=[x.strip() for x in chunks if x.strip()]
 if len(chunks)==1:
  bullets=re.split(r'(?m)(?=^\s*•\s*)',text); actionable=[x.strip() for x in bullets if x.strip() and re.search(rf'\b({ACTIONS})\b',x,re.I)]
  if len(actionable)>1: chunks=actionable
 return chunks or [text]
def tokens(s): return {x for x in re.findall(r'[a-z]+',s.lower()) if len(x)>2 and x not in STOP}
def main():
 pts=json.loads((T/'syllabus-points.json').read_text(encoding='utf-8'))['syllabusPoints']; rows=[]
 for p in pts:
  if p.get('extendedOnlyPlaceholder'): continue
  cs=clauses(p['officialStatement']); mappings=[]; supported=set()
  for i,c in enumerate(cs,1):
   ct=tokens(c); ranked=sorted(((len(ct&tokens(s.replace('-',' '))),s) for s in p['atomicSkillIds']),reverse=True); best=[s for score,s in ranked if score==ranked[0][0] and score>0] if ranked else []
   supported.update(best); mappings.append({'clauseId':f"{p['id']}-c{i}",'officialText':c,'candidateSkillIds':best,'machineStatus':'candidate-covered' if best else 'unmapped','evidenceTokenOverlap':ranked[0][0] if ranked else 0})
  rows.append({'pointId':p['id'],'officialTitle':p['officialTitle'],'clauses':mappings,'currentSkillIds':p['atomicSkillIds'],'skillsWithNoClauseEvidence':sorted(set(p['atomicSkillIds'])-supported)})
 OUT.write_text(json.dumps({'schemaVersion':'1.0','status':'pre-repair-audit-only','points':rows},indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); print(f"Audited {len(rows)} assessable points, {sum(len(x['clauses']) for x in rows)} candidate clauses, {sum(c['machineStatus']=='unmapped' for x in rows for c in x['clauses'])} candidate gaps")
if __name__=='__main__': main()
