# ADR-014 — Open-ended codes as a separate, optional layer

**Status:** proposed (P5.S08) · **Provenance:** design INFERRED (Claude); requirements from GOVERNANCE §5 P5 (codes separate from verbatims) and Scott D5-3 (multi-code, one primary)

## Context
Phase 5 coded the 1,697 respondent-level text answers on eight layers (`05_open_ended/codes.csv`, coding frame v1.1). The schema must carry those codes without changing the verbatims (ADR-009: `TextAnswer` is `VERBATIM`), and every instance valid under 1.1.0 must stay valid (ADR-001: minor version = additive).

## Decision
- **`TextAnswer/@id`** (optional): the stable answer ID — item + source row (`Q22-R144`), as in `05_open_ended/corpus.csv`. Declared with `xs:unique`, not `xs:key`: a key would require the ID on every answer and break 1.1.0 instances.
- **`Study/Coding`** (optional, after `Respondents`), `@frameVersion`:
  - **`CodeDef`** (1..n) — one per code in the frame: `@id`, `@layer`, `@label`, `@origin` (deductive / inductive), `@provenance`; `Definition`, optional `Include`, `Exclude`, `Example`.
  - **`Applied`** (0..n) — one code on one answer: `@answer` (→ `TextAnswer/@id`), `@code` (→ `CodeDef/@id`), optional `@polarity` (+ / −, behaviour codes only), `@primary` (one per answer and layer, D5-3), `@coder`, `@provenance`.
- Keyrefs `appliedAnswerRef` and `appliedCodeRef` enforce both references.

Rules beyond XSD 1.0, checked by `scripts/p5_crosscheck.py`:
- A not-codable answer carries one N- code and nothing else.
- Polarity appears on behaviour codes only.
- Codes never reach a respondent's level or stakeholder type.

## Consequences
- Codes sit beside the verbatims, never inside them. Re-coding replaces `Coding` and leaves `Respondents` unchanged.
- A second coder's codes can sit in the same section under another `@coder`, so agreement can be computed from one document.
- Each code reaches its thread through answer → item → thread, and its gate through the gate codes. It does not reach a cohort: the respondent has no level or stakeholder type (ADR-009).
- The three 1.1.0 examples are not regenerated. The coded example is a separate file (`examples/respondents_coded.xml`), built by `scripts/p5_build_coded_instance.py`.
