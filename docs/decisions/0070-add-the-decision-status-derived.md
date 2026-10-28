---
status: proposed
date: 2026-10-27
---

# Add the decision status derived

## Context and Problem Statement

"Agents propose, humans accept" ([0007](0007-use-madr-with-numbers-local-to-the-unit.md)) leaves no room for a decision that nobody takes: a source document settles the matter. An agent that writes such a decision as `proposed` makes a person accept dozens of facts; an agent that writes nothing loses the trace to the passage.

## Considered Options

- Keep `proposed` for everything an agent writes
- A status `derived` with `derived-from` and a section `## Source says` that restates the passage

## Decision Outcome

Chosen option: "derived", because a decision that shows its passage can be checked against it, which is the review question, while a person still decides when the derived decisions become accepted.

- `derived` binds like `accepted` until a person accepts or supersedes it. Only a person sets `accepted`; agents set `derived` and `proposed`.
- The checker demands `derived-from` and `## Source says` on a derived decision, and does not warn when an active unit cites one.

### Consequences

- Good: the facts of the sources reach the decisions with their provenance, and a person accepts them in bulk.
- Bad: an agent can claim that a source says what it does not; the form makes the claim visible, and review reads a sample.
