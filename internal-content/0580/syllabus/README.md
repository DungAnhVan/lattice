# Cambridge IGCSE Mathematics 0580 — Syllabus Taxonomy (Gate 1)

## Gate 1B data flow

The pipeline is separated into `extraction/` (regenerable coordinate-aware PDF blocks), `drafts/` (regenerable review candidates), and `taxonomy/` (canonical data). Extraction, draft building, index generation, and validation never overwrite canonical taxonomy.

```text
npm run extract:0580-syllabus
npm run build:0580-drafts
npm run promote:0580-taxonomy -- --confirm
npm run generate:0580-indexes
npm run validate:0580-taxonomy
npm run test:0580-taxonomy
npm run gate1b:0580
```

Promotion writes `reports/promotion-diff.md`, requires `--confirm`, creates a timestamped backup, and refuses conflicts with approved records.

## What is Lattice?

Lattice is an internal curriculum and past-paper corpus system. Its core principle is **one canonical record per syllabus point and per question**; topics, skills, papers, and syllabus points are **views** generated through indexes, never duplicate content folders.

## What Gate 1 produces

Gate 1 builds the **versioned syllabus taxonomy** for Cambridge IGCSE Mathematics **0580** (examination years **2025–2027**). It does **not** extract or classify past-paper questions.

Deliverables in this directory:

```
sources/          Official syllabus PDF (unmodified)
taxonomy/         Canonical JSON records
indexes/          Generated views (safe to delete and rebuild)
schemas/          JSON Schema definitions
reports/          Extraction, validation, and unresolved-item reports
```

## Canonical data principle

| Layer | Source | File |
|-------|--------|------|
| Syllabus | Official Cambridge PDF | `taxonomy/syllabus.json` |
| Topics | Official Cambridge structure | `taxonomy/topics.json` |
| Syllabus points | Official codes & statements | `taxonomy/syllabus-points.json` |
| Atomic skills | Lattice pedagogical decomposition | `taxonomy/atomic-skills.json` |
| Relationships | Derived links | `taxonomy/relationships.json` |
| Aliases | Non-canonical wording map | `taxonomy/aliases.json` |

**Indexes are not sources of truth.** They are always regenerated from canonical files.

## Official syllabus points vs atomic skills

- **Syllabus points** (`C1.1`, `E4.6`, …) use official Cambridge codes and preserve `officialStatement` wording from the syllabus.
- **Atomic skills** (`identify-prime-numbers`, `apply-triangle-angle-sum`, …) are Lattice-derived, verb-led, reusable actions for diagnosis and practice. They are marked `"origin": "lattice-derived"`.

## Page numbering

All `sourceReferences.page` values use **one-based** PDF page numbers (first page of the PDF = 1).

## Regenerating indexes

```bash
npm run generate:0580-indexes
```

Or directly:

```bash
python scripts/generate_0580_indexes.py
```

## Building and validating

Full Gate 1 pipeline (build taxonomy + validate):

```bash
npm run gate1:0580
```

Individual steps:

```bash
npm run build:0580-taxonomy      # Extract from PDF and write canonical files
npm run validate:0580-taxonomy   # Structural + schema validation (exit code 1 on failure)
```

Validation checks include: schema compliance, referential integrity, complete official code coverage (72 Core + 72 Extended), index parity, no invented codes, and forbidden skill ID patterns.

## Teacher review

1. Read `reports/unresolved-items.md` for flagged judgments.
2. Inspect records with `"review": { "status": "pending-review" }` in taxonomy files.
3. Compare uncertain Core/Extended pairs using `indexes/core-extended-map.json`.
4. Approve or edit atomic skills; add aliases rather than duplicating skills.
5. Re-run validation after changes.

## Future question classification (example)

When past-paper extraction is built (later gate), a question will reference taxonomy IDs like this:

```json
{
  "primaryTopic": "geometry",
  "secondaryTopics": [],
  "syllabusPoints": ["E4.6"],
  "atomicSkills": [
    "calculate-unknown-angles-and-give-simple",
    "calculate-unknown-angles-and-give-geometric",
    "know-and-use-angle-properties-of"
  ]
}
```

This links one canonical question record to official requirements and teachable skills without copying content into topic folders.

## Topics covered

| Order | Topic ID | Official title |
|------:|----------|----------------|
| 1 | `number` | Number |
| 2 | `algebra-and-graphs` | Algebra and graphs |
| 3 | `coordinate-geometry` | Coordinate geometry |
| 4 | `geometry` | Geometry |
| 5 | `mensuration` | Mensuration |
| 6 | `trigonometry` | Trigonometry |
| 7 | `transformations-and-vectors` | Transformations and vectors |
| 8 | `probability` | Probability |
| 9 | `statistics` | Statistics |

## Taxonomy version

`0580-2025-2027-v1` — see `taxonomy/syllabus.json` for metadata and source provenance.
