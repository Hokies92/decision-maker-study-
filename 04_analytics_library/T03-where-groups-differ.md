---
id: T03
title: Where groups differ
gates: baseline; ACCESS; AGREE; VISION; CASE
question: At which gates does who you are (country, level, function, company) change the experience — and where does it stop mattering?
required_xpaths:
  - /d:Study/d:Results/d:SignificanceFlags/d:Flag/@state
  - /d:Study/d:Results/d:SignificanceFlags/d:Flag/@dimension
  - /d:Study/d:Results/d:SignificanceFlags/d:Flag/@item
  - /d:Study/d:Results/d:SignificanceFlags/d:Flag/@thread
  - /d:Study/@confidenceLevel
minimum_n: 25
validity: group-level
ecological_caveat: no
output_form: table and chart — outputs/T03/significance_by_gate.csv, significance_by_gate_total.csv, significance_by_gate.svg (heat map), summary.md
script: scripts/p4_t03_where_groups_differ.py
outputs:
  - 04_analytics_library/outputs/T03/significance_by_gate.csv
  - 04_analytics_library/outputs/T03/significance_by_gate_total.csv
  - 04_analytics_library/outputs/T03/significance_by_gate.svg
  - 04_analytics_library/outputs/T03/summary.md
provenance: INFERRED (method); flags RECON_DATA
---

# T03 — Where groups differ

## Question
The source tests, for every question and every breakout dimension, whether the groups' answers differ (SRC-002 cell comments, 95% confidence; ADR-007). T03 counts how often they do at each gate.

## Inputs
Every significance flag (significant / not significant / not tested), its question block (item, or thread for the condensed Main Page Q15), and its dimension.

## Method
1. Drop flags marked not tested and the All-respondents placeholders.
2. Attach each flag's gate through its thread and the current assignment set.
3. For each gate × dimension: tests, significant tests, share significant. Mark cells with fewer than 10 tests.
4. Totals per gate.

## Assumptions
Each flag is the source's own verdict; the test statistic is not in the source (variable `significance_statistics`, MISSING). Tests are not independent (several items per question; overlapping cohorts), so shares are descriptive counts, not a combined test. At 95% about 5% of tests are significant by chance.

## Minimum n
The source marks tables too small to test as "not tested"; those are excluded. T03 makes no comparison between cohorts itself.

## Validity
Group-level: each flag tests groups, not individuals.

## Output
`significance_by_gate.csv` — gate, dimension, tested, significant, share_significant, few_tests. `significance_by_gate_total.csv` — per gate. `significance_by_gate.svg` — heat map, gate × dimension.

## Results on this study
See `outputs/T03/summary.md`.
