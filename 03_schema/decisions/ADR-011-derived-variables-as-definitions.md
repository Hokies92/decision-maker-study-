# ADR-011 — Derived variables stored as definitions, not values

**Status:** proposed (P3.S01) · **Provenance:** INFERRED (Claude); variable list RECON_DATA / INFERRED (`variable_dictionary.csv`)

## Context
The variable dictionary has 189 variables: 130 collected, 51 derivable (6 recodes + 45 summary measures), 8 missing. 47 definitions are Claude's and await Scott's review (Q-P2a). Phase 4 computes from the schema.

## Decision
- **Variable** — `id`, `kind` (`item` | `summary` | `missing`), `status` (`collected` | `derivable` | `missing`), `item` (→ Item, where one exists), label, type, valid values, `rule` (required when `derivable`), provenance.
- Collected variables point to their items; their values are the results.
- Derivable variables carry the rule only. No computed value is stored in v1.
- Missing variables are listed with a `reason`, so the gap is visible in the data file itself.

## Consequences
- Unconfirmed definitions never become numbers in the instance before Scott reviews them.
- Phase 4 techniques reference the rule by variable ID; a computed-values section can be added in a minor version.
