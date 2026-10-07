---
status: proposed
date: 2026-10-07
---
# Build ports and adapters, DDD, SOLID and test-first design into the rules

## Context and Problem Statement

A review by four roles found that the first draft described boxes and arrows
and left the established design principles to chance: a need could not carry
the interface its owner expects, tests had no place, cycles between siblings
passed unnoticed, one glossary was assumed for a whole project, and a warning
about differing kinds invited the wrong fix.

## Considered Options

- Leave design guidance out; the standard is about documents only
- Name the principles in a chapter without changing rules
- Map each principle to a field, a tool rule or a review rule

## Decision Outcome

Chosen option: "map each principle to a rule", because a documentation
standard that fixes where interfaces are written down already decides where
boundaries go, and should decide well.

- Ports and adapters: a need may have a `contract` owned by the unit that
  has the need; differing kinds call for an adapter unit; alternatives are
  named providers of one need.
- DDD: a unit may have its own glossary; the nearest glossary wins.
- SOLID: review rule `C14` for one responsibility and narrow ports; `C13`
  for substitutable alternatives; tool rule `W7` for cycles.
- Test-first: guarantees are checkable, contracts contain examples, a
  provided port names what verifies it (`verified-by`), and `active` means
  verified (`M8`, `C15`).

### Consequences

- Good: the manifest can express the consumer-owned interface.
- Good: "done" has a meaning that a tool can partly check.
- Bad: two more manifest fields and three more rules to learn.
- Bad: `M8` warns for every active unit of an existing repository until its
  tests are named.
- Not adopted: relationship types on wiring lines, a marker for core units
  with a rule on their needs, and wiring that reaches all descendants for
  cross-cutting needs. Each adds vocabulary; they wait for evidence from use.
