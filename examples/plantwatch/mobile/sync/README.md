# sync

`sync` is the memory of the phone. It keeps the owner's plants, their history and their alerts in a store on the phone, takes in the readings that are fetched from sensor sticks, uploads them to the server, and brings what the server knows back to the phone. Whoever reads from it never waits for a network.

## Why

A phone is offline in cellars and stairwells and comes online at moments nobody controls. This library exists so that neither fact reaches a reader of the data. It owns the one store on the phone, and it alone speaks to the server. A reader asks the store; the exchange with the server runs behind the store, on its own schedule.

The unit changes when the phone shall keep something new or keep it differently, or when `cloud-api` changes. A change of wording or of the radio does not reach it.

Readings and plant settings flow in opposite directions and are kept apart on purpose. Readings are immutable and only ever travel towards the server, so repeating a transfer is always safe. Plant settings can change at both ends, so they need a rule for collisions ([0002](docs/decisions/0002-the-change-that-reaches-the-server-last-wins.md)).

The main trade-off: the phone holds a copy that can be days behind the server. `sync` does not hide this; it reports the age of what it holds.

What must stay true: `sync` acknowledges a batch only after it is stored durably, and a reading in the store never changes.

## Capabilities

### `plant-data`

- The exchange with the server runs by itself: after new readings, after a command, when a network connection appears, and when it is asked for.
- Readings of a sensor stick that is attached to no plant wait on the phone and are not uploaded.

## Needs

### `cloud-api`

`sync` counts a request without an answer after 20 seconds as "try again later".

## Out of scope

- Talking to sensor sticks, and converting tick counts to times.
- Deciding whether a plant needs attention. `sync` stores thresholds and alerts and compares nothing.
- Showing anything, including notifications.
- History older than 90 days.

## Read next

1. [docs/references/local-store.md](docs/references/local-store.md): what is kept and in which states
2. [docs/references/exchange.md](docs/references/exchange.md): the exchange with the server
3. [plant data](../docs/references/plant-data.md): the contract of the provided capability
4. [docs/references/glossary.md](docs/references/glossary.md): query and command, upload state, waiting change, pause
5. [Context diagram](docs/diagrams/context.md)
6. [docs/explanation/context.md](docs/explanation/context.md): what `sync` inherits from above
7. [Decisions](docs/decisions/index.md)
