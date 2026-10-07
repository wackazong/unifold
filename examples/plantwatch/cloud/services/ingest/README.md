# ingest

`ingest` is the service that takes readings in. It receives a batch of
readings of one sensor stick, checks every reading, recognises the ones it
has accepted before, and announces each new one as an event. It stores no
readings itself and does nothing with their content beyond checking it.

## Provides

### `ingest-api`

One HTTP operation: upload a batch of readings of one sensor stick. The
response has one result per reading: `new`, `duplicate` or `rejected` with
a reason.

A caller can rely on this:

- A reading reported as `new` or `duplicate` is on the event bus before
  the response is sent. The caller may forget it.
- The same batch may be sent any number of times. Readings accepted
  earlier are reported as `duplicate` and are not announced again.
- A rejected reading does not affect the other readings of the batch.
- When `ingest` cannot store events it answers `503` and reports no
  reading as accepted. Sending the batch again later is always correct.
- `ingest` answers every request within 4 seconds, a batch of 500 readings
  within 2 seconds while the event bus is healthy.
- `ingest` depends on nothing but the event bus. It answers uploads with
  `200` while no subscriber of its events is running.

Limits:

- At most 500 readings and 1 MB per batch.
- `ingest` recognises a duplicate by sensor id and sequence number alone.
  It does not compare contents.
- `ingest` does not know plants or owners. It accepts readings of any
  sensor id.
- For a sensor stick with more than 1 000 gaps in its sequence numbers, a
  reading in an old gap can be reported as `duplicate` without having been
  accepted.

Example response:

```json
{"results": [{"sequence_number": 4711, "status": "new"},
             {"sequence_number": 4712, "status": "rejected",
              "code": "value_out_of_range",
              "message": "soil moisture 104.2 is outside 0 to 100"}]}
```

Contract: [ingest API](doc/references/ingest-api.md).

### `reading-events`

A stream with one event of the type `reading.accepted` for every reading
that `ingest-api` reported as `new`. An event carries the sensor id, the
sequence number, the time, the measured values under fixed names, and the
reading as it was uploaded. A subscriber does not need to know the format
in which readings are uploaded.

A subscriber can rely on this:

- **Key.** The key of an event is the sensor id.
- **Delivery.** Every accepted reading appears on the stream at least
  once and stays there for 7 days. A subscriber that was away for less
  than 7 days misses nothing.
- **Order.** Events of one sensor stick arrive in the order in which
  `ingest` accepted the readings. Within one batch that is the ascending
  order of sequence numbers.
- Every value in an event has passed validation: it lies within the range
  of its quantity.
- The `id` of an event is derived from sensor id and sequence number.

Limits:

- An event can arrive more than once, with the same `id`. This happens
  after a failure and when the same reading is uploaded at two places at
  the same moment.
- The order of events is the order of acceptance, not the order of
  sequence numbers or times. A batch that is uploaded late produces events
  for old readings after events for newer ones.

Example: the accepted reading 4711 of the sensor stick `00a1b2c3d4e5f607`
becomes one event with the `id` `00a1b2c3d4e5f607-4711` and the key
`00a1b2c3d4e5f607`.

Contract: [reading events](doc/references/reading-events.md).

## Needs

### `event-bus`

`ingest` expects a broker that

- acknowledges a message only after it has stored it durably, and
  acknowledges 500 messages of up to 16 kB within 1 second,
- delivers messages with the same key in the order of publication,
- keeps every message of a topic for at least 7 days, also for subscribers
  that `ingest` does not know and that connect later,
- offers a second kind of topic that keeps the latest message per key
  without a time limit and can be read from the beginning.

`ingest` expects the topics it uses to exist; it does not create them.
Without the event bus it accepts nothing and answers `503`.

### `reading-format`

A versioned definition of one reading as a JSON object: which fields
exist, which are required, and where the sequence number, the time, the
flag for an estimated time and the measured values are found. `ingest`
implements major version 1 and expects that a later minor version only
adds optional fields.

## Out of scope

- Storing readings for queries.
- Knowing which plant a sensor stick belongs to, or who owns it.
- Verifying tokens. `ingest` trusts the caller identity it is given.
- Judging a reading against thresholds.
- Correcting a reading, or replacing an accepted one.

## More

- [AGENTS.md](AGENTS.md): why accepting readings is a service of its own
- [doc/context.md](doc/context.md): what the unit inherits
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- References: [ingest API](doc/references/ingest-api.md),
  [reading events](doc/references/reading-events.md),
  [accepted ranges](doc/references/accepted-ranges.md)
