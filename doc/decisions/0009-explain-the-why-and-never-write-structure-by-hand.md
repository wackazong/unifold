---
status: proposed
date: 2026-10-06
---
# Explain the why in AGENTS.md and never write structure by hand

## Context and Problem Statement

`AGENTS.md` is the file agents load first. It is tempting to fill it with an
overview of folders, children and dependencies. Such overviews duplicate the
manifests, go stale, and a controlled study of agent context files found
that structural overviews did not help agents find relevant files while
raising cost
([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988)).

## Considered Options

- `AGENTS.md` contains a catalogue of child units and their ports
- `AGENTS.md` contains the reasons for the composition, pointers and the
  skills table; structure appears only in manifests and generated diagrams

## Decision Outcome

Chosen option: "reasons and pointers only", because reasons are the one
thing that cannot be derived, and structure is the one thing that can.

`doc/architecture.md` is the long form of the why. It follows the same rule
and must not restate the structure of interfaces.

### Consequences

- Good: no hand-written text has to change when the wiring changes.
- Good: `AGENTS.md` stays short.
- Bad: `AGENTS.md` and `doc/architecture.md` overlap in purpose. The rule
  "about 15 lines, then overflow" is a matter of judgement.
- Bad: an agent must open a second file, the manifest or a diagram, to see
  the structure.
- Bad: an agent that wants the structure as text finds it in the generated
  `doc/diagrams/context.md` or through `youmedoc show`, not in `AGENTS.md`.
- A short `## Commands` section is allowed, because agents and people expect
  build and test commands in this file. Longer procedures are skills.
