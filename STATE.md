# Project State

## Current
**Phase:** 1 — Reconstruct the instrument   **Gate:** open
**Step:** P1.S01 — Build the table parser
**Status:** done (awaiting Scott's merge)
**Branch:** phase-1/step-01-table-parser
**Updated:** 2026-10-27 by Claude session

## Step plan — Phase 1

Outputs go to `01_instrument_reconstruction/`. Every item carries a provenance tag. Every derived file is produced by a committed script in `scripts/`.

| ID | Objective | Inputs | Outputs | Done-when | Status | Commit |
|----|-----------|--------|---------|-----------|--------|--------|
| P1.S00 | Propose the Phase 1 step plan | Phase 0 outputs; read-only structure survey of SRC-002/003 | `STATE.md` | Plan merged by Scott; D1–D2 answered | done | `2e58562` (PR #9); gov `b788b0e` (PR #10) |
| P1.S01 | Build the table parser: locate every question block in SRC-002 (stem, answer options, banner columns, row/column positions) | `00_source/data/survey.xlsx` | `scripts/p1_parse_tables.py`; `01_instrument_reconstruction/derived/table_blocks.csv` | All 116 tabulated items found on the 4 breakout sheets; 104 on Main Page; parser output reproducible; no values altered | done — 578 blocks (see decisions log for count reconciliation) | `77a75f6` |
| P1.S02 | Question map: every item S1–S12, Q1–Q25 with ID, **thread ID** (one thread per base question), construct, wording, type, options link, provenance | `table_blocks.csv`; SRC-002 "Other" sheet; SRC-003 | `question_map.csv` + `question_map.md`; `scripts/p1_build_question_map.py` | All 37 base questions and every sub-item listed; wording tagged `VERBATIM` with file/sheet/cell, or `INFERRED` with rationale; piping placeholders (e.g., `hS5Piping`) recorded, not "fixed" | not started | — |
| P1.S03 | Response scales: every answer list with ID, points, labels, direction | `table_blocks.csv` | `response_scales.csv`; script | Every question maps to one scale ID; shared scales deduplicated; labels `VERBATIM` | not started | — |
| P1.S04 | Routing and bases: who was asked what, reconstructed from screener structure and table bases | `table_blocks.csv`; `question_map.csv` | `skip_logic.md` (explicit `IF … THEN ASK`) | Every routed item has a rule tagged `RECON_DATA` (base evidence) or `INFERRED`; unresolvable routing marked `MISSING` | not started | — |
| P1.S05 | Sampling frame and core definitions: screener criteria, role-level and stakeholder-type definitions, breakout groups and their sizes | Screener items S1–S12; banner headers on all sheets | `sampling_frame.md` | Role level (C-level / VP / Director / Manager) and stakeholder type (ITDM / BDM; decision-stage roles) defined `VERBATIM` from source; group sizes cited | not started | — |
| P1.S06 | Gaps and anomalies: Main Page missing Q11_2–7 and Q15_1–7; `Sheet1` fragment; S1 untabulated; open-ended 359 rows vs 319 respids | All P1 outputs | `anomalies.md` | Each anomaly described with evidence and disposition; none silently resolved | not started | — |
| P1.S07 | **Linkage inventory:** every link between question threads that the instrument defines, as an edge list | All P1 outputs; SRC-002 banners; SRC-002 "Other" sheet; SRC-003 | `linkages.csv` (source thread, target thread, link type, evidence, provenance); `linkages.md` (type definitions + summary graph); `scripts/p1_build_linkages.py` | Link types covered: shared response scale; same construct/stem family; routing dependency; piping; screener item used as a breakout (S-thread → every Q-thread it cuts); "Other" free text → parent item; open-ended ↔ structured topical link; respondent-key link (respid shared by SRC-003 and the "Other" sheet). Each edge cites evidence; topical links tagged `INFERRED` until Scott reviews | not started | — |
| P1.S08 | Cross-check and provenance count | All P1 outputs | `scripts/p1_crosscheck.py`; `crosscheck_report.md` | Every table block and data column maps to ≥1 question; every question maps to data or is flagged `NO_DATA`; provenance counts reported | not started | — |
| P1.S09 | Designer review: Scott confirms or rejects every `INFERRED` item and supplies `RECALL_DESIGNER` facts on intent | Open questions list | Updated outputs; decisions log | No `INFERRED` item left unreviewed | not started | — |
| P1.S10 | Draft Phase 1 gate review | All P1 outputs | Gate review block | Every §5 P1 criterion checked with evidence; stop for Scott's merge and tag | not started | — |

## Step plan — Phase 0 (closed — tag `phase-0-complete` on `1c066db`)

| ID | Objective | Inputs | Outputs | Done-when | Status | Commit |
|----|-----------|--------|---------|-----------|--------|--------|
| P0.S01 | Restructure STATE.md to GOVERNANCE Appendix A; propose Phase 0 steps | `STATE.md`, `GOVERNANCE.md` | `STATE.md` | Matches Appendix A; prior log entries preserved; Scott merges PR | done | `0505d45` (PR #2) |
| P0.S02 | Build intake tooling: source register template + manifest script | `GOVERNANCE.md` §5 P0, §9 | `00_source/SOURCE_REGISTER.md` (empty template), `scripts/p0_build_manifest.sh` | Script runs on empty tree without error; register has all required columns | done | `60a619b` (PR #3) |
| P0.S03 | Record survey instrument as `MISSING` | Scott's confirmation (2026-10-27) | Register row for instrument; `00_source/instrument/README.md` stating it is unavailable | Register states no questionnaire, screener, or programming spec exists; Phase 1 reconstruction basis documented as data-only | done | `2f3e201` (PR #4) |
| P0.S04 | Ingest response data + respondent-identity scan | Two Excel files from Scott: structured responses; open-ended responses | `00_source/data/*`, register rows, `scripts/p0_scan_identifiers.py`, scan output | Register rows complete; scan run by committed script **before** the data files are committed; any identifying fields → stop (S8), Scott decides case by case | done | `22b00d3`, renamed `d412158` (PR #5) |
| P0.S05 | Record published report as `MISSING` | Scott's confirmation (2026-10-27) | Register row for report; `00_source/report/README.md` stating it is unavailable | Register states no report or deck exists | done | `6305dc0` (PR #6) |
| P0.S06 | Generate and verify integrity manifest | All `00_source/` files | `00_source/MANIFEST.sha256` | `sha256sum -c` passes; every file in `00_source/` listed | done | `bec88eb` (PR #7) |
| P0.S07 | Draft Phase 0 gate review | All P0 outputs | Gate review block in `STATE.md` | Every §5 P0 criterion checked with evidence; stop for Scott's confirmation and tag | done | `1f25e02` (PR #8) |

## Source intake checklist
- [x] Survey instrument — does not exist; to be reconstructed in Phase 1 (`MISSING`)
- [x] Response data — two Excel files ingested as SRC-002 (structured, tabulated) and SRC-003 (open-ended)
- [x] Published report or deck — does not exist (`MISSING`)

## Gate reviews
<!-- one dated block per closed phase, with criteria checklist and tag -->

### Phase 0 — Ingest source materials
**Drafted:** 2026-10-27 by Claude (P0.S07) · **Reviewed against:** `main` @ `9aa51d1`
**Recommendation:** PASS — close Phase 0 · **Decision:** APPROVED by Scott (PR #8 merged 2026-10-27) · **Tag:** `phase-0-complete` on `1c066db` (created by Scott)

| # | Exit criterion (GOVERNANCE §5) | Result | Evidence |
|---|---|---|---|
| 1 | Every source file present in `00_source/{instrument,data,report}/`, filename preserved as received | PASS, with override | `data/survey.xlsx`, `data/open_ended.xlsx` present; `instrument/` and `report/` hold unavailability notes (no files exist). Filenames changed by Scott's explicit override; received names kept in register (`d412158`). |
| 2 | `SOURCE_REGISTER.md` lists each file with all fields | PASS | 4 rows, SRC-001…SRC-004, all 12 fields populated (`2f3e201`, `22b00d3`, `d412158`, `6305dc0`) |
| 3 | `MANIFEST.sha256` generated and committed | PASS | `bec88eb`; `sha256sum -c` 2/2 OK; script `--check` PASS; covers every evidence file; tamper test caught |
| 4 | No respondent-identifying fields committed in clear text | PASS | Scan run before commit (`IDENTITY_SCAN.md`): 0 HIGH, 30 REVIEW. No respondent named; IDs anonymous. Staff names in metadata and vendor names in free text committed by Scott's decision. |
| 5 | Scott confirms the source set is complete | PASS | Scott, 2026-10-27: the two Excel files are the only data; no instrument, methodology, or report exists (decisions log). |

**Carried into Phase 1 (not blockers):**
- No respondent-level structured data: individual answers cannot be linked to role level or stakeholder type. Phases 3–5 need re-planning; README phase table is protected, so this comes to Scott as a proposal with the Phase 1 plan.
- Instrument must be reconstructed from data only: all items `RECON_DATA` or `INFERRED`; Scott's recollection is the only other source (`RECALL_DESIGNER` tag proposal in parking lot).
- `open_ended.xlsx`: 359 rows vs 319 respids; one possible vendor-employee surname in Q24.
- Governance wording fixes parked (§4.2 step numbering, B4 reset wording).

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
- 2026-10-27: Phase 0 closed. Gate review merged (PR #8, `1c066db`); Scott created tag `phase-0-complete`.
- 2026-10-27: Correction (supersedes the `00_source/instrument/README.md` statement that no item can be `VERBATIM`): SRC-002 table labels carry full question wording in quotes, so wording copied from the data file is `VERBATIM`, cited by file, sheet, and cell. Only wording with no source text is `INFERRED`. The README is protected; this entry is the correction of record.
- 2026-10-27: Structure survey (read-only, P1.S00): SRC-002 tabulates 31 base questions (S2–S12, Q1–Q20), 116 items. Main Page breaks every item out by seniority (C-level / VP / Director / Manager) within ITDM, within BDM, and combined, plus country and region. Other sheets break out by industry, company size, revenue, sales-contact frequency, customer type, and decision-stage role. Level × stakeholder therefore exists at group level for every structured item.
- 2026-10-27: D1 approved (Scott): re-scope Phases 3–5 to group-level data with level × stakeholder on the breakout group; respondent-level slots reserved. README change to follow on a `gov/` branch.
- 2026-10-27: D1 extension (Scott): find more linkages. Each question becomes its own **thread**; links between threads form a graph that can be iterated into network and topology maps, serving both reductionist analysis (decompose by thread, scale, group) and synthetic holism (recombine threads into structures). Added P1.S07 linkage inventory (structural links defined by the instrument). Statistical links between threads belong to Phase 4.
- 2026-10-27: D2 approved (Scott): add provenance tag `RECALL_DESIGNER`. Scope per Scott: he designed the survey's business logic; a contractor executed it. The tag therefore covers design intent and business logic; implementation details (programming, routing as fielded) may differ, so where recall and data conflict, the data is recorded as fielded and the conflict is logged. GOVERNANCE §7 change to follow on a `gov/` branch.
- 2026-10-27: P1.S01 count reconciliation. The plan's targets (116 items per breakout sheet, 104 on Main Page) came from a header scan that started one row late and only matched S/Q-prefixed headers. The parser finds 118 and 106: the extra two on every sheet are S1 (department; it **is** tabulated — correcting the P1.S00 note that S1 was untabulated) and the "ITDM or BDM" summary table (no source ID). Independent check: every labeled row on all five sheets is covered, 0 stray.
- 2026-10-27: Layout differences found by the parser, for P1.S06: Main Page shows Q11 as one condensed table headed "Q11_1" with 7 statements and no base row, where breakout sheets show Q11_1–Q11_7 separately; Main Page shows Q15 as one 7-option table plus Q15_8, where breakout sheets show Q15_1–Q15_7. "S2 and S3 combined" is a merged table, given ID `S2_S3_combined`.
- 2026-10-27: Step ID `P0.S00` was used for the governance commit, so the Phase 0 plan lives in `P0.S01` on `phase-0/step-01-plan` rather than a `step-00-plan` branch (GOVERNANCE §4.2).

## Open questions
<!-- includes all INFERRED items awaiting review -->
- (resolved — see decisions log) D1 (P1.S00): Re-plan of Phases 3–5. Given group-level data with level × stakeholder breakouts, proposed README phase-table change: Phase 3 schema stores results as cells (question × option × breakout group), with level and stakeholder as referenced entities on the group, and respondent-level elements reserved but empty; Phase 4 limited to techniques valid on group percentages; Phase 5 coding by respondent but not linked to level/stakeholder. README is protected — needs Scott's approval; Claude would then make the change on a `gov/` branch.
- (resolved — see decisions log) D2 (P1.S00): Adopt provenance tag `RECALL_DESIGNER` for facts Scott supplies from memory as the study's designer (distinct from Claude's `INFERRED`)? Amends GOVERNANCE §7 — needs Scott's approval; `gov/` branch.

## Parking lot
<!-- out-of-scope ideas, one line each, with the step they were noticed in -->
- (P0.S01) GOVERNANCE §4.2 assumes the plan is step `00`; consider amending to allow the plan to be `S01` when `S00` is already used. Proposal only — `gov/` branch on request.
- (P0.S01) GOVERNANCE B4 wording bans `git reset --hard` on any pushed branch, which also catches a harmless local fast-forward to `origin/main`. Consider narrowing to "any reset that discards commits or uncommitted work." Proposal only.

- (P0.S01) With no instrument on file, Scott's own recollection as the study's designer is the only non-data source. Consider a provenance tag `RECALL_DESIGNER` so facts Scott supplies are distinguished from Claude's `INFERRED` items. Proposal only — `gov/` branch on request.

- (P0.S04) Re-plan Phases 3–5 for table-level data: schema to hold group-level results (cell = question × answer × breakout group), with respondent-level elements reserved but empty; Phase 4 limited to techniques valid on aggregates; Phase 5 coding unlinked to level/stakeholder. Requires a README phase-table change (protected) — proposal at the Phase 1 plan.

- (P0.S04) Public-facing derived version of the data (de-identified, cleaned) — Scott's idea for later; not part of the current phase plan.

- (P1.S00) Phase 4 statistical linkages between threads: correlation of group profiles across the ~40 breakout groups, similarity clustering, network/topology maps. Caveat to carry: links computed on group percentages are ecological — they describe groups, not individuals.

## Governance incidents
<!-- append-only -->
- 2026-10-27 (P0.S01 session open): Claude ran `git reset --hard origin/main` on a local `main` that had no local commits or changes, to sync it after PR #1 merged. The effect was a fast-forward; nothing was discarded and nothing was pushed. It still breaks the letter of rule B4. Disclosed to Scott; no correction needed. Future syncs will use `git merge --ff-only origin/main`.
