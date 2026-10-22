# plants

`plants` is the service that knows the plants. It keeps for every owner the plants with their names, the sensor stick attached to each, and the thresholds. It follows the stream of accepted readings and builds the history of every plant from it. It is the one source for the question "which plant does this sensor stick belong to, and what are its thresholds".

## Why

Somebody has to own the answer to "which plant is this, and whose". This unit does, and it changes when what is known about a plant changes: its fields, its thresholds, its history. Names, attached sensor sticks and thresholds are entered rarely and read often, and they must be correct at once, so they live in one place with one schema and are served by calls.

History is kept in the same service because the registry decides where a reading belongs: the attachment of a sensor stick to a plant is the join between the two. A separate history service would need that attachment for every single reading ([0002](docs/decisions/0002-a-reading-joins-the-plant-at-the-time-it-is-handled.md)).

History is a projection of the reading events, not a second truth. It is built so that handling an event twice changes nothing and that the order of events does not matter. Raw readings are kept only as long as a client can still ask for them; beyond that, hourly aggregates carry the two years ([0001](docs/decisions/0001-raw-readings-for-90-days-hourly-aggregates-for-2-years.md)).

The trade-off: queries and event handling share one service and one database. A heavy history query can slow down the intake of events. That is accepted for version 1.

## Capabilities

### `plants-api`

An HTTP API with two groups of operations.

**For a caller that acts for an owner** and says so in the header `X-Owner-Id`: list, create, replace, read and delete plants, and read the history of a plant, raw or aggregated per hour or day.

**For a caller that acts for itself**: look up the plant to which a sensor stick is attached, with its owner, its name and its thresholds.

A caller can rely on this:

- An owner sees and changes only the plants of that owner. A plant of another owner behaves like a plant that does not exist.
- A sensor stick is attached to at most one plant at any time.
- Creating and replacing use an identifier that the caller chooses. Every operation can be repeated with the same result.
- A change to a plant is visible to the next request, also to the lookup by sensor id.
- A reading counts once in the history, however often its event arrives.
- A reading is in the history within 5 seconds after its event reaches `plants`, while `plants` and its database are healthy.
- Raw readings are available for 90 days, hourly and daily aggregates for 2 years, both counted from the time of the reading.

Limits:

- At most 50 plants per owner.
- A reading belongs to the plant to which its sensor stick is attached when `plants` handles the event. A reading of a sensor stick that is attached to no plant at that moment is not kept.
- A raw reading is returned as it was uploaded. `plants` does not interpret it; it uses the values that the event names.
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

Contract: [plants API](../../docs/references/plants-api.md).

## Needs

### `reading-events`

A stream with one event per accepted reading. `plants` expects each event to carry the sensor id, the sequence number, the time of the reading, a flag for an estimated time, the measured values under the names `soil_moisture`, `light` and `temperature`, and the reading as it was uploaded. It expects every value to lie within the range of its quantity.

`plants` copes with repeated events and with events in any order. It expects that every accepted reading appears on the stream and stays there for at least 7 days.

Contract: [reading events](../../docs/references/reading-events.md).

### `sql-db`

A relational database with a schema that only `plants` uses, and with transactions. `plants` expects a committed transaction to survive a restart, and a column type for JSON documents. It plans with at most 25 920 raw readings and 17 520 hourly aggregates per plant.

### `event-bus`

A broker with a durable subscription: `plants` continues where it stopped after a restart, and an event it has not confirmed is delivered again. All instances of `plants` share one subscription.

## Out of scope

- Accepting or validating uploaded readings.
- Deciding whether a plant needs attention. `plants` stores thresholds and does not compare anything with them.
- Threshold presets and plant species.
- Knowing owners beyond their identifier. `plants` trusts the owner id it is given.
- Telling anybody that a plant changed. Others ask when they need to know.

## Read next

1. [plants API](../../docs/references/plants-api.md): the operations and their guarantees
2. [reading events](../../docs/references/reading-events.md): what the unit requires of the stream of readings
3. [docs/references/data-model.md](docs/references/data-model.md): what is stored and for how long
4. [docs/explanation/context.md](docs/explanation/context.md): what the unit inherits
5. [Context diagram](docs/diagrams/context.md), [decisions](docs/decisions/index.md)
