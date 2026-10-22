---
status: proposed
date: 2026-10-07
---
# License the standard under MIT or Apache-2.0

## Context and Problem Statement

The standard is copied into every project that uses it: text, skills and
tool. Without a licence nobody may do that. The licence must allow copying
into projects of any kind, including closed ones.

## Considered Options

- MIT only
- Apache-2.0 only
- MIT or Apache-2.0, at the user's option
- A documentation licence such as CC BY 4.0 for the text, a software licence
  for the tool

## Decision Outcome

Chosen option: "MIT or Apache-2.0", because the dual licence is well known,
permissive, compatible with most projects, and one licence for text and tool
keeps the copied folder simple.

Both licence texts are part of the copied folder. The templates and the
output of the generator may be used without attribution, so that the
documents of an adopting project carry no obligation.

### Consequences

- Good: a project of any licence can carry the copy.
- Bad: a software licence is an unusual choice for a specification text. A
  documentation licence would fit the prose better; it would also put two
  regimes into one copied folder.
