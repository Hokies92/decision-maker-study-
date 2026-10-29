# ADR-003 — Editable thread → gate assignment

**Status:** proposed (P3.S01) · **Provenance:** grouping RECALL_DESIGNER (Scott, 2026-10-28); design INFERRED (Claude)

## Context
Scott grouped all 37 threads into 7 groups (`scott_grouping.csv`). Five groups are gates; three are not: Screener metadata ("an input to 'target'"), Baseline ("Baseline only"), and Relationship accounts ("Own group", cross-gate). Scott has said regrouping must stay possible (`design_intent.md` §3; decisions log 2026-10-28).

| Group (Scott's words) | Role | Gate | Threads |
|---|---|---|---|
| Screener metadata | input | Target | 12 |
| Baseline | baseline | — | 3 |
| Access | gate | ACCESS | 5 |
| Successful meeting ("I call it agree to explore now") | gate | AGREE | 4 |
| Shared Vision | gate | VISION | 6 |
| Business Case | gate | CASE | 3 |
| Relationship accounts (open-ended) | crossGate | — (Phase 5 tags each answer) | 4 |

## Options
1. A gate attribute on each thread. Regrouping means editing the instrument.
2. A gate attribute on each result. 24,552 copies; regrouping means rewriting results.
3. **Groups and assignments as separate elements, collected in named assignment sets.**

## Decision
Option 3.
- **Group** — `id`, `label` (Scott's words, VERBATIM), `role` ∈ {`gate`, `input`, `baseline`, `crossGate`}, optional `gate` (a gate ID; required when role is `gate`; `TARGET` for the screener input).
- **AssignmentSet** — `id`, `author`, `status` ∈ {`current`, `alternative`, `superseded`}, provenance. Each set assigns every thread to one group.
- Exactly one set is `current`. v1 ships with one set: `SCOTT-2026-10-28`, `current`, `RECALL_DESIGNER`.

## Consequences
- Regrouping adds a new set and changes which one is `current`. Nothing else changes, and the old grouping stays on record.
- An alternative reading (a client's, or a draft) can sit next to Scott's without replacing it.
- A result's gate is always found by following `Result → Item → Thread → Assignment (current set) → Group → Gate`.
