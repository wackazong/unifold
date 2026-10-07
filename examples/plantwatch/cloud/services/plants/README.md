---
unit: plants
summary: Registry of plants with their sensors, thresholds and reading history
kind: service
status: planned
provides:
  plants-api:
    kind: http
    summary: Plants with their sensors, thresholds and history
    contract: doc/references/plants-api.md
needs:
  reading-events:
    kind: events
    summary: Accepted readings, to build the history of each plant
  sql-db:
    kind: db
    summary: Relational database with transactions
  event-bus:
    kind: queue
    summary: Durable subscription with at-least-once delivery
---
# plants

`plants` is the service that knows the plants. It keeps for every owner
the plants with their names, the sensor stick attached to each, and the
thresholds. It follows the stream of accepted readings and builds the
history of every plant from it. It is the one source for the question
"which plant does this sensor stick belong to, and what are its
thresholds".

## Provides

### `plants-api`

An HTTP API with two groups of operations.

**For a caller that acts for an owner** and says so in the header
`X-Owner-Id`: list, create, replace, read and delete plants, and read the
history of a plant, raw or aggregated per hour or day.

**For a caller that acts for itself**: look up the plant to which a sensor
stick is attached, with its owner, its name and its thresholds.

A caller can rely on this:

- An owner sees and changes only the plants of that owner. A plant of
  another owner behaves like a plant that does not exist.
- A sensor stick is attached to at most one plant at any time.
- Creating and replacing use an identifier that the caller chooses. Every
  operation can be repeated with the same result.
- A change to a plant is visible to the next request, also to the lookup
  by sensor id. Answers are never served from a cache.
- A reading counts once in the history, however often its event arrives.
- A reading is in the history within 5 seconds after its event reaches
  `plants`, while `plants` and its database are healthy.
- Raw readings are available for 90 days, hourly and daily aggregates for
  2 years, both counted from the time of the reading.

Limits:

- At most 50 plants per owner.
- A reading belongs to the plant to which its sensor stick is attached
  when `plants` handles the event. A reading of a sensor stick that is
  attached to no plant at that moment is not kept.
- A raw reading is returned as it was uploaded. `plants` does not
  interpret it; it uses the values that the event names.
- While the database is down, every operation answers `503`.

Example: the lookup by sensor id.

```http
GET /internal/v1/sensors/00a1b2c3d4e5f607/plant
```

```json
{
  "plant_id": "0b6f6f0e-2c1d-4f7a-9d42-6f1f0c8a7e11",
  "owner_id": "5b0e2d0a-8f0c-4d0e-9a57-0c1a2f3b4c5d",
  "name": "Monstera in the hall",
  "thresholds": {"soil_moisture": {"min": 30.0}}
}
```

Contract: [plants API](doc/references/plants-api.md).

## Needs

### `reading-events`

A stream with one event per accepted reading. `plants` expects each event
to carry the sensor id, the sequence number, the time of the reading, a
flag for an estimated time, the measured values under the names
`soil_moisture`, `light` and `temperature`, and the reading as it was
uploaded. It expects every value to lie within the range of its quantity.

`plants` copes with repeated events and with events in any order. It
expects that no accepted reading is missing from the stream.

### `sql-db`

A relational database with a schema that only `plants` uses, and with
transactions. `plants` expects a committed transaction to survive a
restart. It plans with about 26 000 raw readings and 17 520 hourly
aggregates per plant.

### `event-bus`

A broker with a durable subscription: `plants` continues where it stopped
after a restart, and an event it has not confirmed is delivered again.
All instances of `plants` share one subscription.

## Out of scope

- Accepting or validating uploaded readings.
- Deciding whether a plant needs attention. `plants` stores thresholds and
  does not compare anything with them.
- Threshold presets and plant species.
- Knowing owners beyond their identifier. `plants` trusts the owner id it
  is given.
- Telling anybody that a plant changed. Others ask when they need to know.

## More

- [AGENTS.md](AGENTS.md): why registry and history are one service
- [doc/context.md](doc/context.md): what the unit inherits
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- References: [plants API](doc/references/plants-api.md),
  [data model](doc/references/data-model.md)
