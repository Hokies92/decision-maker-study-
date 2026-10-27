# Project State

## Current
**Phase:** 0 — Ingest source materials   **Gate:** open
**Step:** P0.S01 — Restructure STATE.md and propose the Phase 0 step plan
**Status:** in progress (awaiting Scott's merge = plan approval)
**Branch:** phase-0/step-01-plan
**Updated:** 2026-10-27 by Claude session

## Step plan — Phase 0

| ID | Objective | Inputs | Outputs | Done-when | Status | Commit |
|----|-----------|--------|---------|-----------|--------|--------|
| P0.S01 | Restructure STATE.md to GOVERNANCE Appendix A; propose Phase 0 steps | `STATE.md`, `GOVERNANCE.md` | `STATE.md` | Matches Appendix A; prior log entries preserved; Scott merges PR | in progress | — |
| P0.S02 | Build intake tooling: source register template + manifest script | `GOVERNANCE.md` §5 P0, §9 | `00_source/SOURCE_REGISTER.md` (empty template), `scripts/p0_build_manifest.sh` | Script runs on empty tree without error; register has all required columns | not started | — |
| P0.S03 | Ingest survey instrument | Files from Scott (questionnaire, screener, skip logic/programming spec) | `00_source/instrument/*`, register rows | Filenames preserved as received; one register row per file; files unmodified | not started (needs files) | — |
| P0.S04 | Ingest response data + respondent-identity scan | Data export(s) from Scott | `00_source/data/*`, register rows, `scripts/p0_scan_identifiers.py`, scan output | Register rows complete; scan run by committed script; any identifying fields → stop (S8), no clear-text commit | not started (needs files) | — |
| P0.S05 | Ingest published report / deck | Report or deck from Scott, if available | `00_source/report/*`, register rows | As S03; or register records "not available" | not started (needs files) | — |
| P0.S06 | Generate and verify integrity manifest | All `00_source/` files | `00_source/MANIFEST.sha256` | `sha256sum -c` passes; every file in `00_source/` listed | not started | — |
| P0.S07 | Draft Phase 0 gate review | All P0 outputs | Gate review block in `STATE.md` | Every §5 P0 criterion checked with evidence; stop for Scott's confirmation and tag | not started | — |

## Source intake checklist
- [ ] Survey instrument (questionnaire / screener, ideally with skip logic)
- [ ] Response data (CSV / XLSX / SPSS export, or tabulated banners)
- [ ] Published report or deck (if available)

## Gate reviews
<!-- one dated block per closed phase, with criteria checklist and tag -->
- (none yet)

## Decisions log
<!-- append-only, dated; supersede, never edit -->
- 2026-10-24: Repo scaffolded. Phase gating adopted. Study date excluded from analysis.
- 2026-10-27: GOVERNANCE.md v1.0.0, CLAUDE.md, PROJECT_INSTRUCTIONS.md merged to `main` (PR #1, merge `10d5ebc`).
- 2026-10-27: Repository stays public (Scott). Rule D3 still applies: no respondent-identifying data committed in clear text.
- 2026-10-27: Step ID `P0.S00` was used for the governance commit, so the Phase 0 plan lives in `P0.S01` on `phase-0/step-01-plan` rather than a `step-00-plan` branch (GOVERNANCE §4.2).

## Open questions
<!-- includes all INFERRED items awaiting review -->
- Q1 (P0.S04): Large or binary source files (`.sav`, `.xlsx`, `.pdf`, >10 MB) require Git LFS per D2, which Scott configures. Configure LFS before ingest, or commit these files directly if they are small?
- Q2 (P0.S04): If the response data contains respondent-identifying fields, preferred handling: (a) keep the raw file out of the repo and commit a de-identified copy produced by a committed script, or (b) decide case by case at the stop?

## Parking lot
<!-- out-of-scope ideas, one line each, with the step they were noticed in -->
- (P0.S01) GOVERNANCE §4.2 assumes the plan is step `00`; consider amending to allow the plan to be `S01` when `S00` is already used. Proposal only — `gov/` branch on request.
- (P0.S01) GOVERNANCE B4 wording bans `git reset --hard` on any pushed branch, which also catches a harmless local fast-forward to `origin/main`. Consider narrowing to "any reset that discards commits or uncommitted work." Proposal only.

## Governance incidents
<!-- append-only -->
- 2026-10-27 (P0.S01 session open): Claude ran `git reset --hard origin/main` on a local `main` that had no local commits or changes, to sync it after PR #1 merged. The effect was a fast-forward; nothing was discarded and nothing was pushed. It still breaks the letter of rule B4. Disclosed to Scott; no correction needed. Future syncs will use `git merge --ff-only origin/main`.
