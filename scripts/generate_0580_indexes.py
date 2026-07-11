#!/usr/bin/env python3
"""Regenerate Lattice 0580 syllabus indexes from canonical taxonomy files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYLLABUS_DIR = ROOT / "internal-content" / "0580" / "syllabus"
TAXONOMY_DIR = SYLLABUS_DIR / "taxonomy"
INDEX_DIR = SYLLABUS_DIR / "indexes"


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main() -> int:
    topics = load_json(TAXONOMY_DIR / "topics.json")["topics"]
    points = load_json(TAXONOMY_DIR / "syllabus-points.json")["syllabusPoints"]
    skills = load_json(TAXONOMY_DIR / "atomic-skills.json")["atomicSkills"]
    core_ext = load_json(INDEX_DIR / "core-extended-map.json")

    by_topic = {}
    for topic in topics:
        tid = topic["id"]
        by_topic[tid] = {
            "syllabusPointIds": sorted(topic["syllabusPointIds"]),
            "atomicSkillIds": sorted(
                {sid for p in points if p["topicId"] == tid for sid in p.get("atomicSkillIds", [])}
            ),
        }

    by_point = {
        p["id"]: {"topicId": p["topicId"], "atomicSkillIds": sorted(p.get("atomicSkillIds", []))}
        for p in points
    }

    by_skill = {
        s["id"]: {"topicIds": sorted(s["topicIds"]), "syllabusPointIds": sorted(s["syllabusPointIds"])}
        for s in skills
    }

    write_json(INDEX_DIR / "by-topic.json", by_topic)
    write_json(INDEX_DIR / "by-syllabus-point.json", by_point)
    write_json(INDEX_DIR / "by-atomic-skill.json", by_skill)
    write_json(INDEX_DIR / "core-extended-map.json", core_ext)

    print(f"Regenerated indexes: {len(by_topic)} topics, {len(by_point)} points, {len(by_skill)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
