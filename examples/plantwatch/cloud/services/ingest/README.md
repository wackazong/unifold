# ingest

`ingest` is the service that takes readings in. It receives a batch of readings of one sensor stick, checks every reading, recognises the ones it has accepted before, and announces each new one as an event. It stores no readings itself and does nothing with their content beyond checking it.

## Why

The moment a client uploads is the only chance to take its readings. This unit exists to make that moment as hard to fail as possible: it does the least that makes a reading safe, which is to check it, to store it durably as an event, and to say so. It changes when the checks on an uploaded reading change or when readings carry a new quantity.

Everything else is left out on purpose. `ingest` has no database, calls no other service and does not know what a plant is. Its only dependency is the event bus, which it needs anyway to publish. Even the memory of which readings it has accepted lives there ([0001](docs/decisions/0001-accepted-ranges-are-kept-on-the-event-bus.md)).

`ingest` is also the border for the format of readings. It is the only place that reads an uploaded reading. Its events carry the values under names of their own, so that a new version of the upload format changes this unit and nothing behind it.

The trade-off: recognition of duplicates is exact in normal operation and only best effort after a failure or under concurrent uploads of the same sensor stick. That is acceptable because every subscriber must tolerate repeated events anyway ([context](docs/explanation/context.md)).

## Capabilities

### `ingest-api`

- `ingest` depends on nothing but the event bus. It answers uploads with `200` while no subscriber of its events is running.
- For a sensor stick with more than 1 000 gaps in its sequence numbers, a reading in an old gap can be reported as `duplicate` without having been accepted.

## Out of scope

- Storing readings for queries.
- Knowing which plant a sensor stick belongs to, or who owns it.
- Verifying tokens. `ingest` trusts the caller identity it is given.
- Judging a reading against thresholds.
- Correcting a reading, or replacing an accepted one.

## Read next

1. [ingest API](../../docs/references/ingest-api.md): the upload operation and the checks
2. [reading events](../../docs/references/reading-events.md): topic and content of the events
3. [docs/references/accepted-ranges.md](docs/references/accepted-ranges.md): the state with which duplicates are recognised
4. [docs/explanation/context.md](docs/explanation/context.md): what the unit inherits
5. [Context diagram](docs/diagrams/context.md), [decisions](docs/decisions/index.md)
