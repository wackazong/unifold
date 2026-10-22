---
status: superseded by 0024
date: 2026-10-07
---

# Allow one wiring line for several children, but not for deeper levels

## Context and Problem Statement

Two reviewers measured the cost of explicit wiring. In the example, 21 of 63 lines only pass a need up. A helper used by five units at different depths took 8 need declarations and 8 wiring lines. Several siblings that need the same provider each take a line.

## Considered Options

- Keep one line per need
- A line `"*.need": provider` for all direct children that have the need
- A line that reaches all descendants, so that units in between declare nothing

## Decision Outcome

Chosen option: "a star for direct children", because it removes the repetition among siblings without hiding anything.

The line for all descendants was rejected: a unit in between would depend on something its manifest does not show. Its `README.md` would no longer describe it as a closed box, and a copy of the folder would hide a dependency. What every unit needs, such as logging, is not a need at all (chapter `manifest.md` of that draft).

### Consequences

- Good: fewer lines; the common case "all services use the bus" is one line.
- Bad: one more form to learn, and the key must be quoted in YAML.
- Bad: a need used deep in the tree still costs a declaration per level.
