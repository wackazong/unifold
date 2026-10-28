---
status: proposed
date: 2026-10-27
---

# Remove verified-by

## Context and Problem Statement

`verified-by` pointed at the tests of a capability. [0030](0030-let-contract-and-verified-by-point-anywhere-in-the-project.md) already made it optional and noted that nothing runs it. In the examples it was set on a few entries and told a reader nothing that the tests' folder did not.

## Considered Options

- Keep it as an optional pointer
- Remove it

## Decision Outcome

Chosen option: "remove it", because a pointer that nothing checks invites false confidence, and the examples of a contract are now the tests that matter.

### Consequences

- Good: one key less, and no false promise.
- Bad: a manifest that still has it is an error until the line is deleted.
