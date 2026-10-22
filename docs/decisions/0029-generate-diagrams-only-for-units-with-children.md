---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Generate diagrams only for units with children

## Context and Problem Statement

[0005](0005-generate-diagrams-as-mermaid-with-link-tables.md) generated up to three files for every unit. On a Cargo workspace of 12 units this gave 14 generated files and a new `docs/` folder in every crate, which was then published with the crate. For a flat tree the architecture diagram equalled the component diagram. The context diagram of a unit drew every sibling, connected or not. Generated files could exceed the line limit, which nobody could fix, and links to folders with spaces were dead.

## Considered Options

- Keep three files per unit
- One file per unit with children, nothing else
- A root key `diagrams` with `parents` (default), `all` and `none`

## Decision Outcome

Chosen option: "a key, default `parents`", because a leaf has nothing to show that `unifold show` does not print, while a design-phase project wants a page per unit.

- `parents`: `component.md` for units with children; `context.md` if such a unit has a parent; `architecture.md` only where children have children.
- `all` adds `context.md` for leaves. `none` writes no diagram.
- A context diagram shows only the siblings the unit is connected to.
- Generated links are URL-encoded, and generated files have no line limit.
- The generated marker counts only at a path the generator writes.
- `check --fix` writes what the generator would write.

This amends 0005; Mermaid with tables and the explorer stay.

### Consequences

- Good: a leaf package gets one file, its manifest.
- Good: no generated file can fail a rule that only a person can fix.
- Bad: a leaf has no page that shows its neighbours on a code host; a reader needs the tool or the parent's diagram.
- Bad: the root has no context diagram by default.
- Bad: one more key in the root manifest, and diagrams differ between projects.
