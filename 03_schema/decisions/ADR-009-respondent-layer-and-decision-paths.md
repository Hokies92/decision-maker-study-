# ADR-009 — Optional respondent layer and decision paths

**Status:** proposed (P3.S01) · **Provenance:** order model RECALL_DESIGNER (Scott, D3-2, 2026-10-29); design INFERRED (Claude)

## Context
Purpose of record (Scott, 2026-10-29): the schema must later hold individual choices over time, for new data and for coaching. The source holds respondent-level text only (SRC-003, "Other" sheet), keyed by `respid`, with no function, level, or stakeholder value.

Scott (D3-2): a decision-maker's path is a numbered sequence of gate events, each with the gate, its 1 or 0, and reasons linked to the questions that name them; clock time optional. "Yes. I agree."

## Decision
`Respondents` is an optional section. A study instance without it is valid (GOVERNANCE §5 P3: "defined but optional").

- **Respondent** — `respid`, provenance.
  - **Attributes** (optional) — references to stakeholder nodes (ADR-005) for function, level, purchase role. Empty in this study. Populated only when collected; the cross-check fails if any appears with provenance `INFERRED`.
  - **TextAnswer** (0..n) — `item` (→ Item), text unchanged (`VERBATIM`), `cite`. Blank answers are not stored as answers (the P1.S08 lesson).
  - **DecisionPath** (0..n) — `id`, optional `context` (the decision or opportunity it concerns, as free text), provenance.
    - **GateEvent** (1..n) — `seq` (positive integer, unique within the path; required), `gate` (→ gate ID), `state` (`1` | `0`), optional `observedAt` (date-time), optional `actor` (`vendor` | `salesperson` | `decisionMaker`), provenance.
      - **Reason** (0..n) — `thread`, optional `item`, optional `option` (→ the question and answer that name the reason, e.g. Q15_2 "I could not envision how the value would be delivered"), optional note.

Rules:
- Events are ordered by `seq`, not by `observedAt`.
- A gate may appear more than once in a path (a 0 followed later by a 1 is recovery, not an error).
- `actor` reflects Scott's wording: "Did the vendor and then the salesperson …" (`design_intent.md` §2.2.2).

## Consequences
- Where a path stops, what came before a state change (the coachable moment), and recovery are all readable from `seq` and `state`.
- Reasons point into the instrument, so a coached path and a survey result about the same reason share an address.
- Cohort-level results and individual paths stay separate: nothing links a path to a cohort's percentages except shared gates and reasons. The ecological caveat holds (parking lot, P1.S00).
