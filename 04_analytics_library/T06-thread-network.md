---
id: T06
title: Thread network
gates: TARGET; baseline; ACCESS; AGREE; VISION; CASE; crossGate
question: How are the 37 questions connected by the links the instrument itself defines, which questions sit at the centre, and do the structural clusters match Scott's gates?
required_xpaths:
  - /d:Study/d:Graph/d:Link/@type
  - /d:Study/d:Graph/d:Link/@fromThread
  - /d:Study/d:Graph/d:Link/@fromItem
  - /d:Study/d:Graph/d:Link/@toThread
  - /d:Study/d:Graph/d:Link/@toItem
  - /d:Study/d:Grouping/d:AssignmentSet[@status='current']/d:Assignment/@thread
minimum_n: 25
validity: group-level
ecological_caveat: no
output_form: graph — outputs/T06/thread_metrics.csv, communities.csv, communities_vs_gates.csv, thread_network_all.graphml, thread_network_questions.graphml, thread_network_questions.svg, summary.md
script: scripts/p4_t06_thread_network.py
outputs:
  - 04_analytics_library/outputs/T06/thread_metrics.csv
  - 04_analytics_library/outputs/T06/communities.csv
  - 04_analytics_library/outputs/T06/communities_vs_gates.csv
  - 04_analytics_library/outputs/T06/thread_network_all.graphml
  - 04_analytics_library/outputs/T06/thread_network_questions.graphml
  - 04_analytics_library/outputs/T06/thread_network_questions.svg
  - 04_analytics_library/outputs/T06/summary.md
provenance: INFERRED (method); links as tagged in the instance
---

# T06 — Thread network

## Question
Scott (D1): make each question a thread so the threads can be iterated into networks and topology maps, for "analytical reductionism and also synthetic holism." T06 is the structural network: what the instrument connects, before any answer is read.

## Inputs
Every Link in the instance (381) and the current assignment set.

## Method
1. Fold item endpoints into their thread; drop links to groups and variables, `in_group` links, and self-loops.
2. Merge parallel links between two threads into one edge; edge weight = number of links, with their types.
3. Two views: all links; questions only (without `breakout_of` and `relates_to`, which connect every screener question to every structured question).
4. Per thread and view: distinct neighbours, links, betweenness centrality.
5. Questions view: communities by greedy modularity (deterministic); modularity of the found communities vs modularity of Scott's grouping on the same graph.

## Assumptions
Structural links describe how the instrument was built — shared scales, routing, "please specify" fields, text answers by the same respondents — not what answers mean. A low modularity for Scott's grouping says the gates are a conceptual grouping, not a structural one; it is not a judgment of the gates. Statistical links between answers are T07.

## Minimum n
T06 uses no cohort results. Respondent-overlap links carry counts from the full sample (318–319).

## Validity
Group-level (structure only).

## Output
`thread_metrics.csv` — view, thread, gate, neighbours, links, betweenness. `communities.csv`, `communities_vs_gates.csv`. GraphML for both views (node attributes: gate, label; edge attributes: links, types). `thread_network_questions.svg` — the questions view, shaded by gate.

## Results on this study
See `outputs/T06/summary.md`.
