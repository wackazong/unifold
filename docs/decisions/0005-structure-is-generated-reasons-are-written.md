---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Structure is generated; reasons are written

## Context and Problem Statement

Diagrams, indexes and pointer files are cheap to derive from declarations and expensive to keep correct by hand; reasons cannot be derived at all. Every generated file that is committed must be kept current and folded in reviews. Which files does a tool write, and what stays in a person's hands?

## Decision

- Generated, and committed: `docs/decisions/index.md` of every unit with decisions; the root `AGENTS.md`, with the documents and skills of the root and the unifold block with the index of units; and the skill stubs where their folders exist. Every generated file starts with the comment `<!-- unifold:generated`; a stale or missing one is an error.
- Drawn on demand, not committed: the component diagram of a unit with children, the sequence diagram of a scenario and the state diagram of a contract. The explorer, `unifold explore`, draws them all, with the context and architecture views of every unit and a folded view of a scenario, each include as one step; each picture has a table beside it with the same content.
- Written by people: `README.md`, with the why; the contracts; the explanation files; the decisions. No hand-written file lists units, capabilities or connections, except the hops of a scenario, which are checked declarations.

## Consequences

- Good: no picture can disagree with the manifests, and a repository holds few generated files.
- Good: a unit below the root has no generated `AGENTS.md` of its own; `unifold show` prints what one would hold.
- Bad: a reader on the code host sees no diagram: the structure, the scenarios and the states only in the explorer.
