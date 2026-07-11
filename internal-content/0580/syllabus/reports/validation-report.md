# Validation Report — Gate 1 (0580 Syllabus Taxonomy)

- **Validation date:** 2026-07-11T02:04:29Z
- **Gate status:** PASS

## Tests run

- JSON Schema validation (syllabus, topics, syllabus-points, atomic-skills, relationships)
- Referential integrity (topics, points, skills, relationships)
- Official code completeness (72 Core + 72 Extended)
- Index regeneration parity
- Forbidden skill ID patterns

## Passed checks

- JSON Schema valid: syllabus.json
- JSON Schema valid: topics.json
- JSON Schema valid: syllabus-points.json
- JSON Schema valid: atomic-skills.json
- JSON Schema valid: relationships.json
- No duplicate topic IDs
- No duplicate syllabus point IDs
- No duplicate atomic skill IDs
- All expected Core syllabus codes present
- All expected Extended syllabus codes present
- No invented official syllabus codes
- Index matches canonical data: by-topic.json
- Index matches canonical data: by-syllabus-point.json
- Index matches canonical data: by-atomic-skill.json
- Core Extended-only placeholders preserved: 19

## Warnings

- 4 Core/Extended pairs flagged for teacher review

## Failed checks

- None
