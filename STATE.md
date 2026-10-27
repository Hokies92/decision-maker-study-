# Project State

## Current
**Phase:** 0 — Ingest source materials   **Gate:** open
**Step:** P0.S05 — Record published report as `MISSING`
**Status:** done (awaiting Scott's merge)
**Branch:** phase-0/step-05-report-missing
**Updated:** 2026-10-27 by Claude session

## Step plan — Phase 0

| ID | Objective | Inputs | Outputs | Done-when | Status | Commit |
|----|-----------|--------|---------|-----------|--------|--------|
| P0.S01 | Restructure STATE.md to GOVERNANCE Appendix A; propose Phase 0 steps | `STATE.md`, `GOVERNANCE.md` | `STATE.md` | Matches Appendix A; prior log entries preserved; Scott merges PR | done | `0505d45` (PR #2) |
| P0.S02 | Build intake tooling: source register template + manifest script | `GOVERNANCE.md` §5 P0, §9 | `00_source/SOURCE_REGISTER.md` (empty template), `scripts/p0_build_manifest.sh` | Script runs on empty tree without error; register has all required columns | done | `60a619b` (PR #3) |
| P0.S03 | Record survey instrument as `MISSING` | Scott's confirmation (2026-10-27) | Register row for instrument; `00_source/instrument/README.md` stating it is unavailable | Register states no questionnaire, screener, or programming spec exists; Phase 1 reconstruction basis documented as data-only | done | `2f3e201` (PR #4) |
| P0.S04 | Ingest response data + respondent-identity scan | Two Excel files from Scott: structured responses; open-ended responses | `00_source/data/*`, register rows, `scripts/p0_scan_identifiers.py`, scan output | Register rows complete; scan run by committed script **before** the data files are committed; any identifying fields → stop (S8), Scott decides case by case | done | `22b00d3`, renamed `d412158` (PR #5) |
| P0.S05 | Record published report as `MISSING` | Scott's confirmation (2026-10-27) | Register row for report; `00_source/report/README.md` stating it is unavailable | Register states no report or deck exists | done | `6305dc0` |
| P0.S06 | Generate and verify integrity manifest | All `00_source/` files | `00_source/MANIFEST.sha256` | `sha256sum -c` passes; every file in `00_source/` listed | not started | — |
| P0.S07 | Draft Phase 0 gate review | All P0 outputs | Gate review block in `STATE.md` | Every §5 P0 criterion checked with evidence; stop for Scott's confirmation and tag | not started | — |

## Source intake checklist
- [x] Survey instrument — does not exist; to be reconstructed in Phase 1 (`MISSING`)
- [x] Response data — two Excel files ingested as SRC-002 (structured, tabulated) and SRC-003 (open-ended)
- [x] Published report or deck — does not exist (`MISSING`)

## Gate reviews
<!-- one dated block per closed phase, with criteria checklist and tag -->
- (none yet)

## Decisions log
<!-- append-only, dated; supersede, never edit -->
- 2026-10-24: Repo scaffolded. Phase gating adopted. Study date excluded from analysis.
- 2026-10-27: GOVERNANCE.md v1.0.0, CLAUDE.md, PROJECT_INSTRUCTIONS.md merged to `main` (PR #1, merge `10d5ebc`).
- 2026-10-27: Repository stays public (Scott). Rule D3 still applies: no respondent-identifying data committed in clear text.
- 2026-10-27: Q1 resolved (Scott): source is two small Excel files — structured responses and open-ended responses. No Git LFS; commit directly.
- 2026-10-27: Q2 resolved (Scott): option (b). If respondent-identifying fields are found, Claude stops (S8) and Scott decides case by case. The identity scan runs before any data file is committed.
- 2026-10-27: Q3 resolved (Scott): no questionnaire, screener, methodology document, or report exists. The instrument and methodology are reconstructed in Phase 1 from the two data files only; every item will carry `RECON_DATA` or `INFERRED`, with no `VERBATIM` or `RECON_REPORT` sources available.
- 2026-10-27: Phase 0 step plan approved (PR #2, merge `0505d45`).
- 2026-10-27: Manifest scope is evidence files only. `*.md` (register, unavailability notes), `.gitkeep`, and the manifest itself are excluded, so appending register rows never breaks integrity checks. A recorded file whose hash changes fails both build and check; the script never rewrites an entry.
- 2026-10-27: Source data is final (Scott): the two Excel files are the only data that exist. No respondent-level structured export is available. Verified at intake: the structured file is a tabulated report (N=319, column percentages with significance tests, broken out by ITDM/BDM and seniority); the open-ended file and the "Other" sheet are respondent-level (respid) but carry no role-level or stakeholder-type value per respondent. Consequence: individual answers cannot be linked to level or stakeholder type; level × stakeholder analysis is limited to the breakouts in the tables. Scope of Phases 3–5 to be re-planned at the Phase 1 plan.
- 2026-10-27: Identity-scan findings decided (Scott): commit both data files as received — "the raw data is the raw data"; a cleaned public-facing version can be built later. Covers staff names in file metadata/comments/header, vendor names and one possible vendor-employee surname in free text. No respondent is identified.
- 2026-10-27: Upload-system prefixes (`1be1a22d-`, `cd05d1e9-`) dropped; files stored under the names Scott created, prefixes recorded in the register.
- 2026-10-27: Supersedes the entry above. Scott renamed the data files: `survey.xlsx` (structured) and `open_ended.xlsx`. Explicit override of the GOVERNANCE §5 P0 criterion "filename preserved as received"; the received names are kept in the register, and contents are unchanged.
- 2026-10-27: Scan rule refined after real-data false positives: cells that are a decimal or an integer under 10 digits are excluded from value-pattern checks.
- 2026-10-27: Step ID `P0.S00` was used for the governance commit, so the Phase 0 plan lives in `P0.S01` on `phase-0/step-01-plan` rather than a `step-00-plan` branch (GOVERNANCE §4.2).

## Open questions
<!-- includes all INFERRED items awaiting review -->
- (none open)

## Parking lot
<!-- out-of-scope ideas, one line each, with the step they were noticed in -->
- (P0.S01) GOVERNANCE §4.2 assumes the plan is step `00`; consider amending to allow the plan to be `S01` when `S00` is already used. Proposal only — `gov/` branch on request.
- (P0.S01) GOVERNANCE B4 wording bans `git reset --hard` on any pushed branch, which also catches a harmless local fast-forward to `origin/main`. Consider narrowing to "any reset that discards commits or uncommitted work." Proposal only.

- (P0.S01) With no instrument on file, Scott's own recollection as the study's designer is the only non-data source. Consider a provenance tag `RECALL_DESIGNER` so facts Scott supplies are distinguished from Claude's `INFERRED` items. Proposal only — `gov/` branch on request.

- (P0.S04) Re-plan Phases 3–5 for table-level data: schema to hold group-level results (cell = question × answer × breakout group), with respondent-level elements reserved but empty; Phase 4 limited to techniques valid on aggregates; Phase 5 coding unlinked to level/stakeholder. Requires a README phase-table change (protected) — proposal at the Phase 1 plan.

- (P0.S04) Public-facing derived version of the data (de-identified, cleaned) — Scott's idea for later; not part of the current phase plan.

## Governance incidents
<!-- append-only -->
- 2026-10-27 (P0.S01 session open): Claude ran `git reset --hard origin/main` on a local `main` that had no local commits or changes, to sync it after PR #1 merged. The effect was a fast-forward; nothing was discarded and nothing was pushed. It still breaks the letter of rule B4. Disclosed to Scott; no correction needed. Future syncs will use `git merge --ff-only origin/main`.
