---
id: T09
title: Map of cohorts × questions
gates: baseline; ACCESS; AGREE; VISION; CASE
question: On one picture, where does each cohort sit, and which questions pull cohorts apart?
required_xpaths:
  - /d:Study/d:Results/d:ItemResults/d:Result/@share
  - /d:Study/d:Results/d:ItemResults/d:Result/@base
  - /d:Study/d:Population/d:Cohorts/d:Cohort/@n
  - /d:Study/d:Variables/d:Variable[@kind='summary'][@role='headline']/d:Rule
minimum_n: 25
validity: group-level
ecological_caveat: yes
output_form: map — outputs/T09/cohort_coordinates.csv, measure_loadings.csv, explained_variance.csv, cohort_map.svg (biplot), summary.md
script: scripts/p4_t09_cohort_map.py
outputs:
  - 04_analytics_library/outputs/T09/cohort_coordinates.csv
  - 04_analytics_library/outputs/T09/measure_loadings.csv
  - 04_analytics_library/outputs/T09/explained_variance.csv
  - 04_analytics_library/outputs/T09/cohort_map.svg
  - 04_analytics_library/outputs/T09/summary.md
provenance: INFERRED (method)
---

# T09 — Map of cohorts × questions

## Question
A topology map (Scott, D1): place every cohort on two axes so the main differences between cohorts — and the questions that create them — can be seen at once.

## Inputs
The same matrix as T08: 49 usable cohorts × 73 standardised headline measures.

## Method
1. Standardise each measure across cohorts.
2. Principal components by singular value decomposition; fix each component's sign so its largest loading is positive (reproducible orientation).
3. Cohort coordinates on components 1–2; measure loadings; share of variation explained.
4. Biplot: cohorts as points; the 10 measures with the longest loading vectors as arrows.

## Assumptions
Linear structure: components capture the directions of greatest variation between cohorts. With 49 overlapping cohorts and 73 measures, components beyond the first few are not stable and are not interpreted. Correspondence analysis was considered; PCA on standardised shares was chosen because the measures are shares from different questions, not one contingency table.

## Minimum n
Only usable cohorts (n ≥ 25, every base ≥ 25) enter; All respondents excluded.

## Validity
Group-level percentages.

## Ecological caveat
The map places groups. Distances and directions describe how cohort profiles differ; they do not place any individual decision-maker, and overlapping cohorts sit close partly because they share members.

## Output
`cohort_coordinates.csv` — cohort, label, dimension, pc1, pc2. `measure_loadings.csv` — measure, gate, pc1, pc2. `explained_variance.csv`. `cohort_map.svg` — the biplot (groundwork for visualization concept 5, "the convergence").

## Results on this study
See `outputs/T09/summary.md`.
