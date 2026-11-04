---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# From design to code: brief, trace and tests named after examples

## Context and Problem Statement

A design in unifold is complete when every connection has a contract with examples and every story is a scenario, but nothing links any of it to code or tests: a contract can drift from its implementation and a clean check says nothing about it. "Implement this unit" must be a defined task, for a person and for an agent. How does an implementer go from the design to code, and how is drift seen?

## Decision

- `unifold brief UNIT` prints what an implementer needs: the parts of each capability with signature, `Pre:`, `Result:`, `Errors:` and examples with ids; each need with its parts and the `## Fake` of its contract; the states; the scenarios through the unit; the constants; the context items.
- A test that proves an example names the example's id in its name or in a comment. `unifold trace UNIT` searches the files below the unit, outside `docs/`, for the ids of the examples of the contracts of its capabilities, and reports the examples that no test names (`X1`, info) and the ids that no example has (`X2`, warning). It parses no code, so it works for every language.
- The procedure "implement a unit" is: brief, one test per example first, fakes for the needs as the contracts say, code until the tests pass, trace until nothing is left, then `status: active`.
- The tool still reads no code; keeping the map and the code in step is part of every change and its review.

## Consequences

- Good: the path from a contract to a test is a name, and drift between a contract and its tests shows in one command.
- Bad: a test that proves an example without naming it is invisible to `trace`.
