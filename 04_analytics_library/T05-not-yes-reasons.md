---
id: T05
title: Not-yes reasons
gates: VISION
question: When decision-makers were interested and then pulled back, why — and how much of it happens where the vendor cannot see it?
required_xpaths:
  - /d:Study/d:Results/d:ItemResults[@item='Q15_2']/d:Result/@share
  - /d:Study/d:Results/d:SignificanceFlags/d:Flag[@thread='T-Q15']/@state
  - /d:Study/d:Population/d:Cohorts/d:Cohort/@n
minimum_n: 25
validity: group-level
ecological_caveat: no
output_form: table and chart — outputs/T05/reasons_by_cohort.csv, not_yes_reasons.svg, summary.md
script: scripts/p4_t05_not_yes_reasons.py
outputs:
  - 04_analytics_library/outputs/T05/reasons_by_cohort.csv
  - 04_analytics_library/outputs/T05/not_yes_reasons.svg
  - 04_analytics_library/outputs/T05/summary.md
provenance: INFERRED (method; the visible / inside classification is Claude's)
---

# T05 — Not-yes reasons

## Question
Q15 is the survey's direct measure of a 0 at the Vision gate, in the decision-maker's own word: "pull back." T05 ranks the reasons per cohort and marks which the vendor can see (another vendor won) and which happen inside the customer's company after the vendor leaves.

## Inputs
Shares selecting Q15_1–Q15_8 per cohort; Q15 significance flags (the Main Page's condensed table names thread T-Q15).

## Method
1. For each cohort, the share selecting each reason, and its rank within the cohort.
2. Mark where each reason happens: Q15_1 visible to the vendor; Q15_2–Q15_6 inside the customer's company; Q15_7 other; Q15_8 don't know (INFERRED).
3. Count, across usable cohorts, how often each reason ranks first.
4. Report the source's significance flags for Q15 by dimension.

## Assumptions
Q15 allows several reasons, so shares do not add up across reasons and no "total internal" figure is computed. The classification of where a reason happens is an interpretation (the vendor can observe losing to a competitor; it cannot observe internal momentum or risk judgments).

## Minimum n
Ranks across cohorts use usable cohorts only (cohort n ≥ 25 and base ≥ 25).

## Validity
Group-level percentages.

## Output
`reasons_by_cohort.csv` — item, label, where, where_provenance, cohort, dimension, value, base, n, usable, rank_in_cohort. `not_yes_reasons.svg` — bar chart, black = visible to the vendor, grey = inside the customer's company (groundwork for visualization concept 3, "after the vendor leaves the room").

## Results on this study
See `outputs/T05/summary.md`.
