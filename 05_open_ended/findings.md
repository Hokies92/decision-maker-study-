# Findings from the open-ended answers (P5.S07)

Authored record (Claude, INFERRED). Every number here comes from a generated file: `views/coded/summary.md` and the CSVs beside it (`scripts/p5_build_coded_views.py`), `consistency_report.md` (`scripts/p5_agreement.py`), and Phase 4 output T04. The P5 cross-check confirms each number appears in a generated file. Unit: one answer unless stated. Of 1,697 answers, 748 are codable. Best = Q22 and Q24; worst = Q23 and Q25; Q21 = what makes a vendor different.

## What is valid

1. **One behaviour dominates both sides: knowing the customer's business.** It is the most common Q21 criterion (71 answers). It is also the most common effective behaviour in best accounts (70). It still shows up 31 times as ineffective in worst accounts. By the Johnston rule it is a *satisfier*. Layer: behaviour, alpha 0.87.

2. **Satisfiers are about knowledge and help; dissatisfiers are about conduct.**
   - Satisfiers (10) include knowing the business, solving problems (8% ineffective), product expertise, insight, relationship and partnership.
   - Dissatisfiers (4):
     - selling for the vendor instead of the customer, B-CUSTOMER-FIRST: 52 ineffective vs 9 effective (84%);
     - respect (90%);
     - being easy to deal with (72%);
     - honesty (67%).
   - 12 behaviours are *critical*: they decide the account either way. Examples are responsiveness, commitment, competence, price and flexibility.

   In plain terms: decision-makers credit salespeople for what they know and how they help, and blame them for how they behave.

3. **The free text runs the same direction as the structured gaps (T04), at concept level.**

   | Concept | Structured gap (T04, All) | Open-ended answers |
   |---|---|---|
   | The pitch (P05): product presentation gets more than it is valued | +0.44 | Linked codes appear 58 times in worst accounts, 11 in best |
   | Knowing my business, my issues, and preparing on me rather than on themselves (P01, P03, C01, C02): valued more than received | −0.38 to −0.40 | Linked codes appear 70–95 times as effective in best accounts |

   Both sources say the same thing: what customers get is the pitch, and what they want is to be understood.

   The link is by concept, not by person. The two sources cannot be joined respondent by respondent. The concept map (`t04_concept_links.csv`) is INFERRED and is for Scott's review.

4. **The biggest structural gap is almost silent in the free text.**
   - "Equipped to make the case" (P07) has the largest T04 gap: −0.47.
   - Only 30 open-ended answers carry the codes linked to it.
   - Helping the decision-maker sell internally (B-HELPS-SELL-INTERNALLY) appears in 1 experiential answer.

   Decision-makers rate this as valued and not received when asked directly, but they do not name it when describing their best and worst salespeople. A gap no one can put into words is consistent with the lexicon finding that the customer side has no word for it (L17 is a gap concept).

5. **The free text is about the meeting and the relationship, not the first gates.** Primary gate of codable answers:
   - Relationship: 272
   - Agree: 161
   - No single gate: 143
   - Vision: 80
   - Case: 79
   - Access: 10
   - Target: 3

   Asked about sales teams in general, decision-makers describe what happens once a salesperson is in the room and afterwards.

6. **The account manager carries the best relationships; the sales rep carries the worst.**
   - Account manager: 90 best vs 40 worst (69% best).
   - Sales rep: 15 best vs 47 worst (24% best).
   - Technical contacts lean best: 14 vs 4.

   Roles are matched by pattern (INFERRED).

7. **Attribution is split between the person and the company, in Q21 and in best and worst accounts alike.**
   - The salesperson is credited or blamed in 52–54% of codable answers, depending on the frame (33% in "please specify" answers).
   - The vendor organisation is credited or blamed in 43–50%.
   - The product is rarely credited or blamed (2–8%).
   - The decision-maker's own company is almost never blamed, except in a few "please specify" answers.

   Layer: attribution, alpha 0.83.

8. **Empathy is the leading SERVQUAL dimension in every frame, and most of all in worst accounts.**
   - Differentiator: 46%
   - Best: 51%
   - Worst: 59%

   Responsiveness is higher in best accounts (24%) than in worst (17%). Layer: servqual, alpha 0.85.

9. **The answers are shallow ladders.** Only 15 of 748 reach a personal or organisational value. Most stop at an attribute. Means-end analysis can describe *what* is valued here, not *why*.

10. **Decision-makers do not split into distinct types by what they talk about.**
    - Typology silhouette: 0.04, i.e. weak structure.
    - One type holds 150 of 219 respondents. It is led by knowing the business and solving problems.

    This matches Phase 4, where 45 of 49 cohorts share one profile.

11. **The same respondent often reports a dimension both well and badly:** 107 of 1,115 respondent–dimension pairs. Their best and worst accounts differ on the same behaviour. This is the CIT contrast at the level of one person.

## Vendors and names

- IBM is named most for the best teams: 85 best vs 17 worst. It is praised mostly for knowing the business and solving problems.
- Vendors named more for the worst than the best (≥ 5 mentions):
  - Dell: 9 vs 16
  - AT&T: 4 vs 7
  - Verizon: 4 vs 5
  - Siemens: 1 vs 5
- Full table with "praised for / criticised for": `views/coded/vendors.csv`. The search index, by vendor and by feedback: `index/answers_search.csv`.
- **Invalid reading:** these counts are not ratings. A large vendor is named more often in both lists, so the share best (e.g. IBM 83%) is the only comparable figure, and only for vendors with enough mentions.

## Lexicon pass 2 — the decision-makers' own words

These are candidate words for Scott to name the gap concepts:
- **Being condescended to (L28):** 10 answers, 9 in worst accounts. Most frequent words: *arrogant*, plus vendor names.
- **Selling inside the vendor on the customer's behalf (L27):** 17 answers, 11 in best accounts. Words: *account manager*, *resources*, *quickly*.
- **Being contacted (L05):** 7 answers. Words: *agressive*, *cold*, *calling*.

Five concepts are never expressed in the free text: L01, L04, L06, L07, L24. Several gap concepts are thin (≤ 7 answers): L02, L10, L16, L17, L18.

The main coder never used L26 (judging sales teams). The blind coder used it on every Q22/Q23 answer. The rule for L26 needs Scott's call (`coding/recode_notes.md`).

## What is invalid

- Reading any open-ended count as a property of a role level or stakeholder type. Respondents have no level or stakeholder in the source.
- Joining open-ended answers to structured cohorts person by person. The T04 link is at concept level only.
- Treating vendor mention counts as quality ratings.
- Treating the typology as segments (silhouette 0.04).
- Treating NMF topics as themes. Normalised mutual information with the hand-coded primary behaviour is 0.12. The topics find roles and vendor names (topic 3: ibm, oracle, sap; topic 6: hp, microsoft, dell), not behaviours.

## What is unknown

- Whether the lexicon results hold under a settled L26 rule. Lexicon presence alpha is 0.72 (usable with caution); without L26 it is 0.83.
- Why the case-building gap is silent in the free text: the customer side has no word for it, or the questions (best and worst *sales teams*) did not invite it.
- Whether the answers are cut off: the longest stop near 255 characters (P2.S06).
- The coders are two models. Agreement shows the frame is applied consistently, not that the codes are true.
