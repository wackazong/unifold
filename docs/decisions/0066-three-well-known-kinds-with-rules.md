---
status: proposed
date: 2026-10-27
---

# Three well-known kinds with rules, and a kind on every composite

## Context and Problem Statement

[0058](0058-define-well-known-kinds.md) proposed closed lists of kinds and was rejected: no list fits every project. Yet a build process that cuts a system into units and tests each alone needs three distinctions a checker can hold: a pure calculation that can be tested without any fake, a unit that keeps state, and the one unit that talks to one external system.

## Considered Options

- Keep `kind` as free text without rules
- A closed list, as 0058 proposed
- Three well-known values with rules; any other value allowed and silent except for an info finding

## Decision Outcome

Chosen option: "three well-known values with rules", because the three carry checks that make a cut verifiable, and a project with its own vocabulary loses nothing.

| Kind | Meaning | Rule |
|---|---|---|
| `logic` | A pure calculation: no input or output, no memory between calls; time and randomness are parameters | Logic throughout: every child is `logic`, the final provider of every need is `logic`, no need reaches a need of the root |
| `stateful` | Keeps state, such as a session or a state machine | May need anything |
| `adapter` | The one unit that talks to one external system, a need of the root | The final provider of none of its needs is an `adapter` |

- A need of the root without `platform: true` is finally reached only by `adapter` units. `platform: true` marks a host service such as time or randomness, whose contract describes a controllable fake.
- A unit with children below the root states a `kind`: it says what the box is to its parent's wiring, where the rules apply to every line. A `logic` composite has only `logic` children; a composite that holds state anywhere is `stateful`; one that exists to wrap one external system is an `adapter`. The root has no kind.
- Any other value gives an info finding and no rule. The connection kinds on capabilities and needs do not change.

This supersedes 0058.

### Consequences

- Good: the cut of a system becomes checkable; a logic unit is known to be testable without a fake, an adapter is known to be the only place where an external protocol lives.
- Good: a project that uses other words is not nagged beyond an info line.
- Bad: three more warnings to understand, and a composite without a kind is now an error.
