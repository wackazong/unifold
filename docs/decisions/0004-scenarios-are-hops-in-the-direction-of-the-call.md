---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Scenarios are hops in the direction of the call

## Context and Problem Statement

A consistent map can still be wrong: a story of the system may need a connection nobody declared, or a connection may exist that no story uses. Hand-drawn sequence diagrams tell stories, but nothing checks them, and they go stale. How is a story written so that a tool can check it against the map and the contracts, and draw it?

## Decision

- A scenario is declared in a manifest under `scenarios`: `summary`, optional `source` and `given`, `hops` and `expect`. It is held by the lowest unit that contains every unit it names.
- A hop is `caller -> target.part`, with an optional note after `: `, written in the direction of its part: an operation from the consumer to the provider, an event from the provider to the consumer. The note and `given` are free text that no checker reads. A unit is named by its path from the holding unit, a capability or need of the holding unit bare; `target.capability.part` names the connection where two share the part.
- Every hop resolves to one connection of the map, its part is in that connection's contract, and the contract is one document at every level.
- The hops stand in the order in which a reader follows the story. A scenario stays at the level of the design: it does not model what happens inside a call, what runs at the same time, how often a step repeats, or the states of a connection; the contracts and their examples hold that detail. `child.scenario`, or `caller -> child.scenario` where the child's capability has several users, includes a scenario of a child, rewritten to the names of this level, so that a story is told once per level.
- A scenario of a child counts for the wiring lines of its parents: a hop at a capability or need of the child uses every line above that connects it. A parent repeats a child's story only where it adds a step of its own.

## Consequences

- Good: a story that needs a connection nobody declared is an error; a connection no story uses is a warning.
- Good: the sequence diagram is drawn from the hops, end to end across levels, and cannot disagree with the map.
- Good: a story is short enough to read in a review, and nobody has to model timing or states to write one.
- Bad: no checker finds a step that a protocol forbids or a result that contradicts an example; the tests of the units do.
- Bad: the direction of every hop must be right.
