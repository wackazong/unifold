# server

`server` is a running program that keeps alerts. It consumes the events of accepted readings, has each reading judged, stores the alerts that open and close, sees to it that every opened alert is notified, and answers queries about alerts over HTTP. It holds the state and decides nothing about readings itself.

## Why

Something must run: hold the subscription, own the database schema, listen on a network port. This unit is that program, and it is kept free of everything that is not running. It does not know what makes a reading alarming and not how an owner is reached. It asks for both through needs, each defined by a contract that the provider names too. It changes when what is stored about an alert, the order of the steps or the queries change.

What it does know is order and durability. It is the one place that decides what is written together and what may repeat: a reading's outcome, the evaluation state and the owed notification are stored in one transaction; the event is confirmed afterwards; notifying is a second step that can run again. Every guarantee about "once" rests on these few rules, so they are concentrated here instead of being spread over the logic.

The trade-off: `server` treats the evaluation state as a value it cannot read. It cannot repair or inspect it, only store it, hand it back or drop it.

## Capabilities

### `alerts-api`

- `server` opens no alert that `evaluation` did not decide. It closes one only on such a decision or by expiry.
- At most one alert is open per plant, quantity and bound, also when events repeat or several instances run.
- The first attempt to notify follows at once when an alert is stored.

## Needs

### `evaluation`

`server` waits up to 20 seconds for a result.

### `notification`

`server` waits up to 10 seconds for an outcome.

## Out of scope

- Comparing a value with a threshold.
- Looking up plants or thresholds.
- Wording a notification or talking to a push service.
- Changing an alert on request of a caller.

## Read next

1. [docs/references/processing.md](docs/references/processing.md): what is stored, the handling of an event, delivery of notifications, expiry
2. [evaluation](../docs/references/evaluation.md), [notification](../docs/references/notification.md), [reading events](../../../docs/references/reading-events.md): the contracts of its needs
3. [docs/explanation/context.md](docs/explanation/context.md): what the unit inherits
4. [Context diagram](docs/diagrams/context.md)
