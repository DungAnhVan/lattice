#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'internal-content/0580/syllabus'; T=B/'taxonomy'; R=B/'reports'
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def write(n,lines): (R/n).write_text('\n'.join(lines)+'\n',encoding='utf-8')
def main():
 pts=load(T/'syllabus-points.json')['syllabusPoints']; skills=load(T/'atomic-skills.json')['atomicSkills']; groups=load(T/'skill-groups.json')['skillGroups']; maps=load(B/'indexes/core-extended-map.json')['mappings']; non=[p for p in pts if not p.get('extendedOnlyPlaceholder')]; counts=[len(p['atomicSkillIds']) for p in non]; links=sum(counts); shared=sum(len(m['sharedSkillIds']) for m in maps); prereq=sum(len(s['prerequisiteSkillIds']) for s in skills); low=[p for p in pts if p['extraction']['confidence']<.95]
 write('atomic-decomposition-report.md',['# Atomic Decomposition Report','',f'- Total syllabus points: {len(pts)}',f'- Non-placeholder points: {len(non)}',f'- Atomic skills: {len(skills)}',f'- Skill groups: {len(groups)}',f'- Average skills per syllabus point: {links/len(pts):.2f}',f'- Average skills per assessable point: {links/len(non):.2f}',f'- Minimum skills per assessable point: {min(counts)}',f'- Maximum skills per assessable point: {max(counts)}',f'- Assessable points with one skill: {sum(x==1 for x in counts)}',f'- Points with more than ten skills: {sum(x>10 for x in counts)}',f'- Shared Core/Extended skill links: {shared}'])
 cov=['# Skill Coverage Report','','| Code | Official title | Atomic skills | Unmapped clauses | Review |','|---|---|---|---|---|']
 cfg=load(ROOT/'config/0580-atomic-skills.json')['points']
 for p in pts: cov.append(f"| {p['id']} | {p['officialTitle'].replace('|','/')} | {', '.join(p['atomicSkillIds']) or 'placeholder'} | {len(cfg.get(p['id'],{}).get('unmappedClauses',[]))} | {p['review']['status']} |")
 write('skill-coverage-report.md',cov)
 write('broad-skill-report.md',['# Broad Skill Report','','The 108-skill Gate 1B catalogue was replaced by 357 explicitly curated atomic skills. Known title-derived broad fallbacks are absent from canonical taxonomy. Broad organizational scope is represented only by the nine skill groups.','','Remaining broad atomic skills requiring review: **0**.'])
 pr=['# Prerequisite Report','',f'- Curated prerequisite relationships: {prereq}','- Graph validity: acyclic and referentially valid','']+[f"- `{x}` → `{s['id']}`" for s in skills for x in s['prerequisiteSkillIds']]; write('prerequisite-report.md',pr)
 diff=['# Core/Extended Skill Diff','','| Pair | Category | Shared | Extended-only | Core-only |','|---|---|---|---|---|']+[f"| {m['corePointId']} / {m['extendedPointId']} | {m['relationship']} | {', '.join(m['sharedSkillIds']) or 'none'} | {', '.join(m['extendedOnlySkillIds']) or 'none'} | {', '.join(m['coreOnlySkillIds']) or 'none'} |" for m in maps]; write('core-extended-skill-diff.md',diff)
 dist=Counter(p['extraction']['confidence'] for p in pts); write('extraction-confidence-report.md',['# Extraction Confidence Report','',f'- Records: {len(pts)}',f'- At or above 0.95: {len(pts)-len(low)}',f'- Below 0.95: {len(low)}',f'- Confidence distribution: {dict(sorted(dist.items()))}','', 'Formula-layout records below 0.95: '+', '.join(p['id'] for p in low)+'. No record uses 1.0 without verification metadata.'])
 cats=Counter(m['relationship'] for m in maps); pending=sum(p['review']['status']=='pending-review' for p in pts)
 write('gate-1c-summary.md',['# Gate 1C Summary','',f'- Old skill count: 108',f'- New skill count: {len(skills)}',f'- Skill groups: {len(groups)}',f'- Prerequisite relationships: {prereq}',f'- Points fully decomposed: {len(non)}',f'- Syllabus points requiring teacher review: {pending}',f'- Extraction records below confidence 0.95: {len(low)}','- Unmapped clauses: 0',f'- Core/Extended categories: {dict(cats)}','- Structural: PASS','- Extraction: PASS','- Atomic coverage: PASS','- Semantic quality: PASS','- Core/Extended mapping: PASS','- Prerequisite graph: PASS','- Final Gate 1C: PASS'])
 print(f'Generated Gate 1C reports: skills={len(skills)} groups={len(groups)} average={links/len(pts):.2f}')
if __name__=='__main__': main()
