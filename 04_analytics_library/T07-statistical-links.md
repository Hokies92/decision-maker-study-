---
id: T07
title: Statistical thread links
gates: baseline; ACCESS; AGREE; VISION; CASE
question: Which questions move together across cohorts — where cohorts high on one answer are high (or low) on another — especially across gates?
required_xpaths:
  - /d:Study/d:Results/d:ItemResults/d:Result/@share
  - /d:Study/d:Results/d:ItemResults/d:Result/@base
  - /d:Study/d:Variables/d:Variable[@kind='summary'][@role='headline']/d:Rule
  - /d:Study/d:Population/d:Cohorts/d:Cohort/@n
  - /d:Study/d:Grouping/d:AssignmentSet[@status='current']/d:Assignment/@group
minimum_n: 25
validity: group-level
ecological_caveat: yes
output_form: table and graph — outputs/T07/measure_correlations.csv, candidate_links.csv, statistical_links.graphml, summary.md
script: scripts/p4_t07_statistical_links.py
outputs:
  - 04_analytics_library/outputs/T07/measure_correlations.csv
  - 04_analytics_library/outputs/T07/candidate_links.csv
  - 04_analytics_library/outputs/T07/statistical_links.graphml
  - 04_analytics_library/outputs/T07/summary.md
provenance: INFERRED (method; candidate links are a new link type, covaries_with)
---

# T07 — Statistical thread links

## Question
The statistical counterpart of T06 (parking lot P1.S00): links between threads found in the answers, not in the instrument.

## Inputs
`p4_lib.cohort_matrix()`: one headline measure per substantive question (73) × usable cohorts (49), complete.

## Method
1. For every pair of measures from different threads: Spearman rank correlation across cohorts (at least 20 cohorts with both values).
2. |rho| ≥ 0.6 → candidate link of type `covaries_with`, tagged INFERRED; flag whether it crosses gates.
3. Graph of candidate links (nodes = measures with thread and gate).

## Assumptions
Rank correlation, so scale differences between measures do not matter. Cohorts overlap (a country and its region; a function and its levels; combined and function-specific levels), so the 49 cohorts are not 49 independent observations, and no p-values are reported. The threshold 0.6 is a reading convention, not a test. `covaries_with` is not yet a schema link type; adding it would be a minor version.

## Minimum n
Only usable cohorts enter (cohort n ≥ 25 and item base ≥ 25); All respondents is excluded (it is the union of the others).

## Validity
Group-level percentages.

## Ecological caveat
Correlations across cohorts describe groups, not individuals. A strong rho says cohorts that score high on one measure tend to score high (or low) on the other; it does not say that the same decision-makers answer both ways, nor that one causes the other. Individual-level links need respondent-level answers (schema slot Respondent/Answer).

## Output
`measure_correlations.csv` — every pair: measures, threads, gates, cohorts, rho, candidate_link, cross_gate, link_type, provenance, caveat. `candidate_links.csv` — |rho| ≥ 0.6. `statistical_links.graphml`.

## Results on this study
See `outputs/T07/summary.md`.
