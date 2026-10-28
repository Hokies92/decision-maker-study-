# Design Intent

Why the survey exists and what it was built to measure. Authored record (not generated). Every statement carries one provenance tag (GOVERNANCE §7).

| Tag | Source in this file |
|---|---|
| `RECALL_DESIGNER` | Scott Santucci, in chat, 2026-10-28. Quoted as written. |
| `RECON_REPORT` | REF-1: Santucci, S., "Using Selling Objectives To Corral Random Acts Of Sales Support," Forrester Research, May 29, 2014 — the published report built on this survey (its methodology section describes this study, N=319). |
| `RECON_DATA` | The source data files (SRC-002, SRC-003), checked by script or by direct reading. |
| `INFERRED` | Claude's reading. Pending Scott's review. |

Context-only references (lineage, not evidence about this study's fielding): REF-2 "Engineering Valuable Sales Conversations" (Forrester, Nov 12, 2008); REF-3 "Sales Enablement Defined" (Forrester, Aug 3, 2010).

**Scott's decision (2026-10-28):** REF-1–3 are context only. They are not added to the source register and not stored in this repository. "You may extract the context you need from it. I want to keep your focus as pure to extracting essence from the data provided." The data files remain the only evidence; this file is the only place the references are used.

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

### 2.4 Stakeholder hierarchy (`RECALL_DESIGNER`)

"No, the role played in purchase is subordinate to IT or Business in this model. However there are many ways we can define roles and role hierarchies so lets not that and make sure we are flexible."

Consequence for the schema (`INFERRED`): one stakeholder hierarchy, not two parallel dimensions — function (IT / business) at the top; level and purchase-process role (S2–S6) beneath it. Role definitions and hierarchy depth stay configurable, not fixed to this survey's categories.

## 3. How the survey maps to the gates

**Scott groups the questions himself** (2026-10-28: "your gate mapping is not intuitive to me. I'd rather you just give me a list of the questions in order and let me group them.").

- Input for Scott: `question_list.md` / `question_list.xlsx` — all 37 questions in survey order, wording as asked, with a blank "Scott's group" column.
- Scott's grouping will be recorded here, tagged `RECALL_DESIGNER`, and becomes the gate assignment used by later steps.
- Claude's draft mapping is withdrawn and not used. It remains in git history only (commit `88d0801`).

### 3.1 Scott's grouping, as received

**Screener S1–S12** — `RECALL_DESIGNER` (Scott, 2026-10-28): "This is demographic information. Think if this as "metadata" for context and it's an input to "target" if you organized this information in a structured way that allows a user to create cohorts based on choices from this information." Asked that the structure carry "tags to preserve relationships of down stream topics."

**Q1–Q25** — `RECALL_DESIGNER` (Scott, 2026-10-28). Group names as Scott wrote them; machine-readable copy in `scott_grouping.csv`.

| Scott's group | Gate | Questions |
|---|---|---|
| Baseline | — (new; not one of the five gates) | Q1, Q2, Q21 |
| Access | Access | Q3, Q4, Q5, Q6, Q7 |
| Successful meeting ("I call it agree to explore now") | Agree | Q8, Q9, Q10, Q11 |
| Shared Vision | Vision | Q12, Q13, Q14, Q15, Q16, Q17 |
| Business Case | Case | Q18, Q19, Q20 |
| Relationship accounts (open-ended) — own group, name proposed by Claude, accepted as "Own group" | Cross-gate; Phase 5 tags each answer to the gate it describes | Q22, Q23, Q24, Q25 |

Scott on scales (2026-10-28): "The scale structures were very intentional."

Resolved (Scott, 2026-10-28): Q21 — "Baseline only." Q22–Q25 — "Own group." Target has no Q-questions in Scott's grouping; its input is the screener (above).

## 4. Methodology as published (`RECON_REPORT`, REF-1 "Methodology") checked against the data

| # | REF-1 states (paraphrased) | Data (`RECON_DATA`) | Status |
|---|---|---|---|
| M1 | 319 senior-level executives in Canada, France, Germany, the UK, and the US | N=319; same five countries | **agrees** |
| M2 | Involved in purchasing technology products or services | S5/S6 decision-stage items; study centered on IT decisions | **agrees** |
| M3 | All respondents screened for significant involvement in IT decision-making, IT purchasing processes, and authorization | "Don't know / not involved" options (S5_6, S6_6, S6_7) are 0% | **agrees** — confirms these were screen-outs |
| M4 | Fielded online by Research Now; small monetary incentive; panel of volunteers; contact info and firm basics required for quality assurance | Header cell names "Research N…"; attention check Q19_4 present | **agrees** |
| M5 | 50% business side, 50% IT role | ITDM 160 / BDM 159 | **agrees** |
| M6 | Business side 29% C-suite or VP; IT role 30% C-suite or VP | IT 28.75% (C-level 21.25 + VP 7.5); business 30.19% (11.32 + 18.87) | **conflict → resolved:** report editing error; data stands |
| M7 | Companies with annual revenues of at least $500 million | 9.7% report revenue under $500M (2.5 + 2.5 + 4.7) | **conflict → resolved:** report editing error; data stands |
| M8 | A figure base in REF-1 reads "319 executive-level buyers at global companies with 100 or more employees" | Smallest employee bucket is labeled "1,0000 to 4,999 employees" (source typo; reads as 1,000) | **conflict → resolved:** report editing error; data stands |
| M9 | Statistical data intended to be descriptive, not inferential | — | carries into Phase 4 assumptions |

Per GOVERNANCE §7: where a published statement and the data conflict, the data is recorded as fielded; the conflict is logged in `STATE.md`.

M6–M8 resolved, `RECALL_DESIGNER` (Scott, 2026-10-28): "Its just sloppy editing on our part at Forrester." The sample is one consistent sample; the data's figures are authoritative.

## 5. Lineage (`RECON_REPORT`, REF-1 and REF-3) — context, not analysis

5.1 REF-1: "For the past six years, Forrester fielded an executive buyers study" — this survey is one wave of a recurring study.

5.2 REF-3 reports an earlier wave (166 North American enterprise business and IT decision-makers). Items with the same wording as this survey: Q1 (same 11 qualities), Q2, Q8 (three of the dimensions), Q9. Q21's question ("What differentiates a vendor from their competition the most?") was closed-ended in that wave and is open-ended here. Q9's top scale point was "Usually" there and is "Frequently" here.

5.3 REF-2 is the origin of Model-Map-Match and of the "valuable conversation" principles (timely, relevant, in context; authentic, accurate, actionable); REF-1 carries the "value communications process" term.

Study dates are excluded from analysis (README). Lineage is recorded as structure only.
