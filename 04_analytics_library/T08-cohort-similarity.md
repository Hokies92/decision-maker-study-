---
id: T08
title: Cohort similarity and clusters
gates: baseline; ACCESS; AGREE; VISION; CASE
question: Which cohorts have the most similar experience across all questions, and which cohorts stand apart?
required_xpaths:
  - /d:Study/d:Results/d:ItemResults/d:Result/@share
  - /d:Study/d:Results/d:ItemResults/d:Result/@base
  - /d:Study/d:Population/d:Cohorts/d:Cohort/@n
  - /d:Study/d:Population/d:Cohorts/d:Cohort/@dimension
  - /d:Study/d:Variables/d:Variable[@kind='summary'][@role='headline']/d:Rule
minimum_n: 25
validity: group-level
ecological_caveat: yes
output_form: table and chart — outputs/T08/cohort_clusters.csv, cohort_distances.csv, cluster_profiles_z.csv, cohort_dendrogram.svg, summary.md
script: scripts/p4_t08_cohort_similarity.py
outputs:
  - 04_analytics_library/outputs/T08/cohort_clusters.csv
  - 04_analytics_library/outputs/T08/cohort_distances.csv
  - 04_analytics_library/outputs/T08/cluster_profiles_z.csv
  - 04_analytics_library/outputs/T08/cohort_dendrogram.svg
  - 04_analytics_library/outputs/T08/summary.md
provenance: INFERRED (method)
---

# T08 — Cohort similarity and clusters

## Question
"Synthetic holism" (Scott, D1): recombine all questions into one profile per cohort and ask which cohorts share an experience. The Target gate is about the right people; T08 shows whether the right people differ in what they experience.

## Inputs
`p4_lib.cohort_matrix()` — 49 usable cohorts × 73 headline measures, complete.

## Method
1. Standardise each measure across cohorts (z-score); drop measures with no variation.
2. Euclidean distance between cohort profiles.
3. Hierarchical clustering, average linkage; cut at 4 clusters.
4. Each cohort's nearest neighbour; distance from the average profile; mean z-score of each measure per cluster.

## Assumptions
Every measure weighs the same after standardising. Clusters at k = 4 are a reading aid, not a claim that four types exist; the dendrogram shows the full structure. Cohorts overlap (a country and its region; a function, its levels and the combined levels), so near neighbours are partly the same people and some closeness is built in.

## Minimum n
Only usable cohorts (n ≥ 25, every base ≥ 25) enter; All respondents excluded.

## Validity
Group-level percentages.

## Ecological caveat
Similarity is between group profiles. Two cohorts with the same profile need not contain decision-makers with the same experience, and a distinctive cohort says nothing about any one member of it.

## Output
`cohort_clusters.csv` — cohort, label, dimension, n, cluster, nearest, nearest_distance, distance_to_centre. `cohort_distances.csv` — full distance matrix. `cluster_profiles_z.csv` — mean z-score per measure per cluster. `cohort_dendrogram.svg`.

## Results on this study
See `outputs/T08/summary.md`.
