# ADR-010 — Time is order; no study date

**Status:** proposed (P3.S01) · **Provenance:** exclusion README / CLAUDE.md; time model RECALL_DESIGNER (Scott, 2026-10-28, `design_intent.md` §2.2.5; D3-2, 2026-10-29); design INFERRED (Claude)

## Context
The study date is deliberately excluded from analysis (README, CLAUDE.md). Scott: "I track time more like Leibniz than Newton and I use the gates to align event time "bergionsian" and factor in kairos time (creating coachable moments) so the easiest thing to manage is choices."

## Decision
- No element or attribute in `dms/v1` holds the study's fielding date, wave year, or any date derived from file names.
- The only time in the schema is in decision paths (ADR-009): `seq` (required, order) and `observedAt` (optional, clock).
- No calculation in the schema depends on clock time. Kairos is not a stored flag; a coachable moment is identified by position — the event before a state change.

## Consequences
- Paths of very different length compare step for step.
- If a future dataset needs explicit kairos markers, they are a minor-version addition to `GateEvent`.

## Implementation notes (P3.S02–S05)

Added after the XSD was built and validated against real data. Each note records where the implementation refines the decision above; the decision itself is unchanged.

- **Verbatim wording may contain a year.** S7 asks about revenues "in calendar year …"; that wording is stored VERBATIM (item stem, dimension definition, variable label). The rule is that no field holds a date and no analysis uses one; the cross-check (C13) enforces exactly that and reports the copies of the S7 wording.
