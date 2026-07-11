from __future__ import annotations
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def digest():
 h=hashlib.sha256()
 for p in sorted((ROOT/'internal-content/0580/syllabus/taxonomy').glob('*.json')): h.update(p.read_bytes())
 return h.hexdigest()
class Gate1CTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.points=load('internal-content/0580/syllabus/taxonomy/syllabus-points.json')['syllabusPoints']; c.skills=load('internal-content/0580/syllabus/taxonomy/atomic-skills.json')['atomicSkills']; c.groups=load('internal-content/0580/syllabus/taxonomy/skill-groups.json')['skillGroups']; c.cfg=load('config/0580-atomic-skills.json')['points']; c.defs=load('config/0580-skill-definitions.json')['skills']; c.maps=load('config/0580-core-extended-map.json')['mappings']
 def test_curated_map_covers_nonplaceholders(self): self.assertEqual({p['id'] for p in self.points if not p.get('extendedOnlyPlaceholder')},set(self.cfg))
 def test_every_configured_skill_defined(self): self.assertEqual({s for x in self.cfg.values() for s in x['atomicSkills']},set(self.defs))
 def test_no_title_fallback_or_broad_skill(self): self.assertFalse({'apply-algebraic-manipulation','apply-area-and-perimeter','apply-functions-concepts','solve-equations'} & {s['id'] for s in self.skills})
 def test_no_unmapped_clauses(self): self.assertFalse(any(x['unmappedClauses'] for x in self.cfg.values()))
 def test_descriptions_have_no_filler(self): self.assertFalse(any('in mathematical problems' in s['description'].lower() or 'perform the specified operation' in s['description'].lower() for s in self.skills))
 def test_groups_do_not_replace_atomic_links(self): self.assertTrue(all(p['atomicSkillIds'] for p in self.points if not p.get('extendedOnlyPlaceholder')))
 def test_all_72_pairs_mapped(self): self.assertEqual(72,len(self.maps))
 def test_pair_skill_diffs_are_real(self):
  by={p['id']:set(p['atomicSkillIds']) for p in self.points}
  for m in self.maps:
   self.assertLessEqual(set(m['sharedSkillIds']),by[m['corePointId']]&by[m['extendedPointId']]); self.assertLessEqual(set(m['extendedOnlySkillIds']),by[m['extendedPointId']]-by[m['corePointId']])
 def test_draft_builder_is_canonical_read_only(self):
  before=digest(); subprocess.run([sys.executable,'scripts/build_0580_drafts.py'],cwd=ROOT,check=True,capture_output=True); self.assertEqual(before,digest())
 def test_confidence_one_requires_verification(self): self.assertTrue(all(p['extraction']['confidence']<1 or p['extraction']['verifiedBy'] and p['extraction']['verifiedAt'] for p in self.points))
 def test_placeholders_have_no_skills(self): self.assertTrue(all(not p['atomicSkillIds'] for p in self.points if p.get('extendedOnlyPlaceholder')))
 def test_prerequisites_valid_and_acyclic(self):
  ids={s['id'] for s in self.skills}; graph={s['id']:s['prerequisiteSkillIds'] for s in self.skills}; self.assertTrue(all(set(v)<=ids for v in graph.values())); done=set(); active=set()
  def visit(n):
   self.assertNotIn(n,active)
   if n in done:return
   active.add(n)
   for x in graph[n]:visit(x)
   active.remove(n);done.add(n)
  for n in graph:visit(n)
 def test_every_group_references_valid_skills(self): self.assertTrue(all(set(g['atomicSkillIds'])<={s['id'] for s in self.skills} for g in self.groups))
 def test_every_skill_has_group(self): self.assertTrue(all(s['skillGroupIds'] for s in self.skills))
 def test_raw_extraction_has_144_complete_records(self):
  rows=load('internal-content/0580/syllabus/extraction/raw-syllabus-points.json')['records']; self.assertEqual(144,len(rows)); self.assertTrue(all({'boundingRegions','rawTitle','rawStatement','rawNotes','rawBlocks','extractionIssues'}<=set(r) for r in rows))
