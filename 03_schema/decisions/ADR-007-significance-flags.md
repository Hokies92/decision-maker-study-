# ADR-007 — Significance as a flag on question × dimension

**Status:** proposed (P3.S01) · **Provenance:** INFERRED (Claude); structure RECON_DATA (`significance.csv`, anomaly A16)

## Context
SRC-002 stores significance tests as 1,688 cell comments, one on each question's header row per breakout dimension (A16). Phase 2 parsed them into 1,686 flags: significant 233, not significant 924, not tested 529. The test statistic is not in the source; the report header states 95% confidence.

## Decision
**SignificanceFlag** — `item` (the question block), `dimension` (→ Dimension, or `ALL`), `state` ∈ {`significant`, `notSignificant`, `notTested`}, `tableSize` (when stated), `comment` (the source comment, VERBATIM), `cite`, `provenance` `RECON_DATA`.

Flags are not attached to cells. The source tests whether a dimension and a question are related; it does not test individual cells.

## Consequences
- "Which dimensions matter for this gate" is answerable directly: flags → item → thread → gate.
- Each flag is a ready-made statistical link between a screener dimension and a question thread (decisions log 2026-10-29), for Phase 4.
- The confidence level is a study-level attribute (`0.95`, RECON_DATA from the report header); no test statistic is stored, because none exists in source.
