# Unresolved Items — Gate 1 (Cambridge IGCSE Mathematics 0580)

Items below require teacher judgment before the taxonomy is used for high-stakes classification or mastery tracking.

## Gate 1B teacher-review queue

All 144 syllabus points, 108 atomic skills, and 72 explicit Core/Extended mappings are currently `pending-review` (324 review items total). Automated structural and semantic checks pass, but approval coverage remains 0% until a subject teacher reviews the official transcription, pedagogical decomposition, and mapping basis.

## Core / Extended equivalence uncertainty

The following Core/Extended pairs have related but non-identical official wording. They are recorded in `indexes/core-extended-map.json` under `uncertainEquivalence` and must not be treated as automatically equivalent.

| Core | Extended | Issue |
|------|----------|-------|
| C1.9 | E1.9 | Extended may add expectations beyond Core estimation wording after PDF normalisation |
| C1.10 | E1.10 | Extended adds bounds of calculation results; Core states upper/lower bounds only |
| C2.5 | E2.5 | Extended adds fractional, non-linear simultaneous, and quadratic equation scope |
| C3.3 | E3.3 | Extended adds gradient from two coordinates; Core limits to grid reading |
| C9.3 | E9.3 | Extended adds quartiles, IQR, and grouped-data mean estimate |

## Atomic skills — breadth judgments

Automated decomposition may be too broad or too narrow in these areas:

- **Geometry angle properties (C4.6 / E4.6)** — bullet properties under numbered requirements could be split further (e.g. separate skills for angles on a straight line, triangle sum, parallel-line angles) or kept as combined application skills.
- **Algebra manipulation (E2.2)** — factorisation patterns (difference of two squares, quadratics, completing the square) are partially grouped; teachers may prefer finer skills per factorisation type.
- **Graphs and functions (E2.10 / E2.11)** — function types and curve features may need additional atomic skills for diagnostic practice.
- **Trigonometry (E6.4–E6.6)** — sine/cosine rules and combined Pythagoras–trigonometry problems may need explicit prerequisite links between skills.

## Possible duplicate or alias candidates

These skills share similar labels across Core and Extended tiers and may warrant aliases after review:

- `understand-and-use-indices-positive-zero` (appears across C1.7 / E1.7 / C2.4 / E2.4 contexts)
- `understand-and-use-the-rules-of` (indices rules repeated in multiple points)
- `calculate-with-simple-and-compound-interest` (C1.13 / E1.13)

See `taxonomy/aliases.json` for current alias mappings.

## Prerequisites not inferred

No automatic prerequisite graph has been applied to syllabus points or atomic skills. Teachers should review whether to add relationships such as:

- Linear equations before simultaneous equations
- Pythagoras' theorem before right-angled trigonometry
- Angle facts before circle theorems

## PDF extraction caveats

- Some PDF control characters (`\u0007`, thin spaces) were stripped during normalisation; verify any statements with unusual notation against the source PDF.
- `C6.2` / `E6.2` use a table layout without an explicit `Notes and examples` row header; content was parsed from an alternate pattern.
- Occasional line breaks within words come from the PDF layout; official statements should be spot-checked for high-stakes use.

## Review workflow

1. Open `taxonomy/syllabus-points.json` and filter `review.status: pending-review`.
2. Compare uncertain Core/Extended pairs side-by-side using the source PDF page cited in `sourceReferences`.
3. Adjust `atomic-skills.json` labels/IDs or add entries to `aliases.json` as needed.
4. Set `review.status` to `approved` and add notes when satisfied.
5. Re-run `npm run gate1:0580` to regenerate indexes and validation report.
