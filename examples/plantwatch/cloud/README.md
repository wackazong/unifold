---
unit: cloud
summary: Server side that stores readings, keeps the plant registry and raises alerts
kind: system
status: planned
provides:
  public-api:
    kind: http
    summary: Upload readings and query plants, history and alerts
    contract: doc/references/public-api/index.md
needs:
  push-service:
    kind: http
    summary: Delivers a notification to a phone
  reading-format:
    kind: specification
    summary: The format in which readings are uploaded
  container-host:
    kind: infrastructure
    summary: Runs containers, gives them a private network and persistent volumes
wiring:
  public-api: gateway.public-api
  gateway.ingest-api: ingest.ingest-api
  gateway.plants-api: plants.plants-api
  gateway.alerts-api: alerts.alerts-api
  ingest.event-bus: platform.event-bus
  ingest.reading-format: reading-format
  plants.reading-events: ingest.reading-events
  plants.sql-db: platform.sql-db
  plants.event-bus: platform.event-bus
  alerts.reading-events: ingest.reading-events
  alerts.plants-api: plants.plants-api
  alerts.push: push-service
  alerts.sql-db: platform.sql-db
  alerts.event-bus: platform.event-bus
  platform.container-host: container-host
---
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
  whether it is new, a duplicate or rejected. A reading reported as new or
  duplicate is kept; the client may delete its copy.
- **Every other request is safe to repeat too.** Plants are created with an
  identifier the client chooses, so a repeated request changes nothing.
- **An alert follows a reading within 1 minute.** When an accepted reading
  makes a plant need attention, the alert is visible in the API and one
  notification is handed to the push service within 1 minute after the
  upload. An alert that stays open produces no further notification.
- **History is kept for 2 years per plant**, at full resolution for the last
  90 days and as hourly and daily aggregates for the rest.
- **An owner sees only what belongs to that owner.**

Limits:

- Queries lag behind uploads. A reading reported as new appears in history
  and in alerts within seconds, not within the upload request.
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

`cloud` hands over a notification addressed to an owner id. It expects the
provider to deliver it to every phone that has registered with the provider
for that owner. It expects the provider to accept a collapse identifier: two
notifications with the same identifier appear on a phone as one. Delivery may
be delayed and may fail; `cloud` does not learn whether a phone showed the
notification.

### `reading-format`

A versioned definition of one reading as a JSON document: its fields, their
units and ranges, and how sensor id and sequence number identify it. `cloud`
accepts major version 1. It expects that a newer minor version only adds
optional fields.

### `container-host`

Something that runs the containers of `cloud`, restarts one that stops,
connects them with a private network in which they find each other by name,
and gives a container that asks for one a volume that survives restarts.
Exactly one port is reachable from outside the private network. Whoever
publishes that port terminates TLS.

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
- [doc/architecture.md](doc/architecture.md): invariants, the path of an
  upload, where things run
- [Context diagram](doc/diagrams/context.md),
  [component diagram](doc/diagrams/component.md),
  [architecture diagram](doc/diagrams/architecture.md)
- [Decisions](doc/decisions/index.md)
- References: [public API](doc/references/public-api/index.md),
  [events](doc/references/events.md),
  [calls between services](doc/references/service-calls.md)
