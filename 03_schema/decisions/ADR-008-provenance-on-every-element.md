# ADR-008 — Provenance on every element

**Status:** proposed (P3.S01) · **Provenance:** requirement GOVERNANCE §7; design INFERRED (Claude); synthetic label approved by Scott (D3-3, 2026-10-29)

## Context
GOVERNANCE §7: every reconstructed fact is tagged `VERBATIM`, `RECON_DATA`, `RECON_REPORT`, `RECALL_DESIGNER`, `INFERRED`, or `MISSING`. Scott approved one synthetic test record (D3-3). An invented record must never be mistaken for data.

## Decision
- A `provenance` attribute is **required** on every element that states a fact (items, cohorts, results, flags, links, assignments, gates, events…).
- Its type is an enumeration of the six governance tags plus `SYNTHETIC`.
- `SYNTHETIC` is allowed by the XSD (XSD 1.0 cannot make it conditional) but the cross-check (P3.S05) fails if it appears anywhere outside `03_schema/tests/`, or if a file under `tests/` lacks it.
- Where one element holds facts of different origin (an item's wording is VERBATIM, its type INFERRED), the element carries separate attributes: `textProvenance`, `typeProvenance` — the same split `question_map.csv` already uses.
- `INFERRED` items Scott approved keep `INFERRED` and add `reviewed="confirmedByScott"` (decisions log 2026-10-29: approval is not recollection).

## Consequences
- Any consumer can filter to source facts only (`VERBATIM` + `RECON_DATA`) with one XPath predicate.
- Provenance counts in the cross-check come straight from the instance.
