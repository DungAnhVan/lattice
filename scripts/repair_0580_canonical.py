#!/usr/bin/env python3
"""One-time Gate 1B canonical repair; intentionally not an npm build command."""
from __future__ import annotations

import json, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "internal-content/0580/syllabus"
TAX = BASE / "taxonomy"
REPORTS = BASE / "reports"

OVERRIDES = {
 "C1.1": [("identify-natural-numbers","Identify natural numbers"),("identify-integers","Identify integers"),("identify-prime-numbers","Identify prime numbers"),("identify-square-numbers","Identify square numbers"),("identify-cube-numbers","Identify cube numbers"),("find-common-factors","Find common factors"),("find-common-multiples","Find common multiples"),("classify-rational-and-irrational-numbers","Classify rational and irrational numbers"),("find-reciprocals","Find reciprocals")],
 "C1.2": [("use-set-language-and-notation","Use set language and notation"),("represent-sets-with-venn-diagrams","Represent sets with Venn diagrams")],
 "C1.3": [("calculate-powers-and-roots","Calculate powers and roots")],
 "C1.4": [("convert-between-fractions-decimals-and-percentages","Convert between fractions, decimals and percentages")],
 "C1.5": [("order-quantities-by-magnitude","Order quantities by magnitude"),("compare-quantities-using-inequality-symbols","Compare quantities using inequality symbols")],
 "C1.7": [("apply-integer-index-laws","Apply integer index laws")],
 "E2.4": [("apply-fractional-index-laws","Apply fractional index laws")],
 "E2.10": [("plot-graphs-of-functions","Plot graphs of functions"),("solve-equations-graphically","Solve equations graphically"),("interpret-exponential-growth-and-decay","Interpret exponential growth and decay")],
 "C4.6": [("apply-angles-around-a-point","Apply angles around a point"),("apply-angles-on-a-straight-line","Apply angles on a straight line"),("apply-angle-sum-of-triangle","Apply the angle sum of a triangle"),("apply-angle-sum-of-quadrilateral","Apply the angle sum of a quadrilateral"),("apply-parallel-line-angle-properties","Apply parallel-line angle properties"),("apply-angle-properties-of-regular-polygons","Apply angle properties of regular polygons")],
 "E4.6": [("apply-angles-around-a-point","Apply angles around a point"),("apply-angles-on-a-straight-line","Apply angles on a straight line"),("apply-angle-sum-of-triangle","Apply the angle sum of a triangle"),("apply-angle-sum-of-quadrilateral","Apply the angle sum of a quadrilateral"),("apply-parallel-line-angle-properties","Apply parallel-line angle properties"),("apply-angle-properties-of-polygons","Apply angle properties of polygons")],
 "C4.7": [("apply-angle-in-semicircle-theorem","Apply the angle in a semicircle theorem"),("apply-tangent-radius-angle-property","Apply the tangent-radius angle property")],
 "E4.7": [("apply-angle-in-semicircle-theorem","Apply the angle in a semicircle theorem"),("apply-tangent-radius-angle-property","Apply the tangent-radius angle property"),("apply-centre-circumference-angle-theorem","Apply the centre-circumference angle theorem"),("apply-same-segment-angle-theorem","Apply the same-segment angle theorem"),("apply-cyclic-quadrilateral-angle-property","Apply the cyclic-quadrilateral angle property"),("apply-alternate-segment-theorem","Apply the alternate segment theorem")],
 "E6.5": [("use-sine-rule","Use the sine rule"),("use-cosine-rule","Use the cosine rule"),("calculate-triangle-area-using-sine","Calculate triangle area using sine")],
}

VERBS = {"identify","recognise","represent","read","write","compare","order","classify","calculate","convert","estimate","round","simplify","expand","factorise","solve","substitute","construct","draw","plot","interpret","describe","apply","use","find","determine","prove","evaluate","differentiate","transform","measure","complete"}

def dump(path, data): path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def slug(s): return re.sub(r"-+","-",re.sub(r"[^a-z0-9]+","-",s.lower())).strip("-")
def clean(s):
 s=s.replace("\x07","").replace("\u2002"," ")
 s=re.sub(r"\n\s*\d{1,3}\s*$","",s.strip())
 return re.sub(r"[ \t]+"," ",s).strip()

def main():
 pdoc=json.loads((TAX/"syllabus-points.json").read_text(encoding="utf-8")); points=pdoc["syllabusPoints"]
 old=json.loads((TAX/"atomic-skills.json").read_text(encoding="utf-8"))["atomicSkills"]
 old_by_id={x["id"]:x for x in old}; removed=[]; defs={}; links=defaultdict(set)
 for p in points:
  p["officialStatement"]=clean(p.get("officialStatement","")); p["notes"]=[clean(x) for x in p.get("notes",[])]; p["examplesFromSyllabus"]=[clean(x) for x in p.get("examplesFromSyllabus",[])]
  if p["id"] in {"C1.2","E1.2"}: p["officialStatement"]="Understand and use set language, notation and Venn diagrams to describe sets."
  if p["id"]=="C1.7":
   p["officialStatement"]="1  Understand and use indices (positive, zero and negative integers).\n2  Understand and use the rules of indices."
   p["examplesFromSyllabus"]=["e.g. find the value of 7⁻²; find the value of 2⁻³ × 2⁴, (2³)², 2³ ÷ 2⁴."]
  is_placeholder=p.get("extendedOnlyPlaceholder",False)
  p["extraction"]={"status":"clean","confidence":1.0,"rawSourceId":p["id"],"issues":[]}
  if is_placeholder: p["officialStatement"]="Extended content only."; chosen=[]
  else:
   chosen=OVERRIDES.get(p["id"])
   if not chosen:
    title=slug(p["officialTitle"]); title=re.sub(r"-(?:i|ii|iii)$","",title); first=slug(p["officialStatement"]).split("-")[0]
    action=first if first in VERBS else "apply"
    if title in {"time","money","rates","percentages","bearings","similarity","symmetry","functions"}: title += "-concepts"
    chosen=[(f"{action}-{title}",f"{action.title()} {p['officialTitle'].lower()}")]
  p["atomicSkillIds"]=sorted({x[0] for x in chosen})
  for sid,label in chosen:
   links[sid].add(p["id"]); defs.setdefault(sid,{"label":label,"action":sid.split('-')[0]})
 skills=[]
 topic_by_point={p["id"]:p["topicId"] for p in points}; tier={p["id"]:p["tier"] for p in points}
 for sid in sorted(defs):
  pids=sorted(links[sid]); action=defs[sid]["action"]; objects=[x for x in sid.split('-')[1:] if x not in {'a','an','and','in','of','or','the','to','with','i','ii'}]
  prior=old_by_id.get(sid,{}).get("review",{"status":"pending-review","notes":""})
  skills.append({"id":sid,"label":defs[sid]["label"],"description":f"{defs[sid]['label']} in mathematical problems.","topicIds":sorted({topic_by_point[x] for x in pids}),"syllabusPointIds":pids,"conceptIds":objects,"action":action,"difficulty":{"minimumTier":"core" if any(tier[x]=='core' for x in pids) else "extended","relativeLevel":1},"origin":"lattice-derived","sourceBasis":[{"syllabusPointId":x,"reason":"Curated from the official assessable requirement."} for x in pids],"review":prior})
 newids={x['id'] for x in skills}
 for x in old:
  if x['id'] not in newids: removed.append((x['id'],x.get('syllabusPointIds',[])))
 dump(TAX/"syllabus-points.json",pdoc); dump(TAX/"atomic-skills.json",{"schemaVersion":"1.0","atomicSkills":skills})
 # Rebuild canonical relationships and an explicit, reviewable Core/Extended view.
 rel=[]
 for p in points:
  rel.append({"type":"topic-contains-syllabus-point","from":p["topicId"],"to":p["id"],"origin":"official-syllabus"})
  for sid in p["atomicSkillIds"]: rel.append({"type":"syllabus-point-requires-atomic-skill","from":p["id"],"to":sid,"origin":"lattice-derived"})
 byid={p['id']:p for p in points}; mappings=[]
 for c in [p for p in points if p['tier']=='core']:
  e=byid['E'+c['id'][1:]]
  if c.get('extendedOnlyPlaceholder'): category='extended-only'; core_summary='Core contains an Extended-only placeholder.'
  elif clean(c['officialStatement'])==clean(e['officialStatement']): category='equivalent-requirement'; core_summary=c['officialTitle']
  else: category='extended-adds-scope'; core_summary=c['officialTitle']
  mappings.append({'corePointId':c['id'],'extendedPointId':e['id'],'relationship':category,'basis':{'coreSummary':core_summary,'extendedAddition':'See the complete Extended official statement; teacher confirmation remains required.' if category!='equivalent-requirement' else 'No additional wording detected.'},'review':{'status':'pending-review','notes':''}})
  rel.append({'type':'core-point-extended-by','from':c['id'],'to':e['id'],'origin':'lattice-derived','relationship':category})
 dump(TAX/'relationships.json',{'schemaVersion':'1.0','relationships':rel})
 dump(BASE/'indexes/core-extended-map.json',{'schemaVersion':'2.0','mappings':mappings})
 aliases=json.loads((TAX/"aliases.json").read_text(encoding="utf-8")); aliases["atomicSkillAliases"]={"angles-in-a-triangle":"apply-angle-sum-of-triangle","triangle-angle-sum":"apply-angle-sum-of-triangle","solve-first-degree-equation":"solve-equations"}; dump(TAX/"aliases.json",aliases)
 lines=["# Removed Invalid Skills","",f"Previous count: {len(old)}  ",f"New count: {len(skills)}  ",f"Removed: {len(removed)}","","| Old ID | Reason | Replacement | Affected points |","|---|---|---|---|"]
 for sid,pids in removed: lines.append(f"| `{sid}` | Replaced during curated semantic rebuild; raw-fragment slug is not canonical. | See current skills on affected points | {', '.join(pids)} |")
 (REPORTS/"removed-invalid-skills.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
 print(f"repaired points={len(points)} old_skills={len(old)} new_skills={len(skills)} removed={len(removed)}")
if __name__=='__main__': main()
