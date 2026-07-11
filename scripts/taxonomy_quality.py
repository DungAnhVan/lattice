"""Shared semantic checks for the Cambridge 0580 taxonomy."""
from __future__ import annotations

import re

APPROVED_ACTIONS = {
    "identify", "recognise", "represent", "read", "write", "compare", "order",
    "classify", "calculate", "convert", "estimate", "round", "simplify", "expand",
    "factorise", "solve", "substitute", "construct", "draw", "plot", "interpret",
    "describe", "apply", "use", "find", "determine", "prove", "evaluate",
    "differentiate", "transform", "measure", "complete", "form", "sketch", "recall",
    "choose", "preserve", "add", "change", "collect", "continue", "design", "divide",
    "enlarge", "enter", "express", "model", "multiply", "rationalise", "reflect",
    "rotate", "substitute", "subtract", "translate", "assess", "extract", "list", "relate",
}
STOP_WORDS = {"a", "an", "and", "in", "of", "or", "the", "to", "with", "i", "ii"}
FOOTER_MARKERS = ("back to contents page", "cambridgeinternational.org", "cambridge igcse mathematics 0580 syllabus")
END_CONJUNCTION = re.compile(r"\b(and|or|of|to|with)\s*[.:;]?\s*$", re.I)
END_PAGE = re.compile(r"(?:^|\n)\s*\d{1,3}\s*$")


def official_content_issues(statement: str, examples: list[str] | None = None) -> list[str]:
    issues: list[str] = []
    text = statement.strip()
    lower = text.lower()
    if not text:
        issues.append("empty official statement")
    if END_CONJUNCTION.search(text):
        issues.append("statement appears truncated")
    if END_PAGE.search(text):
        issues.append("statement ends with a page number")
    if any(marker in lower for marker in FOOTER_MARKERS):
        issues.append("footer or website text in statement")
    if any(ord(ch) < 32 and ch not in "\n\t" for ch in text):
        issues.append("control character in statement")
    for example in examples or []:
        if END_PAGE.search(example.strip()):
            issues.append("example ends with a page number")
        if any(marker in example.lower() for marker in FOOTER_MARKERS):
            issues.append("footer or website text in example")
    return issues


def skill_issues(skill: dict) -> list[str]:
    issues: list[str] = []
    sid = skill.get("id", "")
    parts = sid.split("-")
    action = skill.get("action", "")
    if not re.fullmatch(r"[a-z]+(?:-[a-z0-9]+)+", sid):
        issues.append("ID is not meaningful lowercase kebab-case")
    if sid[:1].isdigit():
        issues.append("ID begins with a number")
    if not parts or parts[0] not in APPROVED_ACTIONS:
        issues.append("ID does not begin with an approved action")
    if action not in APPROVED_ACTIONS or (parts and action != parts[0]):
        issues.append("action does not match ID action")
    if parts and parts[-1] in STOP_WORDS:
        issues.append("ID ends with a stop word")
    if len(parts) < 2:
        issues.append("ID has no meaningful mathematical object")
    if sid == "ab-sin-c" or re.fullmatch(r"(?:[a-z]-?){2,6}", sid):
        issues.append("ID is a formula fragment")
    if any(c.lower() in STOP_WORDS for c in skill.get("conceptIds", [])):
        issues.append("conceptIds contain stop-word noise")
    if not skill.get("syllabusPointIds"):
        issues.append("skill is linked to no syllabus point")
    if not skill.get("label", "").strip() or not skill.get("description", "").strip():
        issues.append("label or description is empty")
    return issues
