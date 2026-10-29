---
id: T04
title: Value vs experience
gates: AGREE; VISION; CASE
question: How far apart are what decision-makers say they value and what they report receiving from salespeople — and is the gap the same in every cohort?
required_xpaths:
  - /d:Study/d:Results/d:ItemResults/d:Result/@share
  - /d:Study/d:Results/d:ItemResults/d:Result/@option
  - /d:Study/d:Variables/d:Variable[@kind='summary']/d:Rule
  - /d:Study/d:Population/d:Cohorts/d:Cohort/@n
minimum_n: 25
validity: group-level
ecological_caveat: yes
output_form: table and chart — outputs/T04/value_vs_experience.csv (pair × cohort), gap_spread.csv, value_vs_experience.svg (dumbbell), summary.md
script: scripts/p4_t04_value_vs_experience.py
outputs:
  - 04_analytics_library/outputs/T04/value_vs_experience.csv
  - 04_analytics_library/outputs/T04/gap_spread.csv
  - 04_analytics_library/outputs/T04/value_vs_experience.svg
  - 04_analytics_library/outputs/T04/summary.md
provenance: INFERRED (method and pairs — pairs await Scott's review)
---

# T04 — Value vs experience

## Question
The asymmetry in one measure: the share of decision-makers who say something makes a salesperson valuable, against the share who say they frequently receive it. Two further pairs contrast how often salespeople are prepared on themselves vs on the customer.

## Inputs
Measures from T02 / `p4_lib.measures()`; the authored pair list `04_analytics_library/pairs.csv` (each pair names its measures and states why the two sides describe the same thing).

## Method
1. For each pair, side a = what is valued (or the salesperson's self-knowledge), side b = what is received (or knowledge of the customer). A side made of several options of one single-choice question is their sum.
2. For each cohort: a, b, gap = b − a. Negative = less received than valued.
3. Across usable cohorts: smallest, median and largest gap; whether the gap has the same sign in every cohort.

## Assumptions
The two sides of a pair come from different questions and scales (a selection from a list vs a frequency rating). The gap compares shares of the same cohort, not answers on one scale; treat its size as an order of magnitude and its direction as the finding. Pairs are Claude's (INFERRED) until Scott reviews `pairs.csv`.

## Minimum n
A pair's values for a cohort are `usable` only if every measure on both sides has cohort n ≥ 25 and item base ≥ 25. The spread statistics use usable cohorts only.

## Validity
Group-level percentages.

## Ecological caveat
Both sides are shares of the same cohort, but not necessarily of the same people: the decision-makers who value something may not be the ones who report not receiving it. The gap describes the group. Measuring it for individuals needs respondent-level answers (schema slot Respondent/Answer).

## Output
`value_vs_experience.csv` — pair_id, pair_type, gate, concept, cohort, dimension, a_value, b_value, gap, a_base, b_base, usable, provenance. `gap_spread.csv` — per pair across usable cohorts. `value_vs_experience.svg` — dumbbell chart, All respondents (the "about themselves vs about me" picture, concept 2).

## Results on this study
See `outputs/T04/summary.md`.
