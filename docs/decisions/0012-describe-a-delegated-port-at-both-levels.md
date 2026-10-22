---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Describe a delegated port at both levels and keep its contract in one place

## Context and Problem Statement

When a unit delegates a provided port to a child, the port is declared in two manifests. Writing the example showed three rules pulling apart: a `README.md` must be understandable alone, a parent must not restate a child, and every fact has one home. All three agents that wrote the example reported this.

## Considered Options

- Only the child describes the port; the parent links to it
- Only the parent describes the port; the child cites it as context
- Both describe it at their own level; the contract has one home, chosen by where the port is fully defined

## Decision Outcome

Chosen option: "both, with one home for the contract", because a reader of the parent must learn what the unit guarantees without opening the child, and a reader of the child must not need the parent.

The contract lives in the parent if the port combines several children or the parent adds to it; otherwise in the child. This is listed as an allowed repetition.

### Consequences

- Good: both `README.md` files stay usable alone.
- Good: the precise definition exists once.
- Bad: two prose descriptions of one port can drift. Review rule `C13` compares them only indirectly.
- Bad: whether the parent "adds something" is a judgement.

The same trial led to review rule `C13` (every need matches its provider), to the rule that invariants children must obey are decisions or references, and to the workflow step "Match".
