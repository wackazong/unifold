---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# One contract per connection, where the wiring is

## Context and Problem Statement

Two units that are connected must agree on what travels between them. A protocol name such as `http` says how they talk, not what they say, and a schema file alone says nothing about behaviour, errors or tests. Where is a connection defined, and what must the definition hold so that both sides can be built and tested from it?

## Decision

- Every connection has one contract: a Markdown document in `docs/references/` of the unit that wires the connection, or of a unit above it. Both sides name the same document in `contract`; a side that uses only some parts lists them under `parts`.
- A contract has a header (`Notation:`, `Sources:`, and optionally `Binding:`, `Carried by:`, `Version:`), `## Use`, `## States` where the connection has state, `## Qualities` where it promises more than its parts, `## Parts` and `## Fake`.
- A part is a command, query, event, callback or type, with a signature in a fenced block. A command, query or callback has `Pre:`, `Result:`, `Errors:` and examples; an event has `When:` and `Delivery:`.
- `## States` is a table `State | Part | Result | Next` with a start state: the states a consumer can see or must respect. Where it exists, `## Use` and `Pre:` do not repeat the order of calls.
- `## Fake` says what stands in for the contract in the tests of its consumers: a replay of the examples, a simplified behaviour with its faults, or the real implementation.
- A contract that outgrows the word limit becomes a folder with `index.md` and one file per part.

## Consequences

- Good: a provider knows what to guarantee, a consumer knows what to rely on and what to test against, and a reviewer has one place where a change shows.
- Good: the checker verifies that both sides name the same document, that the parts exist, and that the table of states is sound.
- Bad: a connection costs a document, even a small one.
