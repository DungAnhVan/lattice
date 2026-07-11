#!/usr/bin/env python3
"""Create the machine-readable Gate 1C decomposition audit without changing canonical data."""
from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'internal-content/0580/syllabus'; TAX=BASE/'taxonomy'; OUT=BASE/'reports/decomposition-plan.json'
BROAD={'apply-algebraic-manipulation','calculate-powers-and-roots','apply-area-and-perimeter','apply-averages-and-measures-of-spread','apply-functions-concepts','apply-percentages-concepts','solve-equations','apply-statistics','use-geometry'}
def main():
 points=json.loads((TAX/'syllabus-points.json').read_text(encoding='utf-8'))['syllabusPoints']; plan=[]
 for p in points:
  statement=p['officialStatement']; clauses=[x.strip(' •\t') for x in re.split(r'(?m)(?:^|\n)\s*(?:\d+\s+|•\s*)',statement) if x.strip()]
  plan.append({'pointId':p['id'],'title':p['officialTitle'],'placeholder':p.get('extendedOnlyPlaceholder',False),'currentSkillIds':p['atomicSkillIds'],'currentClauseCount':len(clauses),'clauses':clauses,'broadSkillIds':[x for x in p['atomicSkillIds'] if x in BROAD or len(p['atomicSkillIds'])==1 and len(clauses)>1],'requiresDecomposition':not p.get('extendedOnlyPlaceholder') and (len(p['atomicSkillIds'])==1 or bool(set(p['atomicSkillIds'])&BROAD))})
 OUT.write_text(json.dumps({'schemaVersion':'1.0','generatedFrom':'taxonomy/syllabus-points.json','points':plan},ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(f'Audited {len(plan)} points; decomposition required for {sum(x["requiresDecomposition"] for x in plan)}')
if __name__=='__main__': main()
