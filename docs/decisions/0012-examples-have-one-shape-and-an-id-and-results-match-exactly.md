---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Examples have one shape and an id; results match exactly

## Context and Problem Statement

The examples of a contract are its first tests, and a scenario's results are what an implementer builds to. With free-form tables and loosely matched results, two people write different tests from one contract, a typo in an error name counts as a success, and a scenario can contradict the contract it uses without anyone noticing. How exact must examples and results be?

## Decision

- The examples table of a command, query or callback has the columns `Case | Input | Expected`, or `Case | Given | Input | Expected`; that of an event `Case | Action | Emitted`, or with `Given`. `Input` is a call in the notation of the signature; `Expected` a value, `ok`, or an error case that `Errors:` names. A case name is unique within the part.
- The id of an example is `<contract>#<part>/<case-slug>`, with the slug formed like the anchor of a heading.
- A hop's result is `ok`, an error case spelled exactly as `Errors:` names it (case-sensitive, constants excluded), a value, or `= <case>`. A result spelled like an error case, but not exactly, is reported. A hop whose input is an example's input must have that example's result; `= <case>` must name an example that exists.

## Consequences

- Good: two people write the same tests from a contract, and a scenario that contradicts an example fails the check.
- Bad: existing tables are reshaped, and a scenario's literal results must match the contract to the letter.
