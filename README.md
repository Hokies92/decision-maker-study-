# Decision Maker Study — Reconstruction & Re-architecture

## Objective
Reverse-engineer a Forrester decision-maker survey, inventory its data, and rebuild it on a richer XML schema that links every response to **role level** and **stakeholder type**, enabling graph/network and multivariate analysis. Study date is deliberately ignored.

## Phases (gated — each must be complete before the next starts)
| # | Phase | Output | Folder |
|---|-------|--------|--------|
| 0 | Ingest source materials | Raw instrument, data, report | `00_source/` |
| 1 | Reconstruct the instrument | Question map, skip logic, response scales, sampling frame | `01_instrument_reconstruction/` |
| 2 | Inventory the data | Variable dictionary; collected vs. derivable vs. missing | `02_data_inventory/` |
| 3 | Design the new schema | XSD + sample instance documents | `03_schema/` |
| 4 | Analytics library | Catalog of techniques, each tied to schema fields | `04_analytics_library/` |
| 5 | Open-ended responses | Coding frame, linked back to level/stakeholder | `05_open_ended/` |

Structured data is handled first (phases 1–4); open-ended data follows (phase 5).

## Session continuity
`STATE.md` is the single source of truth for where work stands. Every session reads it first and updates it last.
