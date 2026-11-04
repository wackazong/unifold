---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Structure is generated; reasons are written

## Context and Problem Statement

Diagrams, indexes and pointer files are cheap to derive from declarations and expensive to keep correct by hand; reasons cannot be derived at all. Every generated file that is committed must be kept current and folded in reviews. Which files does a tool write, and what stays in a person's hands?

## Decision

- Generated, and committed: `docs/diagrams/component.md` of every unit with children; `docs/decisions/index.md` of every unit with decisions; the root `AGENTS.md`, with the documents and skills of the root and the unifold block with the index of units; and the skill stubs where their folders exist. Every generated file starts with the comment `<!-- unifold:generated`; a stale or missing one is an error.
- Drawn on demand, not committed: the sequence diagram of a scenario and the state diagram of a contract. `unifold scenario` prints a scenario with each included scenario as one step, and opens them with `--expand`; `unifold states` prints the states of a contract; each picture shows every row of the table beside it; the explorer shows both, with the context and architecture views of every unit.
- Written by people: `README.md`, with the why; the contracts; the explanation files; the decisions. No hand-written file lists units, capabilities or connections, except the hops of a scenario, which are checked declarations.
- A diagram is Markdown with a Mermaid chart and the same content as tables.

## Consequences

- Good: no picture can disagree with the manifests, and a repository holds few generated files.
- Good: a unit below the root has no generated file of its own; `unifold show` prints what one would hold.
- Bad: a reader on the code host sees a scenario only through the tool or the explorer.
