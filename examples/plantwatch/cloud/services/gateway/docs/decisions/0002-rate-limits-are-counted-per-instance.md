---
status: proposed
date: 2026-10-06
---
# Rate limits are counted per instance, in memory

## Context and Problem Statement

The public contract limits requests per token and new owners per client
address. `gateway` runs in several instances. An exact limit needs a
counter that all instances share.

## Considered Options

- A shared counter in a store that all instances reach
- Counters in the memory of each instance
- No rate limit in `gateway`; rely on whatever stands in front of it

## Decision Outcome

Chosen option: "counters in memory", because the limits exist to stop a
client that has gone wrong, not to bill usage, and a shared store would
give `gateway` a state and a dependency that
[0001](0001-self-contained-signed-tokens.md) avoids.

### Consequences

- Good: no dependency; a limit check costs no network call.
- Bad: with n instances a client can reach n times the stated rate.
- Bad: counters are lost at a restart.
- Bad: the limit on new owners per client address is weak against a
  caller with many addresses. It bounds accidents, not attacks.
