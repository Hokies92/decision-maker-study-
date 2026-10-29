# ADR-006 — Threads, items, and links as first-class edges

**Status:** proposed (P3.S01) · **Provenance:** INFERRED (Claude); thread model approved by Scott in D1 extension (2026-10-27); links RECON_DATA / INFERRED / RECALL_DESIGNER as in `linkages.csv`

## Context
Scott (2026-10-27): "If you can make each question its one thread, you can iterate creating graph networks or other topology maps to improve our ability to do both a) more analytical reductionism and also b) synthetic holism." P1.S08 found 381 links of 11 types; endpoints are threads (326), thread → group (37), item → thread (10), and item → item (8). One item link points to a variable that is not in the source: `S8_Bucketed` derived from raw S8 (`S8_raw`, status missing).

## Decision
- **Thread** — one per base question (37); holds its **Items** (136). Item fields follow `question_map.csv`: stem and label (VERBATIM, cited), type, role (`asked`, `attention_check`, `derived`, `text`), scale, base, piping token where present.
- **Link** — one element per edge, in a `Graph` section:
  - endpoints as typed attributes: `fromThread` | `fromItem`, and `toThread` | `toItem` | `toGroup` | `toVariable` — exactly one of each set, each checked against its target;
  - `type` (enumeration of the 11 types: `shared_scale`, `routes_to`, `breakout_of`, `derived_from`, `specify_of`, `same_respondents`, `mirror`, `same_construct`, `topic`, `relates_to`, `in_group`);
  - `directed` (true for `routes_to`, `derived_from`, `specify_of`, `breakout_of`, `in_group`);
  - `weight`, `evidence`, `provenance`.

Typed endpoint attributes, rather than one generic reference, let the XSD check every endpoint exists. `toVariable` is used only where the target is a variable with no item — today, the one link to `S8_raw`; the generator maps the source text `S8 (raw, not tabulated)` to that ID and says so in the link's evidence.

## Consequences
- The graph is exported from any instance by reading `Graph/Link`; `linkages.graphml` becomes a view, not a separate source.
- New link types (statistical links in Phase 4, prior-wave wording) arrive as enumeration values in a minor version.
- `in_group` links duplicate the current assignment set (ADR-003). They are kept so the graph is complete on its own; the cross-check confirms they agree.

## Implementation notes (P3.S02–S05)

Added after the XSD was built and validated against real data. Each note records where the implementation refines the decision above; the decision itself is unchanged.

- **Item role** uses the three values in the data: `asked`, `derived`, `attention_check`. Text items are identified by their type (`open_text`, `open_text_specify`), not by role.
- **Approved inferences.** All 27 `INFERRED` links were approved by Scott in P1.S10; they carry `reviewed="confirmedByScott"`.
