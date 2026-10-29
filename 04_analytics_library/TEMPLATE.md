---
id: T00
title: Short name of the technique
gates: TARGET; ACCESS; AGREE; VISION; CASE; baseline; crossGate   # the gates it reads (one or more)
question: The question this technique answers, in one sentence
required_xpaths:
  - /d:Study/d:Results/d:ItemResults/d:Result/@share
  - /d:Study/d:Population/d:Cohorts/d:Cohort/@n
minimum_n: 25
validity: group-level        # group-level | needs respondent data: <what, and where it would go in the schema>
ecological_caveat: no        # yes when the technique links threads or items statistically across cohorts
output_form: table           # table | chart | graph | map — and the files written
script: scripts/p4_t00_example.py
outputs:
  - 04_analytics_library/outputs/T00/example.csv
provenance: INFERRED         # the method is Claude's design unless stated; inputs keep their own tags
---

# T00 — Short name of the technique

<!-- Every technique file starts with the front matter above. `scripts/p4_check_xpaths.py` reads it:
     every field is required, and every XPath must name elements and attributes that exist in the XSD. -->

## Question
What it answers, and why it matters for the gate model.

## Inputs
Which schema fields it reads (the XPaths above), in plain words.

## Method
The steps, exactly enough to reproduce by hand.

## Assumptions
What must be true for the result to mean anything (e.g. scale direction aligned; shares are column percentages).

## Minimum n
Cohorts and item bases below n = 25 are shown but never used in a comparison (Scott, 2026-10-28).

## Validity
Group-level percentages only, or the respondent-level data it would need and where that data would live in the schema.

## Ecological caveat
Required when the technique links threads statistically: results describe groups, not individuals.

## Output
Files written, their columns, and how to read them. Outputs are keyed by gate, cohort, and item so they can feed a visualization (Scott, 2026-10-29).

## Results on this study
Generated summary of the committed output (filled by the reference script run).
