# cloud

`cloud` is the server side. It accepts uploaded readings, keeps the registry
of plants with their thresholds and their history, decides when a plant needs
attention, and notifies the owner once per alert. It runs as a set of
containers and is reached through one HTTP API.

## Provides

### `public-api`

An HTTP API with JSON bodies for a client that acts for one owner. The client
obtains a token, uploads batches of readings, registers plants with their
sensor sticks and thresholds, and queries history and alerts.

A client can rely on this:

- **An upload is safe to repeat.** The response says for every reading
  whether it is `new`, `duplicate` or `rejected`. A reading reported as
  `new` or `duplicate` is kept; the client may delete its copy.
- **Every other request is safe to repeat too.** A plant is created under an
  identifier the client chooses; the same `PUT` sent twice leaves one plant.
- **An alert follows a reading within 1 minute.** When an accepted reading
  makes a plant need attention, the alert is visible in the API and one
  notification is handed to the push service within 1 minute after the
  upload response. An alert that stays open produces no further
  notification.
- **History is kept for 2 years per plant**, at full resolution for the last
  90 days and as hourly and daily aggregates for the rest.
- **An owner sees only what belongs to that owner.** A request for a plant
  or an alert of another owner answers `404`.

Limits:

- Queries lag behind uploads. A reading reported as `new` appears in the
  history within 10 seconds after the upload response, not within the
  upload request.
- `cloud` judges readings by the time they carry, not by the time they
  arrive. A batch that arrives days late opens and closes alerts late.
- `cloud` does not check that the caller owns the sensor stick whose
  readings it uploads. A sensor stick holds no secret that could prove it.
- At most 50 plants per owner and 500 readings per batch.

Example:

```http
POST /v1/sensors/00a1b2c3d4e5f607/batches
Authorization: Bearer <token>
```

```json
{"results": [{"sequence_number": 4711, "status": "new"},
             {"sequence_number": 4712, "status": "duplicate"}]}
```

Contract: [public API](doc/references/public-api/index.md).

## Needs

### `push-service`

`cloud` hands over one notification per request: an owner id as addressee,
a title of up to 60 characters, a body of up to 120 characters, five short
data fields, a collapse identifier and a time to live of 24 hours. It
expects the provider

- to deliver the notification to every phone that has registered with the
  provider for that owner, and to stop trying when the time to live is over,
- to show two notifications with the same collapse identifier on a phone as
  one,
- to answer every request with one of three results: taken, refused for
  good, or failed for now.

Delivery may be late and may fail; `cloud` does not learn whether a phone
showed the notification.

### `reading-format`

A versioned definition of one reading as a JSON document: its fields, their
units and ranges, and how sensor id and sequence number identify it. `cloud`
accepts major version 1. It expects that a newer minor version only adds
optional fields.

### `container-host`

Something that runs the containers of `cloud`, restarts one that stops, and
connects them with a private network in which they find each other by name.
`cloud` expects that it

- gives a container that asks for one a volume that survives restart and
  replacement of the container, and can place two volumes on separate
  storage,
- keeps the clock of every container within 10 seconds of UTC,
- makes exactly one port reachable from outside the private network.
  Whoever publishes that port terminates TLS.

## Out of scope

- Talking to a sensor stick. Readings arrive only through `public-api`.
- Assigning or correcting the time of a reading. `cloud` trusts the time a
  reading carries.
- Changing or deleting a single reading.
- User accounts with passwords, recovery or sharing. An owner is whoever
  holds a token of that owner.
- Threshold presets and knowledge about plant species.
- Delivering a notification to a phone. That is the push service's part.

## More

- [AGENTS.md](AGENTS.md): why the server side is cut this way
- [doc/context.md](doc/context.md): what it inherits from the project
- [doc/architecture.md](doc/architecture.md): invariants, the path of an
  upload, where things run
- [Context diagram](doc/diagrams/context.md),
  [component diagram](doc/diagrams/component.md),
  [architecture diagram](doc/diagrams/architecture.md)
- [Decisions](doc/decisions/index.md)
- References: [public API](doc/references/public-api/index.md),
  [events](doc/references/events.md),
  [calls between services](doc/references/service-calls.md),
  [glossary](doc/references/glossary.md)
