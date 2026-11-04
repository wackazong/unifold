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
- A hop is `caller -> target.part(input): result`, written in the direction of the call: a command or query from the consumer to the provider, an event or callback from the provider to the consumer. The result is text; a command or query has one, an event or callback may leave it out. A unit is named by its path from the holding unit, a capability or need of the holding unit bare; `target.capability.part` names the connection where two share the part.
- Every hop resolves to one connection of the map, its part is in that connection's contract, and the contract is one document at every level.
- The hops stand in the order in which the calls start; the hops that follow a command or query and whose caller is its target happen inside it. An event is asynchronous: when a unit raises one, the call it was handling has returned, and so has every call that waited for it and does nothing more afterwards, while a unit that handles an event keeps running; an event from outside the open calls arrives during them; a callback runs inside the call that triggers it. `parallel` holds lists of hops that run at the same time; `repeat` holds hops that run until a result or a number of times; `child.scenario`, or `caller -> child.scenario` where the child's capability has several users, includes a scenario of a child, rewritten to the names of this level, so that a story is told once per level.
- Every scenario follows the `## States` of the contracts it uses: `given` sets the state a connection starts in, every hop must be allowed in the current state with its result, and the connection moves to the next state. The hops of a `repeat` are followed twice, so that a round can follow a round.
- A scenario of a child counts for the wiring lines of its parents: a hop at a capability or need of the child uses every line above that connects it. A parent repeats a child's story only where it adds a step of its own.
- A hop agrees with the examples of its part: a result `= <case>` takes an example's input and expected result, and a hop whose input is an example's input has that example's result.

## Consequences

- Good: a story that needs a connection nobody declared is an error; a connection no story uses is a warning; a step that the protocol forbids is an error; a step that contradicts an example is an error.
- Good: the sequence diagram is drawn from the hops, end to end across levels, and cannot disagree with the map.
- Bad: a story is written as data, not prose, and the direction of every hop must be right.
