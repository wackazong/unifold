---
status: proposed
date: 2026-10-06
---
# Use MADR with numbers local to the unit, proposed by agents and accepted by humans

## Context and Problem Statement

Decisions must be recorded where they apply, in a known format. Agents write
most of the text, but an agent must not be able to make a decision binding
by writing it down.

## Considered Options

- A project-wide decision log with one number sequence
- MADR files per unit, numbered within the unit
- Date-based file names to avoid number clashes

## Decision Outcome

Chosen option: "MADR per unit with local numbers", because MADR is widely
known, and a decision is identified by its unit and its number, so clashes
between units do not matter.

A decision written by an agent has status `proposed`. Only a human sets
`accepted`. An accepted decision is immutable apart from its status.

### Consequences

- Good: a unit carries its decisions when it is copied.
- Good: the status field tells an agent which decisions bind it.
- Bad: two branches that add a decision to the same unit pick the same
  number and must renumber on merge.
- Bad: there is no project-wide list. Each unit has a generated index of its
  own decisions only.
