---
status: proposed
date: 2026-10-21
---
# Call what a unit provides a capability, and name the key capabilities

## Context and Problem Statement

The manifest key was `provides`, beside `needs`, and an entry under it was
called a port. Two words for one thing, and neither worked as a noun in
prose: `needs` reads as a verb and as a plural noun, `provides` only as a
verb, so sentences fell back to "port", a word the manifest never used.
"Port" also carries two other meanings in this field, a network port and
the port of ports and adapters, and readers of the draft asked which one
was meant.

## Considered Options

- Keep `provides` and the term port
- Keep `provides` as the key and call an entry a capability
- Rename the key to `capabilities` and call an entry a capability
- Rename both sides: `capabilities` and `requirements`

## Decision Outcome

Chosen option: "rename the key to `capabilities` and call an entry a
capability", because one noun then names the thing in the manifest, in the
messages of the tool and in prose, and because `capabilities: ` beside
`needs: ` reads as two lists rather than as two verbs.

- `provides` is no longer a key. A manifest with it is an error (`M2`),
  because the standard has no aliases at 0.1.
- The term "port" is gone from the standard, the rules, the skill and the
  output of the tool. `## Provides` in a `README.md` at level `full` is now
  `## Capabilities` (`T5`).
- The command `unifold port` is now `unifold capability`; the MCP tool of
  that name and the JSON keys `port`, `root-port` and `root-ports-affected`
  follow.
- "Needs" stays. It is already a noun, and renaming it would touch every
  manifest for nothing.
- "Ports and adapters" keeps its name where the guide cites the pattern.

### Consequences

- Good: one word for one thing; prose no longer needs a term that the
  manifest does not have.
- Good: no collision with a network port in a project's own documents.
- Bad: every existing manifest, document and script of an adopter breaks.
  The draft is unpublished, so this is the last moment at which that is
  cheap.
- Bad: `capabilities` is longer than `provides` and wraps more prose lines.
