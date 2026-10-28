---
status: proposed
date: 2026-10-27
---

# Define runtime.md as the behaviour of one unit over time

## Context and Problem Statement

`runtime.md` held "the scenarios that cross several parts": sequences, state machines, the order of a start. With scenarios in the manifest ([0069](0069-declare-scenarios-with-hops-across-levels.md)), the sequences across units have a checked home, and the file needs a sharper purpose.

## Considered Options

- Leave the definition as it is
- `runtime.md` says how one unit behaves while it runs: states and transitions, start and stop, timing, concurrency, limits, failure; stories across units are scenarios

## Decision Outcome

Chosen option: "one unit's behaviour over time", because what no scenario can tell is how a unit moves through its states, and that is what its code needs in a table.

### Consequences

- Good: state tables have one home; a hand-drawn sequence diagram of a story a scenario tells is a review finding.
- Bad: existing `runtime.md` files move their sequences into scenarios.
