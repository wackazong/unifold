# cloud

`cloud` is the server side. It accepts uploaded readings, keeps the registry
of plants with their thresholds and their history, decides when a plant needs
attention, and notifies the owner once per alert. It runs as a set of
containers and is reached through one HTTP API.

## Why

`cloud` exists so that readings become history and alerts while no client is
online. It changes when the public API changes or when readings get a new
use on the server side.

Its three jobs load and fail differently. Accepting an upload must work
whenever a client finally has a connection, also while history or evaluation
is down. Evaluation must react within a minute. Queries are read-heavy and
may be slow without harm. Each job is therefore a service of its own that
can be deployed, scaled and restarted alone.

What joins them is chosen so that a failure does not spread. Readings travel
as events, and the service that accepts them knows no receiver
([0001](docs/decisions/0001-services-learn-about-readings-through-events.md)).
Every service keeps its own data
([0002](docs/decisions/0002-each-service-owns-its-data.md)). One entry point
authenticates
([0003](docs/decisions/0003-one-gateway-is-the-only-public-entry.md)). The
event bus and the database belong to no service and are a unit of their own.
The price is eventual consistency and repeated deliveries
([0004](docs/decisions/0004-every-event-consumer-is-idempotent.md)).

## Capabilities

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

Contract: [public API](docs/references/public-api/index.md).

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
- makes exactly one capability reachable from outside the private network.
  Whoever publishes that capability terminates TLS.

## Out of scope

- Talking to a sensor stick. Readings arrive only through `public-api`.
- Assigning or correcting the time of a reading. `cloud` trusts the time a
  reading carries.
- Changing or deleting a single reading.
- User accounts with passwords, recovery or sharing. An owner is whoever
  holds a token of that owner.
- Threshold presets and knowledge about plant species.
- Delivering a notification to a phone. That is the push service's part.

## Read next

1. [docs/explanation/invariants.md](docs/explanation/invariants.md),
   [runtime.md](docs/explanation/runtime.md),
   [deployment.md](docs/explanation/deployment.md): invariants, the path of
   an upload, where things run
2. [docs/references/public-api/index.md](docs/references/public-api/index.md):
   the contract with clients
3. [docs/references/events.md](docs/references/events.md): event envelope and
   topic names
4. [docs/references/service-calls.md](docs/references/service-calls.md): rules
   for HTTP calls between services
5. [docs/references/glossary.md](docs/references/glossary.md): the terms of
   the server side
6. [docs/explanation/context.md](docs/explanation/context.md): what it
   inherits from the project
7. [Context diagram](docs/diagrams/context.md),
   [component diagram](docs/diagrams/component.md),
   [architecture diagram](docs/diagrams/architecture.md),
   [decisions](docs/decisions/index.md)
