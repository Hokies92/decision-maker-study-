# Survey instrument — unavailable

**Status:** `MISSING` (register row `SRC-001`)
**Confirmed by:** Scott Santucci, 2026-10-27

## Fact

No questionnaire, screener, programming specification, skip-logic document, or methodology document exists for this study. This folder will hold no evidence files.

## Consequence for Phase 1

The instrument and methodology are reconstructed from the response data alone (`00_source/data/`). Therefore:

- No item can carry the `VERBATIM` or `RECON_REPORT` provenance tags.
- Every reconstructed item carries `RECON_DATA` (evidenced by the data) or `INFERRED` (reasoned, not evidenced).
- Every `INFERRED` item is listed in `STATE.md` → *Open questions* until Scott confirms or rejects it.

## What the data can and cannot establish

| Recoverable from data | Partly recoverable | Not recoverable |
|---|---|---|
| Question list (column headers) | Exact wording, if headers are coded or truncated | Question order, if the export reordered columns |
| Response options and scale lengths (observed values) | Scale labels, if values are numeric | Quota targets |
| Question types (single, multi, grid, open) | Screener rules (inferred from who is in the sample) | Fielding mode and dates |
| Routing (structured blank patterns) | | Screened-out respondents |
| Sample composition by role level and stakeholder type, if captured as columns | | |

If an instrument or report is found later, it is ingested as a new register row and Phase 1 items are re-tagged against it; this note is then superseded, not deleted.
