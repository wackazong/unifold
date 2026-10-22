---
status: proposed
date: 2026-10-07
---
# Let contract and verified-by point anywhere in the project

## Context and Problem Statement

`contract` and `verified-by` had to be paths inside the unit, and a port
of an `active` unit without `verified-by` gave a warning. Both trials on
real repositories hit this. The integration tests of a binary were in a
`tests/` folder above it, and the truthful path was an error; to pass, the
trial wrote a false one. Ten services shared one interface file in a
sibling folder, and the rule pushed each to point at its own copy, which
had already drifted. Eleven ports pointed at their own repository by URL
only to silence the warning. In the large example 1 of 32 ports had the
key at all.

## Considered Options

- Keep the rule and the warning
- Keep the rule, drop the warning
- Allow a URL or a path anywhere inside the project; the path must exist;
  a missing `verified-by` is never a finding

## Decision Outcome

Chosen option: "anywhere inside the project, never demanded", because a
pointer that must be present and must be local gets filled with whatever
passes, and a false pointer is worse than none.

- `status: active` no longer implies anything about `verified-by`.
- A port or need may also be written in the short form
  `name: summary text`.
- A difference in `kind` is reported only when both sides state a kind.

### Consequences

- Good: shared definitions and shared test folders are named where they
  are.
- Good: the first example of the standard gives no warning.
- Bad: a manifest may now name a file of a sibling, which the direction
  rules forbid for prose. A unit copied elsewhere loses these paths.
- Bad: nothing asks any more whether a port is tested. "Active" means
  only that the code exists.
- Bad: `verified-by` is still a path that nobody runs.
