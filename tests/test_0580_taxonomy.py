from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
from taxonomy_quality import official_content_issues, skill_issues

def skill(sid='solve-linear-equation',action='solve'):
 return {'id':sid,'label':'Solve a linear equation','description':'Solve a one-variable linear equation.','action':action,'conceptIds':['linear-equation'],'syllabusPointIds':['C2.5']}
def digest():
 h=hashlib.sha256()
 for p in sorted((ROOT/'internal-content/0580/syllabus/taxonomy').glob('*.json')): h.update(p.read_bytes())
 return h.hexdigest()

class QualityTests(unittest.TestCase):
 def test_statement_ending_and(self): self.assertTrue(official_content_issues('Understand sets and'))
 def test_statement_ending_page(self): self.assertTrue(official_content_issues('Order quantities.\n14'))
 def test_footer(self): self.assertTrue(official_content_issues('Use numbers. Back to contents page'))
 def test_number_skill(self): self.assertTrue(skill_issues(skill('2-bad-skill','2')))
 def test_stopword_skill(self): self.assertTrue(skill_issues(skill('apply-angle-of','apply')))
 def test_numeric_action(self): self.assertTrue(skill_issues(skill(action='5')))
 def test_formula_fragment(self): self.assertTrue(skill_issues(skill('ab-sin-c','ab')))
 def test_valid_skill(self): self.assertEqual([],skill_issues(skill()))
 def test_index_generation_read_only(self):
  before=digest(); subprocess.run([sys.executable,'scripts/generate_0580_indexes.py'],cwd=ROOT,check=True,capture_output=True); self.assertEqual(before,digest())
 def test_validation_read_only(self):
  before=digest(); subprocess.run([sys.executable,'scripts/validate_0580_taxonomy.py'],cwd=ROOT,check=True,capture_output=True); self.assertEqual(before,digest())
 def test_draft_preserves_approved_canonical(self):
  p=ROOT/'internal-content/0580/syllabus/taxonomy/atomic-skills.json'; before=p.read_bytes(); subprocess.run([sys.executable,'scripts/build_0580_drafts.py'],cwd=ROOT,check=True,capture_output=True); self.assertEqual(before,p.read_bytes())
 def test_promotion_requires_confirmation(self):
  r=subprocess.run([sys.executable,'scripts/promote_0580_taxonomy.py'],cwd=ROOT,capture_output=True); self.assertEqual(2,r.returncode)
 def test_placeholder_not_equivalent(self):
  m=json.loads((ROOT/'internal-content/0580/syllabus/indexes/core-extended-map.json').read_text(encoding='utf8'))['mappings']; self.assertFalse(any(x['relationship']=='equivalent-requirement' and x['corePointId'] in {'C1.17','C1.18'} for x in m))
 def test_malformed_formula_requires_review(self): self.assertTrue(skill_issues(skill('ab-sin-c','ab')))

if __name__=='__main__': unittest.main()
