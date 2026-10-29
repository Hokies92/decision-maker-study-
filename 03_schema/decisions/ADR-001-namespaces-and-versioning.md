# ADR-001 — Namespaces and versioning

**Status:** proposed (P3.S01) · **Provenance:** INFERRED (Claude), requirement from GOVERNANCE §5 P3

## Context
GOVERNANCE requires the namespace to carry the major version (`…/dms/v1`). The gates must also serve other research and work (Scott, D3-1), so they cannot be tied to this survey's version.

## Options
1. One namespace for everything. Simple, but any change to the survey would force a new gate version, and outside work would have to import the whole study schema.
2. **Two namespaces: the study and the gate model, versioned separately.**
3. A namespace per section (instrument, population, results …). More flexible than needed; more imports for every user.

## Decision
Option 2.

| Vocabulary | Namespace | File |
|---|---|---|
| Study | `https://growthenablement.com/ns/dms/v1` | `decision-maker-study.xsd` |
| Gate model | `https://growthenablement.com/ns/gates/v1` | `gates.xsd` (imported by the study schema) |

Namespace URIs are names, not web addresses; they need not resolve. They use Scott's domain so that they stay stable if the repository moves. Scott can replace the domain before `schema-v1.0.0` is tagged; after that, a change is a major version.

Versioning (semantic):
- **Patch** (1.0.x): documentation or annotation changes only.
- **Minor** (1.x.0): new optional elements or attributes, new enumeration values. Every existing instance still validates.
- **Major** (2.0.0): anything that can make an existing instance invalid. The namespace changes to `/v2`.

Each schema states its version in `xs:schema/@version`; each instance states the version it was written for in a `schemaVersion` attribute on the root.

## Consequences
- Outside work can use the gates by importing `gates.xsd` alone.
- Phase 5 codes, the lexicon, or computed values can arrive as minor versions without breaking v1 instances.
- Scott tags `schema-v1.0.0` at the Phase 3 gate (GOVERNANCE §5).
