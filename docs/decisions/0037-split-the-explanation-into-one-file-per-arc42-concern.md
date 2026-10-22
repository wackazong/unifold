---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Split the explanation into one file per arc42 concern

## Context and Problem Statement

A unit had one explanation file, `docs/architecture.md`, "the long form of the why", with the sections Reasoning, Invariants and Behaviour. Goals, quality goals, deployment and risks had no place; the comparison with [arc42](https://arc42.org) on the front page conceded those sections. The examples improvised a "Where things run" table because nothing named it. One file for all of it would pass the line limit in the units that matter most, and a reader looking for the deployment would have to scan the whole why.

## Considered Options

- One `architecture.md` with fixed sections for every concern
- One file per concern in `docs/explanation/`, named after arc42
- A free folder of explanation topics without fixed names

## Decision Outcome

Chosen option: "one file per concern", because each file then holds one kind of content, stays short, and can be found by name in every unit, and because arc42 has already named the concerns.

| File | Content | arc42 |
|---|---|---|
| `context.md` | What the unit takes over from above, restated and stamped; the only file that links upward. | 2, 3 |
| `requirements.md` | What the unit must achieve, for whom, and its quality goals in order. | 1, 10 |
| `reasoning.md` | Why the unit is cut this way: the forces, the trade-offs, the ideas behind it. | 4 |
| `invariants.md` | What must always, or never, be true inside the unit. | 2, 8 |
| `runtime.md` | Sequences, state machines, the order of a start. | 6 |
| `deployment.md` | Where things run, instances, volumes, what survives a restart. | 7 |
| `risks.md` | Risks, known limits and technical debt, each with what would remove it. | 11 |

- Context and scope are not written a third time: `README.md` is the closed box and the generated context diagram shows the neighbours. `context.md` keeps its meaning.
- The long why is called `reasoning.md`, not "strategy" or "solution": the word names what the file holds, and the examples already used it as a heading.
- Building blocks are the manifests and the generated diagrams, decisions stay in `docs/decisions/`, the glossary in `docs/references/`.
- Topic files beside the fixed ones are allowed for explanation that users of the unit need, for example the wiring patterns of this standard.
- The names are fixed by the template and the generated `AGENTS.md`, not by a tool rule: a file of another name is still checked for links and length.
- For a project of one unit, `docs/explanation/` of the root is the architecture documentation of the project. The front page no longer says that a single package gets little value.

### Consequences

- Good: a unit can carry its whole architecture; nothing is left to a document outside the tree.
- Good: an agent loads the one file its task needs instead of the whole why.
- Bad: seven names to know. The template and the generated `AGENTS.md` list them.
- Bad: the examples and this repository split their `architecture.md` files by hand.
