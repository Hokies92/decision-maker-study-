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
