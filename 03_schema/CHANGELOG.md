# Schema changelog

Versioning follows ADR-001: patch = documentation only; minor = new optional elements, attributes, or enumeration values (every existing instance still validates); major = anything that can invalidate an instance, with a new namespace.

## dms 1.1.0 — 2026-10-29 (P4.S01)
Additive; namespace unchanged (`…/dms/v1`). Gate module unchanged (gates 1.0.0).
- `Variable/@reviewed` — approved INFERRED definitions carry `confirmedByScott` (ADR-008), now available for variables after Scott's review in P4.S01.
- `Variable/@role` (`headline` | `secondary`) — which summary measure to report: for the frequency scale, "Frequently" is the headline and "Occasionally + Frequently" the secondary measure (Scott, P4.S01).
- `TextAnswer/@keyProvenance`, `@keyNote` — mark an answer whose respondent key was assigned rather than read from the source (`01_instrument_reconstruction/respid_corrections.csv`; one case: SRC-003 Q21!A6 → 112).

## dms 1.0.0 / gates 1.0.0 — 2026-10-29 (P3)
First release. Tag `schema-v1.0.0`.
