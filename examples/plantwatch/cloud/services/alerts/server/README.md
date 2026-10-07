---
unit: server
summary: Process of the alerts service - consumes readings, stores alerts and answers queries
kind: app
status: planned
provides:
  alerts-api:
    kind: http
    summary: Open and past alerts per plant
needs:
  reading-events:
    kind: events
    summary: Accepted readings, in order per sensor
  evaluation:
    kind: library
    summary: Decides for a reading whether an alert opens, stays or closes
  notification:
    kind: library
    summary: Tells the owner about an opened alert, exactly once
  sql-db:
    kind: db
    summary: Relational database with transactions
  event-bus:
    kind: queue
    summary: Durable subscription with at-least-once delivery
---
# server

`server` is a running program that keeps alerts. It consumes the events
of accepted readings, has each reading judged, stores the alerts that open
and close, sees to it that every opened alert is notified, and answers
queries about alerts over HTTP. It holds the state and decides nothing
about readings itself.

## Provides

### `alerts-api`

The HTTP API for open and past alerts of an owner. Its operations and the
alert are defined above this unit and cited in
[doc/context.md](doc/context.md). `server` serves them with these
guarantees:

- Every alert it returns was decided by `evaluation` or closed by expiry.
  `server` never opens an alert on its own.
- At most one alert is open per plant, quantity and bound, also when
  events repeat or several instances run.
- An alert is stored within 30 seconds after its event arrives, and the
  first attempt to notify follows at once.
- The field `notification` tells the truth: `sent` only after
  `notification` reported success, `failed` only after it reported a
  final failure or 24 hours passed.
- An answer contains only alerts of the owner named in `X-Owner-Id`.

Limit: while `evaluation` cannot decide, events of the affected sensor
stick wait, and the answers show the state before them.

## Needs

### `reading-events`

Events of accepted readings, each with sensor id, sequence number, time,
a flag for an estimated time and the measured values by name. `server`
expects the events of one sensor stick in the order in which the readings
were accepted. It copes with repeats.

### `evaluation`

A function that takes one reading and the evaluation state that the same
function returned for the previous reading of the same sensor stick, or
nothing for the first. `server` expects it to return

- the plant the reading belongs to, with plant id, owner id and name, or
  the information that there is none,
- a list of changes: open or close an alert for a quantity and a bound,
  with the judged value, the threshold and, for a close, the reason,
- the new evaluation state, as a value that `server` stores and hands
  back unread,
- or the answer "cannot decide now", which leaves everything as it was.

`server` expects the function to change nothing outside its return value,
to return the same result for the same input, and never to ask for an
alert to be opened that is open according to the state it was given.

### `notification`

A function that takes one opened alert, with alert id, owner id, plant
id, plant name, quantity, bound, judged value, threshold and the time of
the reading, and tells the owner about it. `server` expects one of three
answers within 10 seconds: done, try again later, or failed for good.
`server` expects that calling the function again for the same alert does
not show the owner a second notification.

### `sql-db`

A relational database with a schema that only `server` uses. `server`
expects transactions, a unique index that holds only for rows
with a certain value (one open alert per plant, quantity and bound), and
row locks.

### `event-bus`

A broker with a durable subscription that all instances of `server`
share. `server` expects that events with the same key arrive in order
and go to one instance at a time, that an unconfirmed event is delivered
again, and that it continues after a restart where it stopped.

## Out of scope

- Comparing a value with a threshold.
- Looking up plants or thresholds.
- Wording a notification or talking to a push service.
- Changing an alert on request of a caller.

## More

- [AGENTS.md](AGENTS.md): why the process is separate from the logic it
  calls
- [doc/context.md](doc/context.md): the contract and the decisions that
  `server` inherits
- [Context diagram](doc/diagrams/context.md)
- References: [processing](doc/references/processing.md)
