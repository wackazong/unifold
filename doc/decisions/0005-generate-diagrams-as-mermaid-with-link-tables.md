---
status: proposed
date: 2026-10-06
---
# Generate diagrams as Mermaid with link tables

## Context and Problem Statement

Readers want to move through the system visually, from the whole to the
parts. Hand-drawn structure diagrams go stale. The result should be readable
without installing a viewer.

## Considered Options

- A modelling tool with its own viewer, for example LikeC4 or Structurizr
- Mermaid diagrams drawn by hand
- Mermaid diagrams generated from the manifests into Markdown files

## Decision Outcome

Chosen option: "generated Mermaid in Markdown", because code hosting
platforms and editors render it in place, and generation keeps it equal to
the manifests.

Each unit gets three diagrams: context, component and architecture. The names
follow the C4 model loosely; the levels are not fixed, the same three exist
at every unit.

Drill-down uses a table of links below each diagram. Mermaid click targets
are added too, but not every renderer honours them.

### Consequences

- Good: no viewer, no server, no separate model file.
- Good: a stale diagram is a checker warning (`G1`).
- Bad: Mermaid's automatic layout gets hard to read with many units. The
  generator limits depth, not width.
- Bad: no interactive zoom. Moving between levels means following a link.
- Bad: generated files are committed and produce diff noise.
- Bad: `doc/architecture.md` (hand-written) and
  `doc/diagrams/architecture.md` (generated) share a file name.
