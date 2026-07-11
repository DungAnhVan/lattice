from __future__ import annotations
import hashlib,json,re,shutil,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
from extract_0580_syllabus import score
from promote_0580_taxonomy import merge_collection,POINT_REQUIRED,POINT_MUTABLE,plan
def load(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def digest():
 h=hashlib.sha256()
 for p in sorted((ROOT/'internal-content/0580/syllabus/taxonomy').glob('*.json')):h.update(p.read_bytes())
 return h.hexdigest()
class Gate1CRepairTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.points=load('internal-content/0580/syllabus/taxonomy/syllabus-points.json')['syllabusPoints']; c.p={x['id']:x for x in c.points}; c.skills=load('internal-content/0580/syllabus/taxonomy/atomic-skills.json')['atomicSkills']; c.s={x['id']:x for x in c.skills}; c.pcfg=load('config/0580-atomic-skills.json')['points']; c.clauses=load('config/0580-syllabus-clauses.json')['points']; c.groups=load('config/0580-skill-groups.json')['groups']; c.maps=load('config/0580-core-extended-map.json')['mappings']; c.raw={x['rawSourceId']:x for x in load('internal-content/0580/syllabus/extraction/raw-syllabus-points.json')['records']}
 def test_01_e26_has_no_quadratic_inequality(self): self.assertNotIn('solve-quadratic-inequality',self.pcfg['E2.6']['atomicSkills'])
 def test_02_e26_has_graphical_region_skills(self): self.assertLessEqual({'represent-linear-inequality-region-graphically','interpret-linear-inequality-region'},set(self.pcfg['E2.6']['atomicSkills']))
 def test_03_e26_lists_region_inequalities(self): self.assertIn('list-inequalities-defining-region',self.pcfg['E2.6']['atomicSkills'])
 def test_04_e62_shortest_perpendicular(self): self.assertIn('identify-perpendicular-distance-as-shortest-distance',self.pcfg['E6.2']['atomicSkills'])
 def test_05_e64_recognise_coverage(self): self.assertLessEqual({'recognise-sine-graph','recognise-cosine-graph','recognise-tangent-graph'},set(self.pcfg['E6.4']['atomicSkills']))
 def test_06_e64_sketch_coverage(self): self.assertLessEqual({'sketch-sine-graph','sketch-cosine-graph','sketch-tangent-graph'},set(self.pcfg['E6.4']['atomicSkills']))
 def test_07_e64_interpret_and_solve(self): self.assertLessEqual({'interpret-sine-graph','interpret-cosine-graph','interpret-tangent-graph','solve-trigonometric-equation-in-given-domain'},set(self.pcfg['E6.4']['atomicSkills']))
 def test_08_e66_no_control_character(self): self.assertIsNone(re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]',self.p['E6.6']['officialTitle']+self.p['E6.6']['officialStatement']))
 def test_09_e66_title_contains_3d(self): self.assertIn('in 3D',self.p['E6.6']['officialTitle'])
 def test_10_e66_line_plane_angle(self): self.assertIn('calculate-angle-between-line-and-plane',self.pcfg['E6.6']['atomicSkills'])
 def test_11_every_assessable_point_has_clauses(self): self.assertEqual({p['id'] for p in self.points if not p.get('extendedOnlyPlaceholder')},set(self.clauses))
 def test_12_every_clause_has_skill_or_review(self): self.assertTrue(all(c['atomicSkillIds'] or c['coverageStatus']=='needs-review' for x in self.clauses.values() for c in x['clauses']))
 def test_13_point_skills_equal_clause_union(self):
  for pid,x in self.clauses.items(): self.assertEqual(set(self.pcfg[pid]['atomicSkills']),{s for c in x['clauses'] for s in c['atomicSkillIds']})
 def test_14_covered_actions_have_evidence(self):
  for x in self.clauses.values():
   for c in x['clauses']: self.assertLessEqual(set(c['requiredActions']),{a for m in c['skillMappings'] for a in m['coversActions']})
 def test_15_no_known_unsupported_skills(self): self.assertNotIn('apply-tangent-chord-theorem',self.pcfg['E4.8']['atomicSkills'])
 def test_16_group_count_greater_than_nine(self): self.assertGreater(len(self.groups),9)
 def test_17_no_group_duplicates_topic(self): self.assertFalse({'number','algebra-and-graphs','coordinate-geometry','geometry','mensuration','trigonometry','transformations-and-vectors','probability','statistics'}&set(self.groups))
 def test_18_every_group_has_multiple_skills(self): self.assertTrue(all(len(x['atomicSkillIds'])>=2 for x in self.groups.values()))
 def test_19_every_skill_has_group(self): self.assertTrue(all(x['skillGroupIds'] for x in self.skills))
 def test_20_group_inverse_is_exact(self):
  inv={sid:{g for g,x in self.groups.items() if sid in x['atomicSkillIds']} for sid in self.s}; self.assertTrue(all(inv[sid]==set(x['skillGroupIds']) for sid,x in self.s.items()))
 def test_21_no_generated_description_boilerplate(self): self.assertFalse(any('This supports the assessed requirement' in x['description'] or 'showing the required mathematical' in x['description'] for x in self.skills))
 def test_22_descriptions_have_substance(self): self.assertTrue(all(12<=len(x['description'].split())<=65 for x in self.skills))
 def test_23_confidence_derived_from_signals(self): self.assertTrue(all(score(x['signals'])[0]==x['confidence'] for x in self.raw.values()))
 def test_24_control_character_reduces_confidence(self):
  signals={k:False for k in ['controlCharactersFound','footerLeakageFound','detachedTitleFragmentFound','formulaLayoutAmbiguity','continuationAmbiguity']}; signals.update({'codeDetected':True,'titleDetected':True,'statementDetected':True,'notesColumnDetected':True}); clean=score(signals)[0]; signals['controlCharactersFound']=True; self.assertLess(score(signals)[0],clean)
 def test_25_promotion_preserves_identity(self):
  mp,ms,rel,changes=plan(); old=self.p['C1.1']; new={x['id']:x for x in mp['syllabusPoints']}['C1.1']; self.assertEqual((old['topicId'],old['syllabusCode'],old['sourceReferences']),(new['topicId'],new['syllabusCode'],new['sourceReferences']))
 def test_26_promotion_refuses_incomplete_draft(self):
  canonical={'schemaVersion':'1.0','syllabusPoints':[self.p['C1.1']]}; draft={'schemaVersion':'1.0','syllabusPoints':[{'id':'C1.1'}]}
  with self.assertRaises(ValueError):merge_collection(canonical,draft,'syllabusPoints',POINT_REQUIRED,POINT_MUTABLE)
 def test_27_promotion_requires_confirm(self): self.assertEqual(2,subprocess.run([sys.executable,'scripts/promote_0580_taxonomy.py'],cwd=ROOT,capture_output=True).returncode)
 def test_28_mapping_index_matches_config(self): self.assertEqual(load('config/0580-core-extended-map.json'),load('internal-content/0580/syllabus/indexes/core-extended-map.json'))
 def test_29_exact_72_mapping_pairs(self): self.assertEqual(72,len({(x['corePointId'],x['extendedPointId']) for x in self.maps}))
 def test_30_validation_is_read_only(self):
  before=digest(); self.assertEqual(0,subprocess.run([sys.executable,'scripts/validate_0580_taxonomy.py'],cwd=ROOT,capture_output=True).returncode); self.assertEqual(before,digest())
 def test_31_draft_generation_is_read_only(self):
  before=digest(); subprocess.run([sys.executable,'scripts/build_0580_drafts.py'],cwd=ROOT,check=True,capture_output=True); self.assertEqual(before,digest())
 def test_32_index_generation_is_read_only(self):
  before=digest(); subprocess.run([sys.executable,'scripts/generate_0580_indexes.py'],cwd=ROOT,check=True,capture_output=True); self.assertEqual(before,digest())
 def test_33_all_clauses_machine_covered_before_pass(self): self.assertEqual(0,sum(c['coverageStatus']!='covered' for x in self.clauses.values() for c in x['clauses']))
 def test_34_promotion_rolls_back_on_post_validation_failure(self):
  before=digest(); root=ROOT/'internal-content/0580/syllabus/backups'; existing=set(root.glob('*')) if root.exists() else set(); r=subprocess.run([sys.executable,'scripts/promote_0580_taxonomy.py','--confirm','--simulate-post-validation-failure'],cwd=ROOT,capture_output=True)
  for path in (set(root.glob('*'))-existing if root.exists() else set()): shutil.rmtree(path)
  self.assertEqual(4,r.returncode); self.assertEqual(before,digest())
