# Design Brief — Decision Maker Study Schema v1

Authored record (P3.S01). It defines what the schema holds and why; the XSD (P3.S02) implements it. Each design choice that is not obvious has a decision record in `decisions/`.

| Tag | Source in this file |
|---|---|
| `RECALL_DESIGNER` | Scott Santucci, in chat. Quoted as written. |
| `RECON_DATA` | Counts and structures read from Phase 1 and Phase 2 outputs. |
| `INFERRED` | Claude's design choices. Scott approves or rejects them when he merges this step. |

---

## 1. Purpose

1.1 `RECALL_DESIGNER` (2026-10-29, confirmed "This is exaclty correct."): the goal is to make the gate model operable. Every answer is stored as "this cohort's experience at this gate," in a schema that can later hold individual choices over time, so the same structure works for new data and for coaching.

1.2 `RECALL_DESIGNER` (2026-10-29, D3-1): "I want the gates to be a way we interface with other research and work."

1.3 `RECALL_DESIGNER` (2026-10-29, D3-2): a decision-maker's path is stored as an ordered sequence of gate events. Clock time is optional. "Yes. I agree."

1.4 `RECALL_DESIGNER` (2026-10-29, D3-3): one synthetic test record proves the individual layer. "Yes."

## 2. What the schema holds, and what it does not

| Holds now (from source) | Count | Source file |
|---|---|---|
| Threads (one per question) | 37 | `question_map.csv` |
| Items (sub-questions) | 136 | `question_map.csv` |
| Response scales | 34 | `response_scales.csv`, `item_scales.csv` |
| Routing rules | 24 | `routing.csv` |
| Cohort dimensions | 16 | `cohort_dimensions.csv` |
| Cohorts (58 tabulated, 57 definable) | 115 | `cohorts.csv` |
| Results (item × option × cohort) | 24,552 | `results.csv` |
| Significance flags (question × dimension) | 1,686 | `significance.csv` |
| Links between threads, items and groups | 381 | `linkages.csv` |
| Variables (collected, derivable, missing) | 189 | `variable_dictionary.csv` |
| Thread → group → gate assignment (Scott's) | 37 | `scott_grouping.csv` |
| Respondents with text answers | 319 | SRC-003, SRC-002 "Other" sheet |

| Reserved, empty in this study | Why it is empty |
|---|---|
| A respondent's own function, level and purchase role | Not in source. Never inferred (CLAUDE.md). |
| A respondent's structured answers | The source is tables only (SRC-002). |
| Decision paths: one decision-maker's gate events in order | No individual gate choices were collected. This is the slot for new data and coaching (§1.1). |
| Clock time on events | The study date is excluded from analysis (README). |

## 3. Entity model

Two vocabularies. The **gate model** stands alone so other research can use it without this survey (ADR-002). The **study** uses the gate model and holds everything else.

```
gates/v1  (module — reusable on its own)
  GateModel ── Gate ×5 (Target, Access, Agree, Vision, Case; order 1–5; states 1 = yes / 0 = not yes)
            └─ Crosswalk ── Mapping (outside item → Gate, with source and provenance)

dms/v1  (study)
  Study
  ├─ Sources ............ SRC-002, SRC-003 (citations target these)
  ├─ Instrument
  │   ├─ Scale ── Option
  │   ├─ Thread ── Item (→ Scale; role: asked / attention_check / derived / text)
  │   └─ RoutingRule (applies to Items)
  ├─ Population
  │   ├─ StakeholderHierarchy ── Node (facet: stakeholderType | roleLevel | purchaseRole; parent Node)
  │   ├─ Dimension (layer: person | company | engagement; parent Dimension)
  │   └─ Cohort (→ Dimension; → parent Cohort; → Nodes it carries: stakeholder type, role level)
  ├─ Grouping
  │   ├─ Group (Scott's 7 groups; → Gate, or role: input | baseline | crossGate)
  │   └─ AssignmentSet ── Assignment (Thread → Group)   [editable; more than one set allowed]
  ├─ Results
  │   ├─ Result (Item × Option × Cohort: share or not-asked, base n, cell citation)
  │   └─ SignificanceFlag (Item block × Dimension: significant | notSignificant | notTested)
  ├─ Variables ── Variable (collected | derivable | missing; derivation rule; → Item)
  ├─ Graph ── Link (typed endpoints: Thread | Item | Group | Variable; type; weight; evidence)
  └─ Respondents  (optional)
      └─ Respondent (respid)
          ├─ TextAnswer (→ Item; text VERBATIM, unchanged)
          ├─ Attributes (optional → stakeholder Nodes; empty unless collected)
          └─ DecisionPath ── GateEvent (seq; → Gate; state 1|0; Reason → Thread/Item/Option; optional clock time)
```

How a result reaches role level and stakeholder type (the §5 P3 requirement): `Result → Cohort → Node(stakeholderType)` and `Result → Cohort → Node(roleLevel)`. Example: Q9 "Frequently" for C-LEVEL-IT-DIRECTOR → stakeholder type ITDM, role level Director.

How a result reaches a gate: `Result → Item → Thread → Assignment → Group → Gate`. The gate is never copied onto the result, so regrouping changes one assignment, not 24,552 results (ADR-003).

## 4. Rules that apply everywhere

- **Identifiers** reuse the project's existing IDs (`T-Q15`, `Q15_2`, `C-LEVEL-IT-DIRECTOR`, `D-COUNTRY`, `SC-FREQ4`, `R05`). Every reference is enforced by the XSD (key/keyref). A reference to something absent fails validation (ADR-012).
- **Provenance** is a required attribute on every element that states a fact. It takes the six governance tags; `SYNTHETIC` is allowed only in test fixtures (ADR-008).
- **Citations.** Every value read from source carries its cell (`SRC-002 Industry 7!B15`).
- **No study date** anywhere. Time is event order (ADR-010).
- **Wording.** Source wording is stored unchanged and tagged `VERBATIM`. Project-authored labels use "customers" and "salespeople."
- **Minimum n = 25** is a property of each cohort (`belowMinimum`), visible but never removed (Scott, 2026-10-28).
- **Values are not recomputed.** Shares are stored as tabulated. Derived and summary variables are stored as definitions; their values belong to Phase 4 (ADR-011).

## 5. Instance documents planned (P3.S03)

| File | Contents | Proves |
|---|---|---|
| `examples/full_study.xml` | Every entity in §2, no respondent layer | The whole study fits; the respondent layer is optional |
| `examples/thread_q15.xml` | One thread (Q15, "pulled back") with its items, scale, all cohorts, results, flags, links and gate | A self-contained slice validates; the shape is readable |
| `examples/respondents_open_ended.xml` | The 319 respondents and their text answers (Q21–Q25, "please specify"), unchanged | The respondent layer holds real respondent-level data |
| `tests/synthetic_decision_path.xml` | One invented decision-maker's path through the five gates, root marked synthetic | The decision-path layer validates (D3-3). Not data; not in `examples/` |

## 6. Decision records

| ADR | Decision |
|---|---|
| [ADR-001](decisions/ADR-001-namespaces-and-versioning.md) | Two namespaces, `…/dms/v1` and `…/gates/v1`; semantic versioning; the major version lives in the namespace |
| [ADR-002](decisions/ADR-002-gate-model-as-separate-module.md) | Gates are a stand-alone module with permanent IDs and a crosswalk for outside work |
| [ADR-003](decisions/ADR-003-editable-gate-assignment.md) | Thread → group → gate goes through named, editable assignment sets |
| [ADR-004](decisions/ADR-004-result-cell.md) | A result is item × option × cohort, with share, base and cell citation |
| [ADR-005](decisions/ADR-005-stakeholder-hierarchy.md) | Role level and stakeholder type are nodes in one configurable hierarchy, attached to cohorts |
| [ADR-006](decisions/ADR-006-threads-and-links.md) | Threads hold items; links are first-class edges with typed endpoints |
| [ADR-007](decisions/ADR-007-significance-flags.md) | Significance is a flag on question × dimension, not on cells |
| [ADR-008](decisions/ADR-008-provenance-on-every-element.md) | Provenance is required on every fact; `SYNTHETIC` only in test fixtures |
| [ADR-009](decisions/ADR-009-respondent-layer-and-decision-paths.md) | The respondent layer is optional; decision paths are ordered gate events |
| [ADR-010](decisions/ADR-010-time-as-order.md) | No study date; time is order, clock time optional |
| [ADR-011](decisions/ADR-011-derived-variables-as-definitions.md) | Derived variables are stored as definitions, not values |
| [ADR-012](decisions/ADR-012-one-document-type-and-references.md) | One document type, optional sections, all references enforced |
| [ADR-013](decisions/ADR-013-synthetic-test-fixture.md) | The synthetic record lives in `tests/`, marked at the root, and is excluded from every count |

## 7. Not in v1 (parking lot)

- The asymmetry lexicon as schema elements (concepts linked to gates and threads). It suits the gate interface, but it is not in the Phase 3 plan.
- Computed values for summary measures — Phase 4, after Q-P2a.
- Phase 5 codes on text answers — the respondent layer leaves room for them (`TextAnswer` can take codes in a minor version).
