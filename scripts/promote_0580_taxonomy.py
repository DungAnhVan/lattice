#!/usr/bin/env python3
"""Explicit, backed-up promotion of reviewed drafts to canonical taxonomy."""
from __future__ import annotations
import argparse, json, shutil
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'internal-content/0580/syllabus'; TAX=BASE/'taxonomy'; DRAFT=BASE/'drafts'; REPORT=BASE/'reports/promotion-diff.md'
PAIRS=[('syllabus-points.draft.json','syllabus-points.json','syllabusPoints'),('atomic-skills.draft.json','atomic-skills.json','atomicSkills')]
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--confirm',action='store_true'); a=ap.parse_args(); summary=[]
 for draft,canon,key in PAIRS:
  new=json.loads((DRAFT/draft).read_text(encoding='utf-8')); old=json.loads((TAX/canon).read_text(encoding='utf-8')); ni={x['id']:x for x in new[key]}; oi={x['id']:x for x in old[key]}
  approved=[i for i,x in oi.items() if x.get('review',{}).get('status')=='approved' and ni.get(i)!=x]
  summary.append((canon,len(ni.keys()-oi.keys()),len(oi.keys()-ni.keys()),sum(ni.get(i)!=oi.get(i) for i in ni.keys()&oi.keys()),approved))
 lines=['# Promotion Diff','',f"Generated: {datetime.now(timezone.utc).isoformat()}",'','| File | Added | Removed | Changed | Approved conflicts |','|---|---:|---:|---:|---|']+[f"| {x[0]} | {x[1]} | {x[2]} | {x[3]} | {', '.join(x[4]) or 'none'} |" for x in summary]; REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 if not a.confirm: print('Refusing to write canonical taxonomy without --confirm; diff report created'); return 2
 if any(x[4] for x in summary): print('Refusing to overwrite approved canonical records'); return 3
 backup=BASE/'backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); backup.mkdir(parents=True)
 for draft,canon,key in PAIRS: shutil.copy2(TAX/canon,backup/canon); shutil.copy2(DRAFT/draft,TAX/canon)
 print(f'Promoted drafts after confirmation; backup: {backup}'); return 0
if __name__=='__main__': raise SystemExit(main())
