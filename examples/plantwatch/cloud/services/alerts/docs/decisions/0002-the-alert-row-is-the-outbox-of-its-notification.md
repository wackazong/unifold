---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# The alert row is the outbox of its notification

## Context and Problem Statement

When a reading opens an alert, two things must happen: the alert is stored, and the owner is notified. The first is a database change, the second a call to an outside service. They cannot be made atomic. If the process stops between them, either an alert exists without notification or a notification without alert.

## Considered Options

- Notify while the event is handled, then store the alert
- Store the alert, then notify in the same handling step, and confirm the event only after both
- Store the alert together with the fact that a notification is owed; deliver owed notifications in a separate step that repeats until it succeeds

## Decision Outcome

Chosen option: "store the alert with an owed notification", because the decision to notify is then as durable as the alert itself, and a failing push service neither blocks the handling of events nor causes a reading to be judged again.

Every alert is stored with `notification` set to `pending`. A delivery step takes the pending alerts, has each one notified, and stores the outcome. It runs right after an alert is stored and again on a schedule, for at most 24 hours per alert.

Delivery can repeat. Whatever notifies must therefore make a second notification for the same alert harmless for the owner. How it does that is its own decision.

### Consequences

- Good: no notification is forgotten because of a crash.
- Good: a notification is never sent for an alert that was not stored.
- Good: the event stream does not wait for the push service.
- Bad: a notification can be sent more than once. The invariant "one notification per opened alert" holds as seen by the owner, not as counted at the push service.
- Bad: an alert can close before its notification leaves. The owner is then told about a plant that has already recovered.
