# Extraction Report — Gate 1 (Cambridge IGCSE Mathematics 0580)

## Source PDF

| Field | Value |
|-------|-------|
| File | `internal-content/0580/syllabus/sources/2025-2027-syllabus.pdf` |
| Title | Cambridge IGCSE Mathematics 0580 syllabus for examination in 2025, 2026 and 2027 |
| Publication code | 662466 |
| Syllabus version | 3 (May 2024) |
| Download URL | https://www.cambridgeinternational.org/Images/662466-2025-2027-syllabus.pdf |

## Pages examined

- Full PDF: **71 pages** (1-based page numbering throughout this taxonomy)
- Subject content extracted from pages **12–56**
  - Core subject content: pages **12–31**
  - Extended subject content: pages **32–56**

## Extraction counts

| Record type | Count |
|-------------|------:|
| Topics | 9 |
| Core syllabus points | 72 |
| Extended syllabus points | 72 |
| Atomic skills (Lattice-derived) | 228 |
| Relationships | auto-generated from canonical records |

## Extraction method

1. **PDF text extraction** using PyMuPDF (`fitz`) from the official Cambridge PDF.
2. **Section location** by scanning pages 12–56 for Core (`C*.*`) and Extended (`E*.*`) subject content tables.
3. **Syllabus point parsing** using tab-aware regex to handle Cambridge table layout variants (single- and double-digit sub-codes, with and without explicit `Notes and examples` row headers).
4. **Statement cleaning** to remove page footers, navigation text, and PDF control characters while preserving official assessable wording.
5. **Notes/examples separation** — syllabus guidance (`Includes…`, `Candidates are…`, `e.g.…`) moved to `notes` and `examplesFromSyllabus` where detected; assessable statements kept in `officialStatement`.
6. **Atomic skill derivation** — pedagogical decomposition from numbered requirements and bullet lists under official headers; merged by label and ID to avoid duplicates.
7. **Index generation** — `by-topic`, `by-syllabus-point`, `by-atomic-skill`, and `core-extended-map` derived from canonical files only.

## Assumptions

- Official topic numbering (1–9) maps to stable Lattice topic IDs (`number`, `algebra-and-graphs`, etc.).
- Core syllabus points marked **Extended content only.** are preserved as placeholder records with `extendedOnlyPlaceholder: true`.
- `C4.1` / `E4.1` continuation rows in the PDF are merged into a single canonical record per code.
- `relativeLevel` on atomic skills is a local Lattice progression estimate (1–3), not an official Cambridge scale.
- Page numbers in `sourceReferences` are **one-based** (first PDF page = 1).

## Sections intentionally excluded

- Syllabus introduction, aims, and marketing content (pages 1–11)
- Assessment structure, formula lists, mathematical conventions, command words (pages 57–67)
- Grade descriptions and syllabus change log (pages 68–71)
- Past papers, specimen papers, and published resources (not present in this gate)

## Taxonomy version

`0580-2025-2027-v1`
