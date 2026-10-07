---
status: proposed
date: 2026-10-06
---
# Evaluation and notification are libraries beside one process

## Context and Problem Statement

`alerts` does three things: it judges readings against thresholds, it
tells owners about opened alerts, and it consumes events, stores alerts
and answers queries. The three change for different reasons. How are they
separated?

## Considered Options

- One undivided service
- Three services that talk through events or calls
- One process and two libraries with declared interfaces, built into one
  program

## Decision Outcome

Chosen option: "one process and two libraries", because it gives the
separation of concerns without a network between the parts, and it keeps
an alert and the state that led to it in one database transaction.

The two libraries have no state of their own and no access to the
database. What they must remember, they return to the process. They do
not know each other.

### Consequences

- Good: the judging rules are tested without database, event bus or
  clock.
- Good: a change of push provider touches one library.
- Good: one image to deploy, one subscription, one schema.
- Bad: the three parts are released together. A change of wording needs a
  release of the whole service.
- Bad: the libraries cannot be scaled apart from the process.
- Bad: nothing but review keeps the process from growing judging logic of
  its own.
