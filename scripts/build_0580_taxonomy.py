#!/usr/bin/env python3
"""Build Cambridge IGCSE Mathematics 0580 (2025-2027) syllabus taxonomy for Lattice."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
SYLLABUS_DIR = ROOT / "internal-content" / "0580" / "syllabus"
PDF_PATH = SYLLABUS_DIR / "sources" / "2025-2027-syllabus.pdf"
TAXONOMY_DIR = SYLLABUS_DIR / "taxonomy"
INDEX_DIR = SYLLABUS_DIR / "indexes"
SCHEMA_DIR = SYLLABUS_DIR / "schemas"
REPORTS_DIR = SYLLABUS_DIR / "reports"

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

TOPIC_MAP = {
    1: ("number", "Number"),
    2: ("algebra-and-graphs", "Algebra and graphs"),
    3: ("coordinate-geometry", "Coordinate geometry"),
    4: ("geometry", "Geometry"),
    5: ("mensuration", "Mensuration"),
    6: ("trigonometry", "Trigonometry"),
    7: ("transformations-and-vectors", "Transformations and vectors"),
    8: ("probability", "Probability"),
    9: ("statistics", "Statistics"),
}

CODE_RE = re.compile(r"^([CE])(\d+)\.(\d+)\s+(.+?)\s+Notes and examples\s*$", re.MULTILINE)
EXTENDED_ONLY_RE = re.compile(
    r"^([CE]\d+\.\d+)\s+Extended content only\.\s*$", re.MULTILINE
)
TOPIC_HEADER_RE = re.compile(r"^(\d)\s+(.+?)\s*$", re.MULTILINE)
SECTION_RE = re.compile(
    r"(Core subject content|Extended subject content)", re.MULTILINE
)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def verb_from_statement(text: str) -> str:
    text = text.strip().rstrip(".")
    first = re.split(r"[:\n]", text, maxsplit=1)[0].strip()
    first = re.sub(r"^\d+\s+", "", first)
    verbs = [
        "identify",
        "use",
        "understand",
        "calculate",
        "recognise",
        "recognize",
        "solve",
        "draw",
        "interpret",
        "construct",
        "factorise",
        "factorize",
        "expand",
        "simplify",
        "order",
        "give",
        "find",
        "apply",
        "know",
        "read",
        "classify",
        "compare",
        "change",
        "represent",
        "list",
        "complete",
        "manipulate",
        "rationalise",
        "rationalize",
        "describe",
        "measure",
        "convert",
        "estimate",
        "round",
        "enter",
        "appreciate",
        "distinguish",
    ]
    lower = first.lower()
    for v in verbs:
        if lower.startswith(v):
            return v
    words = slugify(first).split("-")
    return words[0] if words else "apply"


def derive_skill_id(statement: str, context: str = "") -> str:
    base = slugify(statement[:80])
    if not base:
        base = slugify(context)
    base = re.sub(r"^\d+-", "", base)
    if len(base) > 60:
        base = "-".join(base.split("-")[:6])
    return base


def extract_pdf_text() -> tuple[str, list[tuple[int, str]]]:
    doc = fitz.open(PDF_PATH)
    pages: list[tuple[int, str]] = []
    full = []
    for i in range(doc.page_count):
        text = doc[i].get_text()
        pages.append((i + 1, text))
        full.append(text)
    doc.close()
    return "\n".join(full), pages


def clean_footer_noise(text: str) -> str:
    patterns = [
        r"Cambridge IGCSE Mathematics 0580 syllabus for 2025, 2026 and 2027\.[^\n]*\n",
        r"Back to contents page www\.cambridgeinternational\.org/igcse \d+\n",
        r"\d+ Number \(continued\)\n",
        r"\d+ Algebra and graphs \(continued\)\n",
        r"\d+ Coordinate geometry \(continued\)\n",
        r"\d+ Geometry \(continued\)\n",
        r"\d+ Mensuration \(continued\)\n",
        r"\d+ Trigonometry \(continued\)\n",
        r"\d+ Transformations and vectors \(continued\)\n",
        r"\d+ Probability \(continued\)\n",
        r"\d+ Statistics \(continued\)\n",
    ]
    for p in patterns:
        text = re.sub(p, "", text)
    return text


def truncate_at_footer(text: str) -> str:
    markers = [
        r"\nCambridge IGCSE Mathematics 0580",
        r"\nBack to contents page",
        r"\nwww\.cambridgeinternational\.org",
        r"\n\d+\nwww\.cambridgeinternational",
        r"\n\d+\t\nNumber \(continued\)",
        r"\n\d+\t\n[A-Za-z].*\(continued\)",
    ]
    for m in markers:
        match = re.search(m, text)
        if match:
            text = text[: match.start()]
    return text.strip()


def clean_statement_text(text: str) -> str:
    text = truncate_at_footer(text)
    text = text.replace("\u0007", "").replace("\u2002", " ")
    text = re.sub(r"\t•\s*\n", "• ", text)
    text = re.sub(r"\t+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_statement_notes_examples(block: str) -> tuple[str, list[str], list[str]]:
    block = clean_statement_text(block)
    notes: list[str] = []
    examples: list[str] = []

    # Split assessable statement from notes/examples sections
    split_patterns = [
        r"(?i)\nIncludes\b",
        r"(?i)\nExample tasks include:?\s*",
        r"(?i)\nExample definition of sets:",
        r"(?i)\nExamples include:",
        r"(?i)\nExample calculations include:",
        r"(?i)\ne\.g\.\b",
        r"(?i)\nCandidates are\b",
        r"(?i)\nProblems may include\b",
        r"(?i)\nRequired formulas\b",
        r"(?i)\nKnowledge of\b",
        r"(?i)\nNotation used\b",
        r"(?i)\nWhen representing\b",
        r"(?i)\nThe following conventions\b",
        r"(?i)\nData may be\b",
        r"(?i)\nProbabilities should be\b",
        r"(?i)\nAngles will be\b",
        r"(?i)\nPositive and fractional\b",
        r"(?i)\nQuestions will not\b",
        r"(?i)\nA ruler must\b",
        r"(?i)\nStem-and-leaf\b",
        r"(?i)\nPlotted points\b",
        r"(?i)\nA line of best fit\b",
        r"(?i)\nCombined events\b",
        r"(?i)\nIn tree diagrams\b",
        r"(?i)\nVenn diagrams\b",
        r"(?i)\nWith powers no higher\b",
        r"(?i)\nFactorise means\b",
        r"(?i)\nSimplify means\b",
        r"(?i)\nExtended candidates\b",
        r"(?i)\nCore candidates\b",
    ]

    statement = block
    remainder = ""
    earliest = len(block)
    for pat in split_patterns:
        m = re.search(pat, block)
        if m and m.start() < earliest:
            earliest = m.start()
            remainder = block[m.start() :]
            statement = block[: m.start()].strip()

    if remainder:
        for pat in [r"(?i)^Includes\b", r"(?i)^Candidates are\b", r"(?i)^Knowledge of\b", r"(?i)^Required formulas\b"]:
            if re.match(pat, remainder.lstrip()):
                notes.append(remainder.strip())
            elif re.match(r"(?i)^(e\.g\.|Example)", remainder.lstrip()):
                examples.append(remainder.strip())
            else:
                notes.append(remainder.strip())

    return statement, notes, examples


def locate_content_sections(pages: list[tuple[int, str]]) -> tuple[str, str]:
    """Extract Core and Extended subject content from PDF pages (not TOC)."""
    core_parts: list[str] = []
    ext_parts: list[str] = []
    mode = None
    for page_num, text in pages:
        if page_num < 12:
            continue
        if page_num >= 57:
            break
        if re.search(r"Extended subject content|E1\.1\t", text) and "E1.1" in text:
            mode = "extended"
        elif mode is None and (re.search(r"Core subject content|C1\.1\t", text)):
            mode = "core"
        if mode == "core":
            core_parts.append(text)
        elif mode == "extended":
            ext_parts.append(text)
    return "\n".join(core_parts), "\n".join(ext_parts)


def parse_subject_content(full_text: str, pages: list[tuple[int, str]]) -> dict:
    core_text = clean_footer_noise(locate_content_sections(pages)[0])
    ext_text = clean_footer_noise(locate_content_sections(pages)[1])

    def page_for_code(code: str, tier: str) -> int:
        search = f"{code}\t"
        start_page = 12 if tier == "core" else 32
        for page_num, text in pages:
            if page_num >= start_page and search in text:
                return page_num
        return start_page

    def parse_section(section_text: str, tier: str) -> list[dict]:
        records_by_code: dict[str, dict] = {}
        expected_prefix = "C" if tier == "core" else "E"
        chunks = re.split(r"(?=[CE]\d+\.\d+\t)", section_text)
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue

            m_ext = re.match(r"^([CE]\d+\.\d+)\t(?:\n|\s+)Extended content only\.\s*", chunk)
            if m_ext:
                code = m_ext.group(1)
                if not code.startswith(expected_prefix):
                    continue
                topic_num = int(code[1])
                topic_id, topic_title = TOPIC_MAP.get(topic_num, (f"topic-{topic_num}", f"Topic {topic_num}"))
                records_by_code[code] = {
                    "id": code,
                    "tier": tier,
                    "topicId": topic_id,
                    "officialCode": code,
                    "officialTitle": "Extended content only",
                    "officialStatement": "Extended content only.",
                    "notes": [],
                    "examplesFromSyllabus": [],
                    "extendedOnlyPlaceholder": True,
                    "sourceReferences": [
                        {
                            "page": page_for_code(code, tier),
                            "section": f"{tier.title()} subject content / {topic_title}",
                        }
                    ],
                }
                continue

            m_code = re.match(
                r"^([CE]\d+\.\d+)\t(?:\n|\s+)(.+?)\t\nNotes and examples\n(.*)$",
                chunk,
                re.DOTALL,
            )
            if m_code:
                code, title, body = m_code.group(1), m_code.group(2).strip(), m_code.group(3).strip()
            else:
                m_alt = re.match(
                    r"^([CE]\d+\.\d+)\t\n([^\n]+)\n(.*)$",
                    chunk,
                    re.DOTALL,
                )
                if not m_alt:
                    continue
                code, title, body = m_alt.group(1), m_alt.group(2).strip(), m_alt.group(3).strip()

            if not code.startswith(expected_prefix):
                continue
            if "(continued)" in title.lower():
                if code in records_by_code:
                    existing = records_by_code[code]
                    extra_stmt, extra_notes, extra_examples = split_statement_notes_examples(body)
                    if extra_stmt:
                        existing["officialStatement"] = f"{existing['officialStatement']}\n{extra_stmt}".strip()
                    existing["notes"].extend(extra_notes)
                    existing["examplesFromSyllabus"].extend(extra_examples)
                    existing["sourceReferences"].append(
                        {
                            "page": page_for_code(code, tier),
                            "section": f"{tier.title()} subject content / {TOPIC_MAP[int(code[1])][1]} (continued)",
                            "tableRow": code,
                        }
                    )
                continue

            topic_num = int(code[1])
            topic_id, topic_title = TOPIC_MAP.get(topic_num, (f"topic-{topic_num}", f"Topic {topic_num}"))
            statement, notes, examples = split_statement_notes_examples(body)
            if not statement:
                statement = title
            statement = clean_statement_text(statement)
            notes = list(dict.fromkeys(notes))
            examples = list(dict.fromkeys(examples))
            records_by_code[code] = {
                "id": code,
                "tier": tier,
                "topicId": topic_id,
                "officialCode": code,
                "officialTitle": title,
                "officialStatement": statement,
                "notes": notes,
                "examplesFromSyllabus": examples,
                "extendedOnlyPlaceholder": False,
                "sourceReferences": [
                    {
                        "page": page_for_code(code, tier),
                        "section": f"{tier.title()} subject content / {topic_title}",
                        "tableRow": code,
                    }
                ],
            }

        records = list(records_by_code.values())
        records.sort(
            key=lambda r: (r["officialCode"][0], int(r["officialCode"].split(".")[0][1:]), int(r["officialCode"].split(".")[1]))
        )
        return records

    core_points = parse_section(core_text, "core")
    ext_points = parse_section(ext_text, "extended")
    return {"core": core_points, "extended": ext_points}


def statement_to_skills(point: dict) -> list[dict]:
    if point.get("extendedOnlyPlaceholder"):
        return []

    statement = clean_statement_text(point["officialStatement"])
    title = point["officialTitle"]
    topic_id = point["topicId"]
    point_id = point["id"]
    tier = point["tier"]

    skills: list[dict] = []
    seen_ids: set[str] = set()

    def add_skill(label: str, description: str, relative_level: int = 1):
        label = re.sub(r"\s+", " ", label).strip()
        if len(label) < 6 or re.search(r"(?i)cambridge|contents page|www\.", label):
            return
        sid_base = derive_skill_id(label, title)
        if not sid_base or sid_base.isdigit() or len(sid_base) < 4:
            sid_base = f"{slugify(title)}-{len(skills) + 1}"
        action = verb_from_statement(label)
        sid = sid_base
        n = 2
        while sid in seen_ids:
            sid = f"{sid_base}-{n}"
            n += 1
        seen_ids.add(sid)
        skills.append(
            {
                "id": sid,
                "label": label.strip().rstrip("."),
                "description": description.strip(),
                "topicIds": [topic_id],
                "syllabusPointIds": [point_id],
                "conceptIds": [w for w in slugify(title).split("-") if w][:5],
                "action": action,
                "difficulty": {"minimumTier": tier, "relativeLevel": relative_level},
                "origin": "lattice-derived",
                "sourceBasis": [{"syllabusPointId": point_id, "reason": f"Derived from official statement in {point_id}"}],
                "review": {"status": "pending-review", "notes": ""},
            }
        )

    numbered = re.findall(
        r"(?:^|\n)\s*(\d+)\s+([^\n]+(?:\n(?!\s*\d+\s)[^\n]+)*)",
        statement,
    )
    bullets = re.findall(r"•\s*([^\n•]+)", statement)
    header_match = re.match(r"^([^:\n]+:)", statement)

    if numbered:
        for _, item in numbered:
            item = re.sub(r"\s+", " ", item).strip()
            add_skill(item[0].upper() + item[1:] if item else item, item, 2 if " and " in item.lower() else 1)
    elif bullets and header_match:
        header = header_match.group(1).strip()
        add_skill(header.rstrip(":"), statement.split("\n")[0], 1)
        verb = verb_from_statement(header)
        for b in bullets:
            b = re.sub(r"\s+", " ", b).strip().rstrip(".")
            if len(b) < 3:
                continue
            label = f"{verb.capitalize()} {b}" if not b[0].isupper() else b
            add_skill(label, f"{header} {b}", 1)
    elif bullets:
        for b in bullets:
            b = re.sub(r"\s+", " ", b).strip().rstrip(".")
            add_skill(b[0].upper() + b[1:] if b else b, b, 1)
    else:
        first_para = statement.split("\n\n")[0].strip()
        lines = [ln.strip() for ln in first_para.split("\n") if ln.strip()]
        text = lines[0] if lines else title
        add_skill(text, statement, 1)

    if not skills:
        add_skill(title, statement, 1)

    return skills


def merge_duplicate_skills(all_skills: list[dict]) -> tuple[list[dict], dict[str, str]]:
    by_label: dict[str, dict] = {}
    aliases: dict[str, str] = {}

    for skill in all_skills:
        key = slugify(skill["label"])[:80]
        if key in by_label:
            existing = by_label[key]
            existing["syllabusPointIds"] = sorted(set(existing["syllabusPointIds"] + skill["syllabusPointIds"]))
            existing["topicIds"] = sorted(set(existing["topicIds"] + skill["topicIds"]))
            existing["sourceBasis"].extend(skill["sourceBasis"])
            aliases[skill["id"]] = existing["id"]
        else:
            by_label[key] = skill

    by_id: dict[str, dict] = {}
    for skill in by_label.values():
        sid = skill["id"]
        if sid in by_id:
            existing = by_id[sid]
            existing["syllabusPointIds"] = sorted(set(existing["syllabusPointIds"] + skill["syllabusPointIds"]))
            existing["topicIds"] = sorted(set(existing["topicIds"] + skill["topicIds"]))
            existing["sourceBasis"].extend(skill["sourceBasis"])
            if skill["label"] != existing["label"]:
                aliases[skill["id"]] = existing["id"]
        else:
            by_id[sid] = skill

    canonical = []
    for skill in by_id.values():
        skill["syllabusPointIds"] = sorted(set(skill["syllabusPointIds"]))
        skill["topicIds"] = sorted(set(skill["topicIds"]))
        canonical.append(skill)
    canonical.sort(key=lambda s: s["id"])
    return canonical, aliases


def build_core_extended_map(core_points: list[dict], ext_points: list[dict]) -> dict:
    core_by_suffix = {p["officialCode"][1:]: p for p in core_points}
    ext_by_suffix = {p["officialCode"][1:]: p for p in ext_points}

    shared = []
    core_only = []
    extended_only = []
    extended_builds_on = []
    uncertain = []

    all_suffixes = sorted(set(core_by_suffix) | set(ext_by_suffix), key=lambda s: [int(x) for x in s.split(".")])

    for suffix in all_suffixes:
        c = core_by_suffix.get(suffix)
        e = ext_by_suffix.get(suffix)
        if c and e:
            if c.get("extendedOnlyPlaceholder") and not e.get("extendedOnlyPlaceholder"):
                extended_builds_on.append(
                    {
                        "corePointId": c["id"],
                        "extendedPointId": e["id"],
                        "relationship": "extended-builds-on-core-placeholder",
                        "notes": "Core syllabus point is a placeholder; Extended contains assessable content.",
                    }
                )
            elif c.get("extendedOnlyPlaceholder") and e.get("extendedOnlyPlaceholder"):
                shared.append({"corePointId": c["id"], "extendedPointId": e["id"], "relationship": "both-placeholder"})
            else:
                c_stmt = re.sub(r"\s+", " ", c["officialStatement"]).strip().lower()
                e_stmt = re.sub(r"\s+", " ", e["officialStatement"]).strip().lower()
                if c_stmt == e_stmt:
                    shared.append({"corePointId": c["id"], "extendedPointId": e["id"], "relationship": "equivalent-wording"})
                elif c_stmt in e_stmt or e_stmt.startswith(c_stmt[:40]):
                    extended_builds_on.append(
                        {
                            "corePointId": c["id"],
                            "extendedPointId": e["id"],
                            "relationship": "extended-extends-core",
                            "notes": "Extended statement adds depth beyond Core wording.",
                        }
                    )
                else:
                    uncertain.append(
                        {
                            "corePointId": c["id"],
                            "extendedPointId": e["id"],
                            "coreStatement": c["officialStatement"][:200],
                            "extendedStatement": e["officialStatement"][:200],
                            "notes": "Wording differs; teacher review required to confirm equivalence.",
                        }
                    )
        elif c and not e:
            core_only.append(c["id"])
        elif e and not c:
            extended_only.append(e["id"])

    return {
        "schemaVersion": "1.0",
        "sharedRequirements": shared,
        "coreOnlyRequirements": core_only,
        "extendedOnlyRequirements": extended_only,
        "extendedBuildsOnCore": extended_builds_on,
        "uncertainEquivalence": uncertain,
    }


def build_relationships(topics: list[dict], points: list[dict], skills: list[dict], core_ext_map: dict) -> dict:
    rels = []
    for topic in topics:
        for pid in topic["syllabusPointIds"]:
            rels.append(
                {"type": "topic-contains-syllabus-point", "from": topic["id"], "to": pid, "origin": "official-syllabus"}
            )
    for point in points:
        for sid in point.get("atomicSkillIds", []):
            rels.append(
                {
                    "type": "syllabus-point-requires-atomic-skill",
                    "from": point["id"],
                    "to": sid,
                    "origin": "lattice-derived",
                }
            )
    for item in core_ext_map["extendedBuildsOnCore"]:
        rels.append(
            {
                "type": "core-point-extended-by",
                "from": item["corePointId"],
                "to": item["extendedPointId"],
                "origin": "official-syllabus",
            }
        )
    for item in core_ext_map["sharedRequirements"]:
        if item["relationship"] in ("equivalent-wording", "both-placeholder"):
            rels.append(
                {
                    "type": "core-point-extended-by",
                    "from": item["corePointId"],
                    "to": item["extendedPointId"],
                    "origin": "official-syllabus",
                    "equivalence": "shared-requirement",
                }
            )

    rels.sort(key=lambda r: (r["type"], r["from"], r["to"]))
    return {"schemaVersion": "1.0", "relationships": rels}


def build_indexes(topics: list[dict], points: list[dict], skills: list[dict]) -> dict:
    by_topic: dict = {}
    for topic in topics:
        by_topic[topic["id"]] = {
            "syllabusPointIds": sorted(topic["syllabusPointIds"]),
            "atomicSkillIds": sorted(
                {sid for p in points if p["topicId"] == topic["id"] for sid in p.get("atomicSkillIds", [])}
            ),
        }

    by_point = {}
    for p in points:
        by_point[p["id"]] = {"topicId": p["topicId"], "atomicSkillIds": sorted(p.get("atomicSkillIds", []))}

    by_skill = {}
    for s in skills:
        by_skill[s["id"]] = {"topicIds": sorted(s["topicIds"]), "syllabusPointIds": sorted(s["syllabusPointIds"])}

    return by_topic, by_point, by_skill


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main() -> int:
    if not PDF_PATH.exists():
        print(f"Missing PDF: {PDF_PATH}", file=sys.stderr)
        return 1

    full_text, pages = extract_pdf_text()
    parsed = parse_subject_content(full_text, pages)

    core_points = parsed["core"]
    ext_points = parsed["extended"]
    all_points_raw = core_points + ext_points

    all_skills_raw: list[dict] = []
    for point in all_points_raw:
        all_skills_raw.extend(statement_to_skills(point))

    skills, skill_alias_map = merge_duplicate_skills(all_skills_raw)

    skill_by_id = {s["id"]: s for s in skills}
    for point in all_points_raw:
        point_skills = []
        for sk in statement_to_skills(point):
            canonical_id = skill_alias_map.get(sk["id"], sk["id"])
            if canonical_id in skill_by_id:
                point_skills.append(canonical_id)
        point["atomicSkillIds"] = sorted(set(point_skills))
        point["syllabusCode"] = "0580"
        point["prerequisiteSyllabusPointIds"] = []
        point["relatedSyllabusPointIds"] = []
        point["origin"] = "official-syllabus"
        point["review"] = {"status": "pending-review", "notes": ""}

    topics = []
    for order, (num, (tid, title)) in enumerate(TOPIC_MAP.items(), start=1):
        sp_ids = sorted([p["id"] for p in all_points_raw if p["topicId"] == tid], key=lambda x: (x[0], int(x.split(".")[1])))
        topics.append(
            {
                "id": tid,
                "syllabusCode": "0580",
                "officialTitle": title,
                "normalizedTitle": tid,
                "order": order,
                "description": f"Cambridge IGCSE Mathematics 0580 topic {num}: {title}.",
                "syllabusPointIds": sp_ids,
                "origin": "official-syllabus",
                "sourceReferences": [{"page": 8, "section": "Content overview"}],
            }
        )

    syllabus = {
        "schemaVersion": "1.0",
        "id": "cambridge-igcse-mathematics-0580-2025-2027",
        "board": "cambridge",
        "qualification": "igcse",
        "subject": "mathematics",
        "syllabusCode": "0580",
        "validFrom": 2025,
        "validTo": 2027,
        "taxonomyVersion": "0580-2025-2027-v1",
        "source": {
            "file": "../sources/2025-2027-syllabus.pdf",
            "title": "Cambridge IGCSE Mathematics 0580 syllabus for examination in 2025, 2026 and 2027",
            "publicationCode": "662466",
            "syllabusVersion": 3,
            "published": "May 2024",
            "accessedLocally": True,
        },
        "topicIds": [t["id"] for t in topics],
        "createdAt": NOW,
        "updatedAt": NOW,
    }

    core_ext_map = build_core_extended_map(core_points, ext_points)
    relationships = build_relationships(topics, all_points_raw, skills, core_ext_map)
    by_topic, by_point, by_skill = build_indexes(topics, all_points_raw, skills)

    topic_aliases = {"algebra": "algebra-and-graphs", "graphs": "algebra-and-graphs"}
    aliases = {
        "atomicSkillAliases": {k: v for k, v in sorted(skill_alias_map.items()) if k != v},
        "topicAliases": topic_aliases,
        "conceptAliases": {},
    }

    write_json(TAXONOMY_DIR / "syllabus.json", syllabus)
    write_json(TAXONOMY_DIR / "topics.json", {"schemaVersion": "1.0", "topics": topics})
    write_json(TAXONOMY_DIR / "syllabus-points.json", {"schemaVersion": "1.0", "syllabusPoints": all_points_raw})
    write_json(TAXONOMY_DIR / "atomic-skills.json", {"schemaVersion": "1.0", "atomicSkills": skills})
    write_json(TAXONOMY_DIR / "relationships.json", relationships)
    write_json(TAXONOMY_DIR / "aliases.json", aliases)
    write_json(INDEX_DIR / "by-topic.json", by_topic)
    write_json(INDEX_DIR / "by-syllabus-point.json", by_point)
    write_json(INDEX_DIR / "by-atomic-skill.json", by_skill)
    write_json(INDEX_DIR / "core-extended-map.json", core_ext_map)

    stats = {
        "topics": len(topics),
        "core_points": len(core_points),
        "extended_points": len(ext_points),
        "atomic_skills": len(skills),
        "pages": len(pages),
        "uncertain_equivalence": len(core_ext_map["uncertainEquivalence"]),
    }
    write_json(REPORTS_DIR / "build-stats.json", stats)
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
