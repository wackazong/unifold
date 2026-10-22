# alerts

`alerts` is the service that decides whether a plant needs attention. It follows the stream of accepted readings, judges each reading against the thresholds of its plant, opens an alert when a threshold is violated, closes it when the plant has recovered, and has one notification sent to the owner for every alert that opens. It answers questions about open and past alerts.

## Why

The promise of the product is "one notification when a plant needs attention". This unit owns that promise. It is the only place that compares a reading with a threshold and the only place that talks to the push service. It changes when that promise changes: what counts as needing attention, and how and when the owner is told.

Inside, four things change for different reasons, and each is a child. The rules by which a reading is judged are pure logic, tested with tables of readings ([rules](rules/README.md)). The registry of plants and the push service are technologies behind a network; each has an adapter, so that the logic names neither
([0003](docs/decisions/0003-thresholds-reach-the-judging-logic-through-an-adapter.md)).
Consuming events, storing alerts and answering queries is plumbing with transactions ([server](server/README.md)). All are built into one program
([0001](docs/decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md)),
so that an alert and what led to it are stored in one transaction
([0002](docs/decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md)).

What must stay true: an alert opens once, and an opened alert leads to one notification, although events and calls can repeat.

## Capabilities

### `alerts-api`

An HTTP API for a caller that acts for an owner and says so in the header `X-Owner-Id`: list the alerts of the owner, filtered by state and plant, and read a single alert.

A caller can rely on this:

- At most one alert is open per plant, quantity and threshold. A plant that stays dry has one open alert, however many readings arrive.
- Every alert that opens leads to one notification that the owner sees. It is handed to the push service at least once, always under the same collapse identifier, so that a repetition replaces the earlier one. The alert says whether it has been handed on.
- An alert does not flap. It never closes with `recovered` while the judged value is beyond its threshold, only when the value is back on the good side by a margin, and at the latest when it is back by 10 percent of the range of its quantity.
- An alert is visible, and its notification is handed over, within 30 seconds after the event of the reading reaches `alerts`, while everything `alerts` needs is healthy.
- A reading is judged once. A repeated event changes no alert and causes no notification.
- An owner sees only the alerts of that owner's plants. An alert of another owner answers `404`.
- A closed alert is kept for 2 years.

Limits:

- `alerts` judges by the time of a reading. Readings that arrive late open and close alerts in the past; the owner is still notified.
- Light is judged over 24 hours, not per reading.
- A notification is handed to the push service. Whether a phone shows it is outside `alerts`.
- A changed threshold, and a sensor stick that was moved to another plant, take up to 60 seconds to apply.
- While the lookup of plants fails, no reading is judged. `alerts` catches up in order afterwards.
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

Contract: [alerts API](../../docs/references/alerts-api.md).

## Needs

### `reading-events`

A stream with one event per accepted reading, keyed by sensor id. `alerts` expects each event to carry the sensor id, the sequence number, the time of the reading, a flag for an estimated time, and the measured values under the names `soil_moisture`, `light` and `temperature`. It expects

- the events of one sensor stick in the order in which the readings were accepted,
- every accepted reading at least once, available for at least 7 days.

It copes with repeated events.

### `plants-api`

An HTTP service inside the private network with a lookup by sensor id. It returns the plant to which the sensor stick is attached, with plant id, owner id, name and thresholds, or says with an answer of its own that the sensor stick is attached to no plant. A threshold is a `min`, a `max` or both per quantity. `alerts` expects that the lookup needs no owner, can be repeated, shows the current state and answers within 5 seconds, or with the status `503` when it cannot.

### `push`

An HTTP service that takes one notification per request, addressed to an owner id, and delivers it to the phones registered for that owner. `alerts` expects that it accepts

- a title of up to 60 characters, a body of up to 120 characters and five short data fields,
- a collapse identifier: two notifications with the same identifier appear on a phone as one,
- a time to live of 24 hours, after which it stops trying to deliver,

and that it answers every request clearly: taken, refused for good, or failed for now. Delivery may be late or fail without `alerts` learning of it.

### `sql-db`

A relational database with a schema that only `alerts` uses. `alerts` expects transactions that survive a restart once committed, row locks, and a unique index that is limited to rows with a certain value.

### `event-bus`

A broker with a durable subscription: `alerts` continues where it stopped after a restart, an event it has not confirmed is delivered again, and events with the same key arrive in order and at one instance at a time, also when several instances of `alerts` share the subscription.

## Out of scope

- Storing thresholds or plants. `alerts` asks for them.
- Storing readings or history.
- Reminders. An alert that stays open sends nothing more.
- Alerts about missing data, such as a sensor stick that has gone silent.
- Acknowledging or closing an alert by hand.
- Choosing which phones get a notification.

## Read next

1. [docs/explanation/invariants.md](docs/explanation/invariants.md),
   [runtime.md](docs/explanation/runtime.md): invariants, the life of an alert, the handling of one reading
2. [docs/references/alerts-api.md](../../docs/references/alerts-api.md): how the API is served
3. [docs/references/glossary.md](docs/references/glossary.md): the terms of this unit
4. [docs/explanation/context.md](docs/explanation/context.md): what the unit inherits
5. [Context diagram](docs/diagrams/context.md),
   [component diagram](docs/diagrams/component.md),
   [decisions](docs/decisions/index.md)
