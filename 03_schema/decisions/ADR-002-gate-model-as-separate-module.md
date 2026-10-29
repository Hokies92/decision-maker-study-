# ADR-002 — The gate model as a separate module

**Status:** proposed (P3.S01) · **Provenance:** requirement RECALL_DESIGNER (Scott, 2026-10-29); design INFERRED (Claude)

## Context
Scott (D3-1): "Yes. I want the gates to be a way we interface with other research and work."

The five gates are Scott's model, not a property of this survey (`design_intent.md` §2.2). Other sources — another survey, CRM stage data, coaching notes, a published study — need to attach to the same gates without adopting this survey's 37 questions.

## Options
1. Gates as a column on threads. Describes the model; cannot be used by anything else.
2. Gates as elements inside the study schema. Usable here only.
3. **Gates as their own small module with permanent IDs and a crosswalk.**

## Decision
Option 3. `gates.xsd` defines:

- **GateModel** — `id`, `version`, author, a definition quoting Scott.
- **Gate** ×5 — permanent IDs `TARGET`, `ACCESS`, `AGREE`, `VISION`, `CASE`; `order` 1–5; Scott's question for each gate, quoted (`design_intent.md` §2.2.2); provenance.
- **State** — exactly two values: `1` = yes (advance), `0` = not yes (Scott, 2026-10-29, `design_intent.md` §2.3a). The close is not a gate; the contract is a terminal state outside the value communication process (§2.2.3).
- **Crosswalk** — a list of mappings, each from an outside item to one gate:
  - `source` (which study, dataset or tool), `itemRef` (its own identifier), `itemText` (optional);
  - `gate`, and `fit` ∈ {`direct`, `partial`, `context`};
  - `provenance`, `note`.

This study's own threads reach the gates through Scott's grouping (ADR-003), not through the crosswalk. The crosswalk is for everything outside the study.

## Consequences
- Any dataset that maps its items to the five gate IDs can be compared with this study gate by gate, without sharing questions.
- Gate IDs never change within `gates/v1`. Renaming or adding a gate is a major version of the gate model only.
- The study schema imports the module; gate references in the study (groups, decision paths) are checked against the five IDs.
