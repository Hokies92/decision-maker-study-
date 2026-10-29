# ADR-004 — The result cell

**Status:** proposed (P3.S01) · **Provenance:** INFERRED (Claude); structure RECON_DATA (`results.csv`); scope approved by Scott in D1 (2026-10-27)

## Context
The source is group-level tables (SRC-002). Phase 2 extracted 24,552 cells: one per item × answer option × cohort; 24,224 values, 328 not asked by design. README (D1): "XSD storing results as cells (question × option × breakout group)."

## Decision
One **Result** element per cell:

| Field | Meaning |
|---|---|
| `item` | → Item |
| `option` | option sequence number within the item's scale (→ Option) |
| `cohort` | → Cohort |
| `status` | `value` or `notAsked` |
| `share` | proportion 0–1, exactly as tabulated; absent when `notAsked` |
| `base` | the cohort's base n for this item |
| `cite` | source cell, e.g. `SRC-002 Industry 7!B15` |
| `baseCite` | the base row's cell |
| `provenance` | `RECON_DATA` |

Results are grouped under the item they belong to, so a thread's results can be read in one place.

Where the same item and cohort appear on more than one sheet, the cell is stored **once**, from the sheet `results.csv` selects. Phase 2 showed the All-respondents share agrees across all five sheets (396 of 396).

## Options considered and rejected
- Store counts instead of shares. The source gives shares and bases; counts would be derived and would round.
- Store a matrix per item. Compact, but a cell could not carry its own citation or status.

## Consequences
- Every number traces to one source cell.
- Level and stakeholder type reach the result through its cohort (ADR-005); the gate through its item's thread (ADR-003).
- Respondent-level answers, if collected later, sit in the respondent layer (ADR-009), not here.

## Implementation notes (P3.S02–S05)

Added after the XSD was built and validated against real data. Each note records where the implementation refines the decision above; the decision itself is unchanged.

- **Multi-select items carry no option.** For `multi_select_option` items the result is the share selecting that item, so `option` (and `scale`) are absent. For all other items, `scale` + `option` together must name an Option (composite key), and the cross-check confirms `scale` is the item's own scale.
- **Repeated cells.** The 24,552 source cells hold 22,968 distinct results; the All-respondents column repeats on all five sheets. Each result is stored once, cited from the canonical sheet "Industry 7" (as in Phase 1); the other four cells are kept as `AlsoAt` citations, so every source cell is accounted for exactly once.
