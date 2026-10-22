---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Services learn about readings through events, not calls

## Context and Problem Statement

An accepted reading is needed in two places: in the history of its plant and in the evaluation that raises alerts. More uses may follow. The service that accepts an upload could hand the reading to each of them, or it could announce the reading and let the others listen. A client is online rarely, so an upload must succeed even when a later step is down.

## Considered Options

- The accepting service calls every service that needs the reading
- The accepting service writes readings to a shared table that the others poll
- The accepting service publishes one event per accepted reading on a durable bus; the others subscribe

## Decision Outcome

Chosen option: "publish events", because the upload then depends only on the event bus, and a new use of readings is a new subscriber that the accepting service does not know.

The decision covers readings. A service that needs the current state of something that changes rarely, such as the thresholds of a plant, asks for it with a call. A copy of that state kept current through further events is not built in version 1.

The event envelope and the topic names are defined in
[events](../references/events.md).

### Consequences

- Good: an upload succeeds while history or evaluation is down. They catch up from the bus.
- Good: the accepting service has no list of receivers.
- Good: a subscriber can be rebuilt by replaying the events the bus still holds.
- Bad: a query can lag behind an upload.
- Bad: the bus delivers at least once, so every subscriber must cope with repeats ([0004](0004-every-event-consumer-is-idempotent.md)).
- Bad: evaluation still depends on a call for thresholds and is delayed while the registry of plants is down.
