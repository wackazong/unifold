---
status: proposed
date: 2026-10-27
---

# Declare scenarios with hops across levels, and generate their diagrams

## Context and Problem Statement

A map that is consistent can still be wrong: a story of the system may need a connection nobody declared, or a connection may exist that no story uses. Hand-drawn sequence diagrams in `runtime.md` show stories, but nothing checks them against the wiring, and they go stale.

## Considered Options

- Keep stories as prose and hand-drawn diagrams
- Scenarios in the manifest as hops, `caller -> target.part`, resolved against the wiring and the parts of the contracts, with generated sequence diagrams

## Decision Outcome

Chosen option: "scenarios in the manifest", because a hop is a checked declaration like a wiring line, and the picture then cannot disagree with the map.

- A scenario lives in the manifest of any unit, under `scenarios`, with `summary`, `hops`, `expect` and a free `source`.
- A hop names units by their path from the holding unit and a capability or need of the holding unit bare. It resolves by following needs up and capabilities down to one connection; the part is looked up in that connection's contract.
- A hop may cross levels; a story is drawn end to end. A scenario should be held by the lowest unit that contains every unit it names.
- An unresolved hop is an error. A wiring line that no scenario passing through the unit uses is a warning, silent where no scenario passes through.
- `docs/diagrams/scenario-<name>.md` is generated per scenario: a Mermaid sequence diagram and the hops as a table.

This amends the invariant "no hand-written file lists units, capabilities or connections": scenario hops are the one exception, and they are checked.

### Consequences

- Good: every edge of the map is justified by a story, and every story runs along declared edges.
- Good: a build process gets integration tests, one per scenario, from the manifests.
- Bad: a hop is a second place that names units; a rename changes it.
