---
id: T01
title: Gate profile
gates: TARGET; baseline; ACCESS; AGREE; VISION; CASE
question: What is this cohort's experience at this gate — every answer, for every cohort, arranged by Scott's gates?
required_xpaths:
  - /d:Study/d:Results/d:ItemResults/d:Result/@share
  - /d:Study/d:Results/d:ItemResults/d:Result/@base
  - /d:Study/d:Results/d:ItemResults/@item
  - /d:Study/d:Grouping/d:AssignmentSet[@status='current']/d:Assignment/@group
  - /d:Study/d:Grouping/d:Group/@gate
  - /d:Study/d:Population/d:Cohorts/d:Cohort/@n
minimum_n: 25
validity: group-level
ecological_caveat: no
output_form: table — outputs/T01/gate_profile.csv (every result with gate, cohort, usable flag); gate_summary.csv and summary.md (one reading per question, All respondents)
script: scripts/p4_t01_gate_profile.py
outputs:
  - 04_analytics_library/outputs/T01/gate_profile.csv
  - 04_analytics_library/outputs/T01/gate_summary.csv
  - 04_analytics_library/outputs/T01/summary.md
provenance: INFERRED
---

# T01 — Gate profile

## Question
Purpose of record (Scott, 2026-10-29): every answer stored as "this cohort's experience at this gate." T01 is that view made readable: every result, ordered by gate, then question, then cohort.

## Inputs
Results (share, base) per item × option × cohort; the current assignment set (thread → group → gate); cohort sizes.

## Method
1. Read every Result; attach its thread, its gate through the current assignment set, its cohort's dimension and n.
2. Mark `usable` = cohort n ≥ 25 and item base ≥ 25.
3. Sort by gate order (Target input, Baseline, Access, Agree, Vision, Case), thread, item, cohort, option.
4. For All respondents, give one reading per question: the headline summary measure where one is defined (T02), else the share selecting the item, else the most chosen option.

## Assumptions
Shares are column percentages of each cohort's base, as tabulated (P2.S04: every single-choice table sums to 1). The gate of a result is the gate of its question's group in the current assignment set; regrouping changes the gate without changing any result.

## Minimum n
Every row carries `usable`. T01 compares nothing, so it keeps all rows; any comparison built on it must filter to `usable`.

## Validity
Group-level percentages only.

## Output
`gate_profile.csv` — columns: item, thread, gate, group, cohort, dimension, option, option_label, share, base, n, below_min, usable, status, cite. One row per distinct result (22,968). Keyed by gate, cohort and item for visualization. `gate_summary.csv` / `summary.md` — one reading per question for All respondents.

## Results on this study
See `outputs/T01/summary.md`.
