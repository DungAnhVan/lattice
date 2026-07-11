#!/usr/bin/env python3
"""Validate Cambridge IGCSE Mathematics 0580 syllabus taxonomy."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SYLLABUS_DIR = ROOT / "internal-content" / "0580" / "syllabus"
TAXONOMY_DIR = SYLLABUS_DIR / "taxonomy"
INDEX_DIR = SYLLABUS_DIR / "indexes"
SCHEMA_DIR = SYLLABUS_DIR / "schemas"
REPORTS_DIR = SYLLABUS_DIR / "reports"

EXPECTED_CORE = [f"C{t}.{s}" for t, n in {1: 18, 2: 13, 3: 7, 4: 8, 5: 5, 6: 6, 7: 4, 8: 4, 9: 7}.items() for s in range(1, n + 1)]
EXPECTED_EXTENDED = [f"E{t}.{s}" for t, n in {1: 18, 2: 13, 3: 7, 4: 8, 5: 5, 6: 6, 7: 4, 8: 4, 9: 7}.items() for s in range(1, n + 1)]
CODE_PATTERN = re.compile(r"^[CE][1-9]\.[0-9]+$")


class ValidationResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.passed: list[str] = []

    @property
    def ok(self) -> bool:
        return not self.errors


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_schema(result: ValidationResult, schema_name: str, data, item_label: str) -> None:
    schema = load_json(SCHEMA_DIR / schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        for err in errors[:20]:
            result.errors.append(f"Schema {item_label}: {err.message} at {list(err.path)}")
        if len(errors) > 20:
            result.errors.append(f"Schema {item_label}: ... and {len(errors) - 20} more errors")
    else:
        result.passed.append(f"JSON Schema valid: {item_label}")


def compute_indexes(topics, points, skills):
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
    return by_topic, by_point, by_skill


def main() -> int:
    result = ValidationResult()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    syllabus = load_json(TAXONOMY_DIR / "syllabus.json")
    topics_doc = load_json(TAXONOMY_DIR / "topics.json")
    points_doc = load_json(TAXONOMY_DIR / "syllabus-points.json")
    skills_doc = load_json(TAXONOMY_DIR / "atomic-skills.json")
    relationships = load_json(TAXONOMY_DIR / "relationships.json")
    aliases = load_json(TAXONOMY_DIR / "aliases.json")

    topics = topics_doc["topics"]
    points = points_doc["syllabusPoints"]
    skills = skills_doc["atomicSkills"]

    validate_schema(result, "syllabus.schema.json", syllabus, "syllabus.json")
    validate_schema(result, "topic.schema.json", topics_doc, "topics.json")
    validate_schema(result, "syllabus-point.schema.json", points_doc, "syllabus-points.json")
    validate_schema(result, "atomic-skill.schema.json", skills_doc, "atomic-skills.json")
    validate_schema(result, "relationships.schema.json", relationships, "relationships.json")

    topic_ids = {t["id"] for t in topics}
    point_ids = {p["id"] for p in points}
    skill_ids = {s["id"] for s in skills}

    if len(topic_ids) != len(topics):
        result.errors.append("Duplicate topic IDs detected")
    else:
        result.passed.append("No duplicate topic IDs")

    if len(point_ids) != len(points):
        result.errors.append("Duplicate syllabus point IDs detected")
    else:
        result.passed.append("No duplicate syllabus point IDs")

    if len(skill_ids) != len(skills):
        result.errors.append("Duplicate atomic skill IDs detected")
    else:
        result.passed.append("No duplicate atomic skill IDs")

    for p in points:
        if p["topicId"] not in topic_ids:
            result.errors.append(f"Syllabus point {p['id']} references missing topic {p['topicId']}")
        for sid in p.get("atomicSkillIds", []):
            if sid not in skill_ids:
                result.errors.append(f"Syllabus point {p['id']} references missing skill {sid}")
        if not p.get("sourceReferences"):
            result.errors.append(f"Syllabus point {p['id']} has no source reference")
        if not CODE_PATTERN.match(p["id"]):
            result.errors.append(f"Invented or invalid official code format: {p['id']}")

    for s in skills:
        for pid in s["syllabusPointIds"]:
            if pid not in point_ids:
                result.errors.append(f"Skill {s['id']} references missing point {pid}")
        if not s.get("sourceBasis"):
            result.errors.append(f"Skill {s['id']} has no sourceBasis")

    for rel in relationships["relationships"]:
        if rel["type"].startswith("topic-") and rel["from"] not in topic_ids:
            result.errors.append(f"Relationship from missing topic: {rel['from']}")
        if rel["type"] in ("syllabus-point-requires-atomic-skill", "syllabus-point-prerequisite-of", "syllabus-point-related-to", "core-point-extended-by") and rel["from"] not in point_ids:
            if rel["type"] != "core-point-extended-by" or rel["from"] not in point_ids:
                result.errors.append(f"Relationship from missing point: {rel['from']}")
        if rel["type"] == "topic-contains-syllabus-point" and rel["to"] not in point_ids:
            result.errors.append(f"Relationship to missing point: {rel['to']}")
        if rel["type"] == "syllabus-point-requires-atomic-skill" and rel["to"] not in skill_ids:
            result.errors.append(f"Relationship to missing skill: {rel['to']}")
        if rel["type"] == "core-point-extended-by" and rel["to"] not in point_ids:
            result.errors.append(f"Core-extended relationship to missing point: {rel['to']}")

    core_ids = sorted([p["id"] for p in points if p["tier"] == "core"])
    ext_ids = sorted([p["id"] for p in points if p["tier"] == "extended"])
    missing_core = [c for c in EXPECTED_CORE if c not in core_ids]
    missing_ext = [c for c in EXPECTED_EXTENDED if c not in ext_ids]
    if missing_core:
        result.errors.append(f"Missing Core syllabus codes: {missing_core}")
    else:
        result.passed.append("All expected Core syllabus codes present")
    if missing_ext:
        result.errors.append(f"Missing Extended syllabus codes: {missing_ext}")
    else:
        result.passed.append("All expected Extended syllabus codes present")

    extra_core = [c for c in core_ids if c not in EXPECTED_CORE]
    extra_ext = [c for c in ext_ids if c not in EXPECTED_EXTENDED]
    if extra_core or extra_ext:
        result.errors.append(f"Invented official codes: core={extra_core}, extended={extra_ext}")
    else:
        result.passed.append("No invented official syllabus codes")

    exp_by_topic, exp_by_point, exp_by_skill = compute_indexes(topics, points, skills)
    for name, expected, actual_path in [
        ("by-topic.json", exp_by_topic, INDEX_DIR / "by-topic.json"),
        ("by-syllabus-point.json", exp_by_point, INDEX_DIR / "by-syllabus-point.json"),
        ("by-atomic-skill.json", exp_by_skill, INDEX_DIR / "by-atomic-skill.json"),
    ]:
        actual = load_json(actual_path)
        if actual != expected:
            result.errors.append(f"Index mismatch: {name}")
        else:
            result.passed.append(f"Index matches canonical data: {name}")

    core_ext = load_json(INDEX_DIR / "core-extended-map.json")
    if core_ext.get("uncertainEquivalence"):
        result.warnings.append(
            f"{len(core_ext['uncertainEquivalence'])} Core/Extended pairs flagged for teacher review"
        )

    placeholder_core = [p["id"] for p in points if p.get("extendedOnlyPlaceholder") and p["tier"] == "core"]
    if placeholder_core:
        result.passed.append(f"Core Extended-only placeholders preserved: {len(placeholder_core)}")

    for s in skills:
        if re.search(r"question-\d|paper-\d|20\d{2}", s["id"]):
            result.errors.append(f"Skill ID contains forbidden reference: {s['id']}")

    report_lines = [
        "# Validation Report — Gate 1 (0580 Syllabus Taxonomy)",
        "",
        f"- **Validation date:** {now}",
        f"- **Gate status:** {'PASS' if result.ok else 'FAIL'}",
        "",
        "## Tests run",
        "",
        "- JSON Schema validation (syllabus, topics, syllabus-points, atomic-skills, relationships)",
        "- Referential integrity (topics, points, skills, relationships)",
        "- Official code completeness (72 Core + 72 Extended)",
        "- Index regeneration parity",
        "- Forbidden skill ID patterns",
        "",
        "## Passed checks",
        "",
    ]
    for item in result.passed:
        report_lines.append(f"- {item}")
    report_lines.extend(["", "## Warnings", ""])
    if result.warnings:
        for w in result.warnings:
            report_lines.append(f"- {w}")
    else:
        report_lines.append("- None")
    report_lines.extend(["", "## Failed checks", ""])
    if result.errors:
        for e in result.errors:
            report_lines.append(f"- {e}")
    else:
        report_lines.append("- None")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "validation-report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Validation: {'PASS' if result.ok else 'FAIL'}")
    print(f"  Passed: {len(result.passed)}")
    print(f"  Warnings: {len(result.warnings)}")
    print(f"  Errors: {len(result.errors)}")
    for e in result.errors[:10]:
        print(f"  ERROR: {e}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
