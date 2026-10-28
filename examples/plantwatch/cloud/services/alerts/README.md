# alerts

`alerts` is the service that decides whether a plant needs attention. It follows the stream of accepted readings, judges each reading against the thresholds of its plant, opens an alert when a threshold is violated, closes it when the plant has recovered, and has one notification sent to the owner for every alert that opens. It answers questions about open and past alerts.

## Why

The promise of the product is "one notification when a plant needs attention". This unit owns that promise. It is the only place that compares a reading with a threshold and the only place that talks to the push service. It changes when that promise changes: what counts as needing attention, and how and when the owner is told.

Inside, the logic of judging, the technologies behind a network and the plumbing with transactions change for different reasons, so each lives in a child of its own. The logic is tested with tables of readings and names no technology ([0003](docs/decisions/0003-thresholds-reach-the-judging-logic-through-an-adapter.md)). All children are built into one program ([0001](docs/decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md)), so that an alert and what led to it are stored in one transaction ([0002](docs/decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md)).

What must stay true: an alert opens once, and an opened alert leads to one notification, although events and calls can repeat.

## Capabilities

### `alerts-api`

- Every call of the push service for the same alert uses the same collapse identifier, so that a repetition replaces the earlier notification on a phone.
- A sensor stick that was moved to another plant takes up to 60 seconds to apply, like a changed threshold.

## Needs

### `plants-api`

`alerts` waits up to 5 seconds for a lookup and then treats the registry as unavailable.

## Read next

1. [docs/explanation/invariants.md](docs/explanation/invariants.md), [runtime.md](docs/explanation/runtime.md): invariants, the life of an alert, the handling of one reading
2. [alerts API](../../docs/references/alerts-api.md): how the API is served
3. [docs/references/glossary.md](docs/references/glossary.md): the terms of this unit
4. [docs/explanation/context.md](docs/explanation/context.md): what the unit inherits
5. [Context diagram](docs/diagrams/context.md), [component diagram](docs/diagrams/component.md), [decisions](docs/decisions/index.md)
