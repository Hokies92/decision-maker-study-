# ADR-005 — Role level and stakeholder type: one configurable hierarchy

**Status:** proposed (P3.S01) · **Provenance:** hierarchy RECALL_DESIGNER (Scott, 2026-10-28); definitions VERBATIM (`cohort_dimensions.csv`); design INFERRED (Claude)

## Context
GOVERNANCE §5 P3: role level and stakeholder type are first-class, referenced entities attached to breakout groups, so every result cell is linkable to both through its group.

Scott (2026-10-28): "the role played in purchase is subordinate to IT or Business in this model. However there are many ways we can define roles and role hierarchies so lets not that and make sure we are flexible."

## Options
1. Two fixed lists, role level and stakeholder type, side by side. Contradicts Scott's single hierarchy.
2. Fixed elements for this survey's categories (ITDM, BDM, C-level …). Breaks the first time a client uses different roles.
3. **One hierarchy of nodes, each with a facet, defined in the instance.**

## Decision
Option 3.
- **StakeholderHierarchy** — `id`, provenance. v1 ships one: `DMS-SCREENER`.
- **Node** — `id`, `label` (VERBATIM where from source), `facet` ∈ {`stakeholderType`, `roleLevel`, `purchaseRole`, `department`, `itRole`}, optional `parent` (→ Node), definition, provenance.
- This study's hierarchy: `stakeholderType` ITDM, BDM at the top; `roleLevel` C-level, Vice president, Director, Manager under each; `department`, `itRole` and `purchaseRole` (decision stages) under the function they belong to.
- **Cohort → Node.** A cohort lists the nodes it carries (`carries stakeholderType="…" roleLevel="…"`). Examples:
  - `C-FUNCTION-ITDM` → stakeholder type ITDM.
  - `C-LEVEL-IT-DIRECTOR` → ITDM and Director.
  - `C-LEVEL-DIRECTOR` (combined) → Director, any stakeholder type.
  - `C-COUNTRY-UK` → none (company dimension).
- The facet list is an enumeration that can grow in a minor version (ADR-001). Another hierarchy (a client's roles) is another `StakeholderHierarchy` in the instance; no schema change.

The hierarchy carries no date; the study date is excluded (README).

## Consequences
- `Result → Cohort → Node(stakeholderType)` and `Result → Cohort → Node(roleLevel)` satisfy the §5 P3 criterion for every result whose cohort is a person cohort.
- Results for company or engagement cohorts (country, revenue, contact frequency) have no level or stakeholder value. That is correct: the source does not cross them with function or level.
- No respondent carries a node unless it was collected (ADR-009). Never inferred.

## Implementation notes (P3.S02–S05)

Added after the XSD was built and validated against real data. Each note records where the implementation refines the decision above; the decision itself is unchanged.

- **Nodes come from person cohorts.** One node per cohort in a person dimension (function, level within function, department, IT role, decision stage), with the parent taken from the cohort's parent. This gives 38 nodes.
- **Carries is a list of node references,** not two fixed attributes. A cohort carries its own node; a combined level cohort (e.g. `C-LEVEL-DIRECTOR`, from S2 + S3) carries the level node under each function (`N-LEVEL-IT-DIRECTOR`, `N-LEVEL-BUS-DIRECTOR`) — "Director, any stakeholder type." Stakeholder type is found by following a node's parents.
- **S5 decision stages** were asked of all 319, so their purchase-role nodes have no parent; S6 stages sit under the business function.
- **The 39 definable industry cohorts** have no parent cohort: the 39 → 7 mapping is not in source (variable `industry_39_to_7_map`, MISSING).
