# CLAUDE.md — Decision Maker Study

You are working in a gated, stepwise reconstruction project. **`GOVERNANCE.md` is binding and outranks this file.** Read it in full at the start of every session.

## What this project is

- **Fact:** A decision-maker survey (structured + open-ended questions) was originally designed by Scott Santucci at Forrester.
- **Goal:** Reverse-engineer the instrument, inventory its data, and rebuild it on an XML schema in which every result is tied to **role level** and **stakeholder type** through its breakout group, and every question is a **thread** linkable to others for network and topology analysis.
- **Data reality:** group-level tables plus respondent-level open-ended text; no per-respondent level or stakeholder. Never infer one.
- **Exclusion:** The study date is deliberately ignored. Do not analyze, weight, or comment on recency.
- **Order:** Structured data first (Phases 1–4); open-ended data next (Phase 5); visualization last (Phase 6).

## Session start — do these in order, every time

1. `git fetch && git status && git log --oneline -10`
2. Read `GOVERNANCE.md`, then this file, then `STATE.md`.
3. Confirm the tree is clean and `STATE.md` agrees with `git log`. If either fails → stop (GOVERNANCE §8, S5).
4. Post the orientation block (GOVERNANCE §6.1) and wait for Scott's go-ahead if the step is new.

## While working

- Work only on the **current step** in `STATE.md`. Before every write, run the scope lock (GOVERNANCE §4.3).
- One step → one branch `phase-<N>/step-<NN>-<slug>` → one PR — or an approved batch of consecutive no-input steps on `phase-<N>/steps-<NN>-<MM>-<slug>` (GOVERNANCE §3.4). Never commit to `main`.
- Tag every reconstructed fact: `VERBATIM` · `RECON_DATA` · `RECON_REPORT` · `RECALL_DESIGNER` · `INFERRED` · `MISSING`. Never fill a gap silently.
- Anything out of scope → `STATE.md` *Parking lot*. Do not act on it.
- Artifacts derived from data are produced by committed scripts. Never hand-edit generated output.
- `00_source/` is evidence. Read it; never change it.

## Session end

Run the verification checklist (GOVERNANCE §6.3), update `STATE.md`, commit, push or deliver a patch, post the step report (GOVERNANCE §11), and **stop**.

## Repository map

| Path | Phase | Contents |
|------|-------|----------|
| `00_source/instrument/` | 0 | Questionnaire, screener, programming spec |
| `00_source/data/` | 0 | Response data exports |
| `00_source/report/` | 0 | Published report / deck |
| `00_source/SOURCE_REGISTER.md`, `MANIFEST.sha256` | 0 | Register and integrity record |
| `01_instrument_reconstruction/` | 1 | Question map, skip logic, scales, sampling frame |
| `02_data_inventory/` | 2 | Variable dictionary, quality report, coverage matrix |
| `03_schema/` | 3 | XSD, `examples/`, mapping, `decisions/` ADRs |
| `04_analytics_library/` | 4 | One file per technique + `catalog.md` |
| `05_open_ended/` | 5 | Coding frame, coded output |
| `06_visualization/` | 6 | Concept sheet, view build scripts' outputs, `catalog.md` |
| `scripts/` | any | Generators and checks (name: `p<N>_<verb>_<object>.py`) |

## Standard commands

```bash
# Source integrity (run before every step close)
sha256sum -c 00_source/MANIFEST.sha256

# Scope check: files changed on this branch
git diff --stat main...HEAD

# Schema validation (Phase 3+)
xmllint --noout --schema 03_schema/decision-maker-study.xsd 03_schema/examples/*.xml
```

Python: use the standard library plus `pandas`, `lxml`, `pyreadstat` (for SPSS). Install with `pip install --break-system-packages` if missing. Record any new dependency in `requirements.txt` in the same commit.

## Core concepts (do not redefine without a logged decision)

- **Role level** — the respondent's seniority tier as defined by the source instrument. Phase 1 records the source definition verbatim; Phase 3 makes it a referenced entity.
- **Stakeholder type** — the respondent's functional role in the decision as defined by the source instrument. Same treatment as role level.
- **Breakout group** — a subset of respondents a table reports on (e.g., ITDM × VP). Carries role level and/or stakeholder type. The unit that ties structured results to level and stakeholder.
- **Thread** — one base question (e.g., Q12) with its sub-items, options, and results; the node in the linkage graph.
- **Respondent** — identified by `respid`; present only in open-ended and "Other" text. Has no level or stakeholder value in source.
- **Collected / derivable / missing** — Phase 2 status of every variable. *Derivable* requires an explicit rule.

## Vocabulary for project-authored text

- Write "customers," not "buyers." Write "salespeople," not "sellers."
- Do not describe Growth Enablement as "go-to-market" or a "consultancy."
- Exception: inside `VERBATIM` content, preserve source wording exactly, whatever terms it uses.

## Communication with Scott

- Lead with the fact or result, then the reasoning, then context.
- State what is valid, what is invalid, and what is unknown — separately.
- Completion claims cite file paths and commit SHAs.
- When blocked, name the stop condition (S1–S8), show the evidence, offer 1–3 options.
