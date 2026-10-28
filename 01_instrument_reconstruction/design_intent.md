# Design Intent

Why the survey exists and what it was built to measure. Authored record (not generated). Every statement carries one provenance tag (GOVERNANCE §7).

| Tag | Source in this file |
|---|---|
| `RECALL_DESIGNER` | Scott Santucci, in chat, 2026-10-28. Quoted as written. |
| `RECON_REPORT` | REF-1: Santucci, S., "Using Selling Objectives To Corral Random Acts Of Sales Support," Forrester Research, May 29, 2014 — the published report built on this survey (its methodology section describes this study, N=319). |
| `RECON_DATA` | The source data files (SRC-002, SRC-003), checked by script or by direct reading. |
| `INFERRED` | Claude's reading. Pending Scott's review. |

Context-only references (lineage, not evidence about this study's fielding): REF-2 "Engineering Valuable Sales Conversations" (Forrester, Nov 12, 2008); REF-3 "Sales Enablement Defined" (Forrester, Aug 3, 2010). The three reference documents are Forrester-copyrighted and are **not** stored in this repository; they are cited only.

---

## 1. Purpose of the study

1.1 `RECALL_DESIGNER` — "the purpose of the document is to 1) frame the how the salesperson shapes decision making within companies then, using to binary logic of the sales objectives"

1.2 `RECALL_DESIGNER` — "100% of the questions are designed to capture decision makers experience or their side of the table in their words without imposing words like "buyer" "buying process" or anything else that the vendor organization simply can't see."

1.3 `RECON_DATA` — Check of 1.2 against the question wording and answer options (all 136 items, all 118 option lists): the words *buyer*, *buying*, *buying process*, *funnel*, *pipeline*, *prospect*, and *lead* do not appear. Terms that do appear are ones visible from the customer's side. Question wording: *vendor(s)* 88, *sales* 59, *purchase(s)* 15, *supplier(s)* 5, *sell* 1 (S11, about the respondent's own company). Answer options: *vendor(s)* 8, *purchase(s)* 7, *sales* 6, *sell* 1. **Consistent with 1.2.**
Note: Forrester's packaging of the study does use "buyer" (file name "buyer research"; study title "Executive Buyer Insight Online Survey" in REF-1). That is the publisher's label, not the instrument's wording.

1.4 `RECALL_DESIGNER` — "The two documents are merely for context so you can see WHY this researc is so important to a bigger and broader vision of what "sales enablement" is and or means."

## 2. The gate model

### 2.1 Original form — four selling objectives (`RECON_REPORT`, REF-1)

REF-1 defines four verifiable objectives every salesperson must achieve, each validated "in a binary way." Paraphrased; milestones as stated in REF-1:

| Objective (REF-1) | Verifiable milestone in REF-1 |
|---|---|
| Gain the appropriate level of access | A meeting secured with the specific level of decision-maker required |
| Have successful meetings | "The client has agreed to explore further" (starting point) |
| Create a shared vision of success | Client has marked up the proposal, modifications discussed, both parties agree |
| Develop a business case | The client executes the contract or not |

### 2.2 Current form — five binary gates (`RECALL_DESIGNER`)

2.2.1 "My NEW version of this a series of binary gates that are designed to track choices (which is the foundational source of reality) and to measure state change"

2.2.2 Gates, quoted:

| Gate | Question (quoted) |
|---|---|
| **Target** | "Did the vendor and then the salesperson target the right message to the right people (Target 1 or 0)" |
| **Access** | "Did the vendor and then the salesperson gain access to the right people (Access 1 or 0)" |
| **Agree** | "Did the vendor and then the salesperson gain agreement with the right people to explore the idea further (Agree 1 or 0)" |
| **Vision** | "Did the vendor and then the salesperson gain a shared vision of success with the right people (Vision 1 or 0)" |
| **Case** | "Did the vendor and then the salesperson provide a business case for the idea the client accepts (case 1 or 0)" |

2.2.3 "Then the terminal stage (contrat or no contract) is not considered part of the selling process (or as I call it now the value communication process)"

2.2.4 "ii) - not provided in the source, but how to define the agreement network (Now "target")" — Target is new; it has no counterpart among REF-1's four objectives.

2.2.5 On time: "I track time more like Leibniz than Newton and I use the gates to align event time "bergionsian" and factor in kairos time (creating coachable moments) so the easiest thing to manage is choices."

### 2.3 Differences between 2.1 and 2.2 (`INFERRED`, from comparing the two)

- Target is added ahead of Access; it defines the agreement network — the "right people" every later gate refers to.
- Each gate is attributed first to the vendor, then to the salesperson ("the vendor and then the salesperson").
- The Case gate closes when the client **accepts the business case**, not when the contract is executed; the contract is a terminal state outside the value communication process.
- Time is relational and event-ordered (gate transitions), not clock time; kairos marks the moments where coaching can change a choice.

## 3. How the survey maps to the gates (`INFERRED` — for Scott's review)

The survey measures the gates from the customer's side: what the decision-maker experienced at each gate, in their words. Proposed assignment of threads (question IDs as in `question_map.csv`):

| Gate | Threads | Why (wording) |
|---|---|---|
| **Target** — the right people | S1–S12 | Who the decision-maker is: department, IT vs business, level, IT role, decision stages (S5/S6), company, industry, frequency of contact |
| **Target** — the right message | Q1, Q2, Q12, Q21 | What qualities make a vendor strategic; whether material is relevant and "written for people like me"; what differentiates a vendor |
| **Access** | Q3, Q4, Q5, Q6, Q7 | Channels responded to, referrals acted on, requests screened out, appointments accepted, reasons to accept |
| **Agree** | Q8, Q9, Q10, Q11, Q13, Q14 | Salesperson preparedness; meetings valuable; Q10 "how often do you accept follow-on meetings?" (= agree to explore further); what makes a meeting valuable; salesperson's agenda |
| **Vision** | Q16, Q19 | Q16 "choose a vendor who has worked with you to turn a vision into a clear path to value"; attributes for shaping a vision into a program plan |
| **Case** | Q17, Q18, Q20 | Difficulty of building a business case; whether vendor materials help "develop convincing reasons to invest"; purchase authority |
| **Gate failures** | Q15 | Each Q15 option reads as a 0 at a gate — see 3.1 |
| **Relationship outcomes** (open) | Q22–Q25 | Best/worst sales teams and points of contact — the decision-maker's account of where gates were passed or failed |

3.1 Q15 ("…you changed your mind and did not make a purchase. What were some of the reasons why you pulled back…") as gate failures:

| Q15 option (VERBATIM, abbreviated) | Gate that returned 0 |
|---|---|
| Q15_2 "I could not envision how the value would be delivered." | Vision |
| Q15_3 "It became too risky of a purchase." | Case |
| Q15_4 "Others internally got involved and the effort to keep the momentum…" | Target / Agree (agreement network widened) |
| Q15_5 "I struggled to get others on board internally." | Vision (shared across the network) |
| Q15_6 "I didn't have a clear path in my mind on who I'd delegate this…" | Vision → Case (path to value) |
| Q15_1 "I pursued the opportunity with a different vendor." | Competitive loss — gates passed by another vendor |

## 4. Methodology as published (`RECON_REPORT`, REF-1 "Methodology") checked against the data

| # | REF-1 states (paraphrased) | Data (`RECON_DATA`) | Status |
|---|---|---|---|
| M1 | 319 senior-level executives in Canada, France, Germany, the UK, and the US | N=319; same five countries | **agrees** |
| M2 | Involved in purchasing technology products or services | S5/S6 decision-stage items; study centered on IT decisions | **agrees** |
| M3 | All respondents screened for significant involvement in IT decision-making, IT purchasing processes, and authorization | "Don't know / not involved" options (S5_6, S6_6, S6_7) are 0% | **agrees** — confirms these were screen-outs |
| M4 | Fielded online by Research Now; small monetary incentive; panel of volunteers; contact info and firm basics required for quality assurance | Header cell names "Research N…"; attention check Q19_4 present | **agrees** |
| M5 | 50% business side, 50% IT role | ITDM 160 / BDM 159 | **agrees** |
| M6 | Business side 29% C-suite or VP; IT role 30% C-suite or VP | IT 28.75% (C-level 21.25 + VP 7.5); business 30.19% (11.32 + 18.87) | **conflict** — figures appear swapped between IT and business |
| M7 | Companies with annual revenues of at least $500 million | 9.7% report revenue under $500M (2.5 + 2.5 + 4.7) | **conflict** |
| M8 | A figure base in REF-1 reads "319 executive-level buyers at global companies with 100 or more employees" | Smallest employee bucket is labeled "1,0000 to 4,999 employees" (source typo; reads as 1,000) | **conflict** — 100 vs 1,000 |
| M9 | Statistical data intended to be descriptive, not inferential | — | carries into Phase 4 assumptions |

Per GOVERNANCE §7: where a published statement and the data conflict, the data is recorded as fielded; the conflict is logged in `STATE.md`.

## 5. Lineage (`RECON_REPORT`, REF-1 and REF-3) — context, not analysis

5.1 REF-1: "For the past six years, Forrester fielded an executive buyers study" — this survey is one wave of a recurring study.

5.2 REF-3 reports an earlier wave (166 North American enterprise business and IT decision-makers). Items with the same wording as this survey: Q1 (same 11 qualities), Q2, Q8 (three of the dimensions), Q9. Q21's question ("What differentiates a vendor from their competition the most?") was closed-ended in that wave and is open-ended here. Q9's top scale point was "Usually" there and is "Frequently" here.

5.3 REF-2 is the origin of Model-Map-Match and of the "valuable conversation" principles (timely, relevant, in context; authentic, accurate, actionable); REF-1 carries the "value communications process" term.

Study dates are excluded from analysis (README). Lineage is recorded as structure only.
