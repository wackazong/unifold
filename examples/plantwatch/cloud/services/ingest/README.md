# ingest

`ingest` is the service that takes readings in. It receives a batch of readings of one sensor stick, checks every reading, recognises the ones it has accepted before, and announces each new one as an event. It stores no readings itself and does nothing with their content beyond checking it.

## Why

The moment a client uploads is the only chance to take its readings. This unit exists to make that moment as hard to fail as possible: it does the least that makes a reading safe, which is to check it, to store it durably as an event, and to say so. It changes when the checks on an uploaded reading change or when readings carry a new quantity.

Everything else is left out on purpose. `ingest` has no database, calls no other service and does not know what a plant is. Its only dependency is the event bus, which it needs anyway to publish. Even the memory of which readings it has accepted lives there
([0001](docs/decisions/0001-accepted-ranges-are-kept-on-the-event-bus.md)).

`ingest` is also the border for the format of readings. It is the only place that reads an uploaded reading. Its events carry the values under names of their own, so that a new version of the upload format changes this unit and nothing behind it.

The trade-off: recognition of duplicates is exact in normal operation and only best effort after a failure or under concurrent uploads of the same sensor stick. That is acceptable because every subscriber must tolerate repeated events anyway ([context](docs/explanation/context.md)).

## Capabilities

### `ingest-api`

One HTTP operation: upload a batch of readings of one sensor stick. The response has one result per reading: `new`, `duplicate` or `rejected` with a reason.

A caller can rely on this:

- A reading reported as `new` or `duplicate` is on the event bus before the response is sent. The caller may forget it.
- The same batch may be sent any number of times. Readings accepted earlier are reported as `duplicate` and are not announced again.
- A rejected reading does not affect the other readings of the batch.
- When `ingest` cannot store events it answers `503` and reports no reading as accepted. Sending the batch again later is always correct.
- `ingest` answers every request within 4 seconds, a batch of 500 readings within 2 seconds while the event bus is healthy.
- `ingest` depends on nothing but the event bus. It answers uploads with `200` while no subscriber of its events is running.

Limits:

- At most 500 readings and 1 MB per batch.
- `ingest` recognises a duplicate by sensor id and sequence number alone. It does not compare contents.
- `ingest` does not know plants or owners. It accepts readings of any sensor id.
- For a sensor stick with more than 1 000 gaps in its sequence numbers, a reading in an old gap can be reported as `duplicate` without having been accepted.

Example response:

```json
{"results": [{"sequence_number": 4711, "status": "new"},
             {"sequence_number": 4712, "status": "rejected",
              "code": "value_out_of_range",
              "message": "soil moisture 104.2 is outside 0 to 100"}]}
```

Contract: [ingest API](../../docs/references/ingest-api.md).

### `reading-events`

A stream with one event of the type `reading.accepted` for every reading that `ingest-api` reported as `new`. An event carries the sensor id, the sequence number, the time, the measured values under fixed names, and the reading as it was uploaded. A subscriber does not need to know the format in which readings are uploaded.

A subscriber can rely on this:

- **Key.** The key of an event is the sensor id.
- **Delivery.** Every accepted reading appears on the stream at least once and stays there for 7 days. A subscriber that was away for less than 7 days misses nothing.
- **Order.** Events of one sensor stick arrive in the order in which `ingest` accepted the readings. Within one batch that is the ascending order of sequence numbers.
- Every value in an event has passed validation: it lies within the range of its quantity.
- The `id` of an event is derived from sensor id and sequence number.

Limits:

- An event can arrive more than once, with the same `id`. This happens after a failure and when the same reading is uploaded at two places at the same moment.
- The order of events is the order of acceptance, not the order of sequence numbers or times. A batch that is uploaded late produces events for old readings after events for newer ones.

Example: the accepted reading 4711 of the sensor stick `00a1b2c3d4e5f607` becomes one event with the `id` `00a1b2c3d4e5f607-4711` and the key `00a1b2c3d4e5f607`.

Contract: [reading events](../../docs/references/reading-events.md).

## Needs

### `event-bus`

`ingest` expects a broker that

- acknowledges a message only after it has stored it durably, and acknowledges 500 messages of up to 16 kB within 1 second,
- delivers messages with the same key in the order of publication,
- keeps every message of a topic for at least 7 days, also for subscribers that `ingest` does not know and that connect later,
- offers a second kind of topic that keeps the latest message per key without a time limit and can be read from the beginning.

`ingest` expects the topics it uses to exist; it does not create them. Without the event bus it accepts nothing and answers `503`.

## Out of scope

- Storing readings for queries.
- Knowing which plant a sensor stick belongs to, or who owns it.
- Verifying tokens. `ingest` trusts the caller identity it is given.
- Judging a reading against thresholds.
- Correcting a reading, or replacing an accepted one.

## Read next

1. [docs/references/ingest-api.md](../../docs/references/ingest-api.md): the upload operation and the checks
2. [docs/references/reading-events.md](../../docs/references/reading-events.md):
   topic and content of the events
3. [docs/references/accepted-ranges.md](docs/references/accepted-ranges.md):
   the state with which duplicates are recognised
4. [docs/explanation/context.md](docs/explanation/context.md): what the unit inherits
5. [Context diagram](docs/diagrams/context.md),
   [decisions](docs/decisions/index.md)
