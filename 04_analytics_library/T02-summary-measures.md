---
id: T02
title: Summary measures
gates: ACCESS; AGREE; VISION; CASE
question: For each rating question, what share of each cohort gives the answer that matters (Frequently; Agree; Important; a differentiator; built the case ourselves)?
required_xpaths:
  - /d:Study/d:Variables/d:Variable[@kind='summary']/d:Rule
  - /d:Study/d:Variables/d:Variable[@kind='summary']/@role
  - /d:Study/d:Variables/d:Variable[@kind='summary']/@reviewed
  - /d:Study/d:Results/d:ItemResults/d:Result/@option
  - /d:Study/d:Results/d:ItemResults/d:Result/@share
minimum_n: 25
validity: group-level
ecological_caveat: no
output_form: table — outputs/T02/summary_measures.csv (63 measures × cohorts); summary.md (headline measures, All respondents)
script: scripts/p4_t02_summary_measures.py
outputs:
  - 04_analytics_library/outputs/T02/summary_measures.csv
  - 04_analytics_library/outputs/T02/summary.md
provenance: INFERRED (method); definitions approved by Scott (P4.S01)
---

# T02 — Summary measures

## Question
Rating questions answer on 4-point scales with no midpoint ("The scale structures were very intentional" — Scott). T02 reduces each rating to the share giving the answer that carries the meaning, so cohorts and gates can be compared on one number.

## Inputs
Each summary Variable's rule and role (headline / secondary), approved by Scott; the shares of the options the rule names.

## Method
For every summary variable and every cohort: sum the shares of the options its rule names. Definitions (P4.S01):
- Frequency (SC-FREQ4): headline "Frequently"; secondary "Occasionally + Frequently".
- Agreement (SC-AGREE4): "Agree + Strongly agree". Importance (SC-IMPORT4, listed high to low): "Very + Somewhat important".
- Differentiator (SC-DIFF3): "Important, and a differentiator". Q18: options 4 + 5, "had to do most / all of the business justification ourselves."
`p4_lib.measures()` checks each option against the rule text in the instance and stops on a mismatch. A value is computed only if every option it needs was asked of that cohort.

## Assumptions
Options within a single-choice question are mutually exclusive, so their shares add. The attention check (Q19_4) has no summary measure.

## Minimum n
Each value carries `usable` (cohort n ≥ 25 and item base ≥ 25). Comparisons use usable values only.

## Validity
Group-level percentages only.

## Output
`summary_measures.csv` — measure, role, item, thread, gate, cohort, dimension, value, base, n, usable, label. `summary.md` — headline measures for All respondents, highest first.

## Results on this study
See `outputs/T02/summary.md`.
