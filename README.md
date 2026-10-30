# Decision Maker Study — Reconstruction & Re-architecture

## Objective
Reverse-engineer a Forrester decision-maker survey, inventory its data, and rebuild it on a richer XML schema in which every result is tied to **role level** and **stakeholder type**, and every question is a **thread** that can be linked to others, enabling graph/network and topology analysis for both reductionist decomposition and synthetic recombination. Study date is deliberately ignored.

**Data reality (2026-10-27):** the source contains group-level tables (N=319, broken out by level × stakeholder and other groups) and respondent-level open-ended text with no per-respondent level or stakeholder value. Results are therefore linked to level and stakeholder through the **breakout group**, not the individual. Respondent-level slots are reserved in the schema for future data.

## Phases (gated — each must be complete before the next starts)
| # | Phase | Output | Folder |
|---|-------|--------|--------|
| 0 | Ingest source materials | Raw instrument, data, report | `00_source/` |
| 1 | Reconstruct the instrument | Question map (one thread per question), skip logic, response scales, sampling frame, linkage inventory | `01_instrument_reconstruction/` |
| 2 | Inventory the data | Variable dictionary; collected vs. derivable vs. missing; group coverage | `02_data_inventory/` |
| 3 | Design the new schema | XSD storing results as cells (question × option × breakout group), level and stakeholder on the group, thread links as first-class edges, respondent-level slots reserved; sample instances | `03_schema/` |
| 4 | Analytics library | Techniques valid on group percentages, incl. thread networks and topology maps; each tied to schema fields | `04_analytics_library/` |
| 5 | Open-ended responses | Coding frame per respondent, linked to question threads (not to level/stakeholder — not in source) | `05_open_ended/` |
| 6 | Visualization | Views that let users see and work through the asymmetry — value vs experience, gate × cohort, the customers' own words — each built by script from committed data | `06_visualization/` |

Structured data is handled first (phases 1–4); open-ended data follows (phase 5); visualization last (phase 6).

## Session continuity
`STATE.md` is the single source of truth for where work stands. Every session reads it first and updates it last.
