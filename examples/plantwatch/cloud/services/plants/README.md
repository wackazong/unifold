# plants

`plants` is the service that knows the plants. It keeps for every owner the plants with their names, the sensor stick attached to each, and the thresholds. It follows the stream of accepted readings and builds the history of every plant from it. It is the one source for the question "which plant does this sensor stick belong to, and what are its thresholds".

## Why

Somebody has to own the answer to "which plant is this, and whose". This unit does, and it changes when what is known about a plant changes: its fields, its thresholds, its history. Names, attached sensor sticks and thresholds are entered rarely and read often, and they must be correct at once, so they live in one place with one schema and are served by calls.

History is kept in the same service because the registry decides where a reading belongs: the attachment of a sensor stick to a plant is the join between the two. A separate history service would need that attachment for every single reading ([0002](docs/decisions/0002-a-reading-joins-the-plant-at-the-time-it-is-handled.md)).

History is a projection of the reading events, not a second truth. It is built so that handling an event twice changes nothing and that the order of events does not matter. Raw readings are kept only as long as a client can still ask for them; beyond that, hourly aggregates carry the two years ([0001](docs/decisions/0001-raw-readings-for-90-days-hourly-aggregates-for-2-years.md)).

The trade-off: queries and event handling share one service and one database. A heavy history query can slow down the intake of events. That is accepted for version 1.

## Needs

### `sql-db`

`plants` plans with at most 25 920 raw readings and 17 520 hourly aggregates per plant.

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
