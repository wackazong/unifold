---
unit: alerts
summary: Decides when a plant needs attention and notifies its owner once
kind: service
status: planned
provides:
  alerts-api:
    kind: http
    summary: Open and past alerts per plant
    contract: doc/references/alerts-api.md
needs:
  reading-events:
    kind: events
    summary: Accepted readings, to evaluate them against thresholds
  plants-api:
    kind: http
    summary: The thresholds of the plant a reading belongs to, and its owner
  push:
    kind: http
    summary: Delivers a notification to the phones of a user
  sql-db:
    kind: db
    summary: Relational database with transactions
  event-bus:
    kind: queue
    summary: Durable subscription with at-least-once delivery
wiring:
  alerts-api: server.alerts-api
  server.reading-events: reading-events
  server.evaluation: rules.evaluation
  server.notification: notifier.notification
  server.sql-db: sql-db
  server.event-bus: event-bus
  rules.thresholds: plants-api
  notifier.push: push
---
# alerts

`alerts` is the service that decides whether a plant needs attention. It
follows the stream of accepted readings, judges each reading against the
thresholds of its plant, opens an alert when a threshold is violated,
closes it when the plant has recovered, and has one notification sent to
the owner for every alert that opens. It answers questions about open and
past alerts.

## Provides

### `alerts-api`

An HTTP API for a caller that acts for an owner and says so in the header
`X-Owner-Id`: list the alerts of the owner, filtered by state and plant,
and read a single alert.

A caller can rely on this:

- At most one alert is open per plant, quantity and threshold. A plant
  that stays dry has one open alert, however many readings arrive.
- Every alert that opens leads to exactly one notification to the owner,
  handed to the push service. The alert says whether that has happened.
- An alert does not flap. It closes only when the judged value has
  recovered by a margin, or when its threshold is gone.
- An alert is visible, and its notification is handed over, within 30
  seconds after the event of the reading reaches `alerts`, while
  everything `alerts` needs is healthy.
- A reading is judged once, however often its event arrives.
- An owner sees only the alerts of that owner's plants.
- A closed alert is kept for 2 years.

Limits:

- `alerts` judges by the time of a reading. Readings that arrive late open
  and close alerts in the past; the owner is still notified.
- Light is judged over 24 hours, not per reading.
- A notification is handed to the push service. Whether a phone shows it
  is outside `alerts`.
- No operation changes an alert.

Example: `GET /v1/alerts?state=open` with `X-Owner-Id`.

```json
{"items": [{"id": "7d2c1c1e-52a0-4b0b-8a3e-1f2d3c4b5a69",
            "plant_id": "0b6f6f0e-2c1d-4f7a-9d42-6f1f0c8a7e11",
            "quantity": "soil_moisture", "bound": "min",
            "state": "open", "threshold": 30.0,
            "opened_at": "2026-10-05T14:15:00Z", "opened_value": 28.4,
            "notification": "sent"}]}
```

Contract: [alerts API](doc/references/alerts-api.md).

## Needs

### `reading-events`

A stream with one event per accepted reading. `alerts` expects each event
to carry the sensor id, the sequence number, the time of the reading, a
flag for an estimated time, and the measured values under the names
`soil_moisture`, `light` and `temperature`. It expects the events of one
sensor stick to arrive in the order in which the readings were accepted.
It copes with repeated events.

### `plants-api`

A lookup by sensor id that returns the plant to which the sensor stick is
attached, with plant id, owner id, name and thresholds, or says that the
sensor stick is attached to no plant. A threshold is a `min`, a `max` or
both per quantity. `alerts` expects the answer to show the current state
and to arrive within 5 seconds. While the lookup fails, `alerts` judges
nothing and catches up afterwards.

### `push`

A service that takes a notification addressed to an owner id and delivers
it to the phones registered for that owner. `alerts` expects

- a clear answer per request: taken, refused for good, or try again,
- a collapse identifier: two notifications with the same identifier
  appear on a phone as one.

Delivery may be late or fail without `alerts` learning of it.

### `sql-db`

A relational database with a schema that only `alerts` uses, and with
transactions that survive a restart once committed.

### `event-bus`

A broker with a durable subscription: `alerts` continues where it stopped
after a restart, an event it has not confirmed is delivered again, and
events with the same key arrive in order, also when several instances of
`alerts` share the subscription.

## Out of scope

- Storing thresholds or plants. `alerts` asks for them.
- Storing readings or history.
- Reminders. An alert that stays open sends nothing more.
- Alerts about missing data, such as a sensor stick that has gone silent.
- Acknowledging or closing an alert by hand.
- Choosing which phones get a notification.

## More

- [AGENTS.md](AGENTS.md): why the service is cut into a process and two
  libraries
- [doc/context.md](doc/context.md): what the unit inherits
- [doc/architecture.md](doc/architecture.md): invariants, the life of an
  alert, the handling of one reading
- [Context diagram](doc/diagrams/context.md),
  [component diagram](doc/diagrams/component.md),
  [architecture diagram](doc/diagrams/architecture.md)
- [Decisions](doc/decisions/index.md)
- References: [alerts API](doc/references/alerts-api.md)
