---
status: proposed
date: 2026-10-06
---
# Every event consumer is idempotent

## Context and Problem Statement

The event bus delivers an event at least once. A subscriber that fails
after it has done its work and before it has confirmed the event receives
the event again. A publisher that fails after it has published and before
it has recorded that fact publishes again. Exactly-once processing across
the bus and a database needs distributed transactions, which the chosen
infrastructure does not offer.

## Considered Options

- Distributed transactions between the bus and the database
- At-most-once: confirm first, then process, and accept losses
- At-least-once delivery, with consumers whose result does not change when
  an event arrives again

## Decision Outcome

Chosen option: "at-least-once with idempotent consumers", because a lost
reading is a missed alert, while a repeated event is harmless when the
consumer is built for it.

Rules that follow:

- Every event has an `id` that is derived from what it describes, so a
  repeated event carries the same `id`
  ([events](../references/events.md)).
- A consumer makes its change and records the handled event in one
  transaction of its own database, or makes a change that is the same when
  applied twice.
- A consumer confirms an event only after its change is durable.
- An effect outside the databases, such as a notification, cannot take part
  in a transaction. The service that causes it finds its own way to make a
  repeat harmless and records that as a decision.

### Consequences

- Good: publishers and subscribers recover from a crash by doing the same
  thing again.
- Good: events can be replayed to rebuild or to repair a subscriber.
- Bad: every consumer carries the cost of recognising repeats.
- Bad: a consumer that forgets this rule works in tests and fails rarely in
  production. Each service tests the repeated event explicitly.
