---
unit: sync
summary: Keeps plants, history and alerts on the phone and in step with the server
kind: library
status: planned
provides:
  plant-data:
    kind: library
    summary: Plants, history and alerts, readable offline and updated when they change
    contract: doc/references/plant-data.md
needs:
  sensor-readings:
    kind: library
    summary: Readings fetched from sensor sticks, to store and upload
  cloud-api:
    kind: http
    summary: Stores readings and returns plants, history and alerts
  reading-format:
    kind: specification
    summary: The format in which readings are stored and uploaded
---
# sync

sync is the memory of the phone. It keeps the owner's plants, their history
and their alerts in a store on the phone, takes in the readings that are
fetched from sensor sticks, uploads them to the server, and brings what the
server knows back to the phone. Whoever reads from it never waits for a
network.

## Provides

### `plant-data`

The owner's plants, history and alerts as the phone holds them, and the
commands that change a plant.

- Every query answers from the store on the phone, with or without a
  network connection, and can be observed: the observer gets a new answer
  whenever the data changes.
- A fetched reading is part of the history as soon as it is stored, before
  it is uploaded.
- A command, such as a changed threshold, takes effect on the phone at once
  and survives a restart. The plant is marked `waiting` until the server has
  confirmed the change, and `refused` if the server refuses it.
- The port reports how old the data is: the age of each plant's readings
  and the time of the last successful exchange with the server.
- The store keeps 90 days of history per plant.
- The exchange with the server runs by itself: after new readings, after a
  command, when a network connection appears, and when it is asked for.
- The port works from the first start without an account and without a
  network connection. It lets the server create the owner at the first
  exchange, and it lets a further phone join the same owner.

Limits: alerts come from the server only; without an exchange the phone
shows the alerts it last received. At most 50 plants. Readings of a sensor
stick that is bound to no plant wait on the phone and are not uploaded.

Example: the owner lowers a threshold in a cellar without reception. The
query for the plant returns the new threshold at once, marked `waiting`.
Back upstairs the change goes to the server, and observers receive the
plant again, now `in step`.

Contract: [plant-data](doc/references/plant-data.md).

## Needs

### `sensor-readings`

A source of readings from the owner's sensor sticks. sync expects that it

- hands over readings in batches of one sensor stick, each reading with
  sensor id, sequence number, tick count, its measured values, a UTC time
  and a flag for an estimated time,
- delivers only values inside their valid ranges,
- waits for an acknowledgement per batch and keeps the readings available
  at their origin until then,
- may deliver a reading again, with the same sensor id and sequence number,
- starts a fetch when asked, and says per sensor stick when it last
  fetched.

### `cloud-api`

The server. sync expects that it

- creates an owner on request and gives out a token for it, gives out a
  further token to whoever holds one, and says until when a token is valid,
- accepts a batch of readings of one sensor stick in the `reading-format`
  and answers for every reading whether it is new, known already or
  refused,
- puts a reading into the history of the plant its sensor stick is bound to
  when the reading arrives,
- returns the owner's plants and alerts, a single plant, and the history of
  a plant for a span of time,
- accepts a plant as a whole under an id the phone has chosen, creating or
  replacing it, and answers with the plant as it then is; removes a plant,
- treats a repeated request like the first one, and
- answers an error with a code that tells "try again later" from "this
  request is wrong".

### `reading-format`

The definition of a reading as it is uploaded and as the history comes
back: field names, units, identity, the flag for an estimated time, and a
version. sync writes and reads this format and no other.

## Out of scope

- Talking to sensor sticks, and converting tick counts to times.
- Deciding whether a plant needs attention. sync stores thresholds and
  alerts and compares nothing.
- Showing anything, including notifications.
- History older than 90 days.

## More

- [AGENTS.md](AGENTS.md): why sync is built this way
- [Context diagram](doc/diagrams/context.md)
- [doc/context.md](doc/context.md): what sync inherits from above
- [Local store](doc/references/local-store.md): what is kept, for how long,
  and the states of a reading and of a change
- [Exchange with the server](doc/references/exchange.md): order, sizes and
  pauses
- [Decisions](doc/decisions/index.md)
