#!/usr/bin/env python3
"""Build disposable review drafts without modifying canonical taxonomy."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'internal-content/0580/syllabus'; TAX=BASE/'taxonomy'; OUT=BASE/'drafts'
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 copies={'syllabus-points.json':'syllabus-points.draft.json','atomic-skills.json':'atomic-skills.draft.json'}
 for src,dst in copies.items(): (OUT/dst).write_text((TAX/src).read_text(encoding='utf-8'),encoding='utf-8')
 core=json.loads((BASE/'indexes/core-extended-map.json').read_text(encoding='utf-8')); (OUT/'core-extended-map.draft.json').write_text(json.dumps(core,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Built drafts/ only; canonical review fields and files were not changed')
if __name__=='__main__': main()
