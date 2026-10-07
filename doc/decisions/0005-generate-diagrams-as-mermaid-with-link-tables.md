---
status: proposed
date: 2026-10-06
---
# Generate diagrams as Mermaid with text tables, and an explorer for clicking

## Context and Problem Statement

Readers want to move through the system visually, from the whole to the
parts, by clicking. Hand-drawn structure diagrams go stale. The result should
be readable without installing a viewer. Agents do not look at pictures.

What the hosts do, as far as it could be established in October 2026:

- GitHub and GitLab render Mermaid inside a frame from another address. A
  relative link in a box therefore leads nowhere. On GitHub, users report
  that full URLs work; on GitLab, links to GitLab pages are reported broken.
  Neither was tested live.
- SVG files embedded as images lose their links, and GitHub removes image
  maps from Markdown.
- Frames of opened-up units cannot carry links in Mermaid.

## Considered Options

- A modelling tool with its own viewer, for example LikeC4 or Structurizr
- Mermaid diagrams drawn by hand
- Mermaid diagrams generated from the manifests into Markdown files, with
  tables below, plus a generated HTML page for full interaction

## Decision Outcome

Chosen option: "generated Mermaid, tables, and an explorer".

- Each unit gets three diagrams: context, component and architecture. The
  names follow the C4 model loosely; the same three exist at every unit.
- Below each diagram are tables: the units shown, with links, and in the
  context file the resolved providers and users of the unit's ports. The
  tables work on every host and are what an agent reads.
- Whether boxes carry links is a setting of the project (`diagram-links`):
  none, relative, or full URLs from a base address.
- `unifold site` writes one HTML file in which every box, frame and table
  entry is clickable.

### Consequences

- Good: no viewer or server is needed to read the committed files.
- Good: a stale diagram is a checker warning (`G1`).
- Good: the same information exists as picture and as text.
- Bad: on a code host, clicking a box works only with full URLs, and those
  always lead to one branch.
- Bad: the explorer loads the Mermaid renderer from the network and is one
  more artefact to publish.
- Bad: Mermaid's automatic layout gets hard to read with many units. The
  generator merges parallel arrows and limits depth, not width.
- Bad: generated files are committed and produce diff noise. A unit's
  summary appears only in its own files and its parent's component diagram,
  to keep that noise local.
- Bad: `context.md` and `architecture.md` each name a hand-written file in
  `doc/` and a generated one in `doc/diagrams/`.
