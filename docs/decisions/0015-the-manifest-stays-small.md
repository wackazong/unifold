---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# The manifest stays small: no secret, plain not, inherited entries

## Context and Problem Statement

Every key of the manifest costs a rule, a test, a line in every unit and a concept for a newcomer. `secret` repeated what the first sentence of `## Why` says and required a decision per unit; `not` items that name a need repeated the wiring; a need that is only passed up repeated its provider's summary and contract at every level. Which keys earn their place?

## Decision

- The manifest has `responsibility`, `kind`, `runs-as`, `status`, `not`, `capabilities`, `needs`, `wiring`, `scenarios`, and at the root `unifold`, `name` and `ignore`. Keys that start with `x-` belong to the project.
- There is no `secret`: what a unit hides is the first sentence of its `## Why`, with the decision linked there.
- `not` is a list of one-line texts.
- An empty entry of `capabilities` or `needs` takes its summary and contract from the one wiring line that joins it to another entry.
- `optional` and `platform` on a need, and `parts` on a contract, stay as they are.

## Consequences

- Good: a manifest says each thing once, and a pass-through costs one empty line per level.
- Bad: a manifest that still has `secret` is an error until the sentence has moved to `## Why`.
