---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Examples have one shape and an id

## Context and Problem Statement

The examples of a contract are its first tests. With free-form tables, two people write different tests from one contract, and nobody can tell which test proves which example. How exact must examples be?

## Decision

- The examples table of an operation has the columns `Case | Input | Expected`, or `Case | Given | Input | Expected`; that of an event `Case | Action | Emitted`, or with `Given`. `Input` is a call in the notation of the signature; `Expected` a value, `ok`, or an error case that `Errors:` names. A case name is unique within the part.
- The id of an example is `<contract>#<part>/<case-slug>`, with the slug formed like the anchor of a heading.

## Consequences

- Good: two people write the same tests from a contract, and `unifold trace` finds the examples that no test names.
- Bad: existing tables are reshaped.
