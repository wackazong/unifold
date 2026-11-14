# plants-api

Contract of `plants.plants-api`. The operations for a caller that acts for an owner, with their bodies and errors, are defined by the public API of plantwatch and cited in [context](../explanation/context.md); this contract states how `plants` serves them and defines the lookup that only this unit has. Notation: HTTP, with JSON bodies as the project conventions define them.
Sources: the public API of plantwatch and the calls between services of `cloud`.
Binding: http

## Use

A caller that acts for an owner reads and changes the owner's plants and reads their history, with `X-Owner-Id` in every request. A caller that acts for itself looks up the plant of a sensor stick with `lookup-by-sensor`, without `X-Owner-Id`. The connection has no state: any part may be called at any time.

Rules for the operations of an owner:

- Every request to `/v1/plants` carries `X-Owner-Id`. Without it `plants` answers `400` with `invalid_request`.
- `plants` does not verify who the caller is. It limits every read and every change to the plants of the owner in the header.
- `latest_reading` is the stored reading with the latest time, not the one that arrived last. For a plant whose raw readings are all older than 90 days it is absent.
- While the database cannot be reached, every operation answers `503` with `unavailable`.

How the history is built from the events:

- `plants` adds a reading to the history when it handles the event for it. A reading belongs to the plant to which its sensor stick is attached when `plants` handles the event. A reading of a sensor stick that is attached to no plant at that moment is not kept.
- A raw reading is returned as it was uploaded. `plants` does not interpret it; it uses the values that the event names.

## Qualities

| Aspect | Guarantee |
|---|---|
| latency | an operation on plants is answered within 200 ms, a page of history within 2 seconds, while the database is healthy and below its size limit; a lookup by sensor id within 50 ms |
| freshness | a reading is in the history within 5 seconds after its event reaches `plants` while `plants` and its database are healthy; a history request sees every reading whose event was handled before the request arrived; a lookup reflects every `PUT` and `DELETE` that was answered before the lookup arrived |
| consistency | while `plants` is behind on the event stream, history is incomplete at its newest end and complete again once it has caught up; nothing is skipped |
| concurrency | two `PUT` requests for the same plant at the same moment both succeed, and the later one wins as a whole; of two `PUT` requests that attach the same sensor stick to two plants at the same moment, one succeeds and the other gets `409` `sensor_already_attached` |
| availability | while the database cannot be reached, every operation answers `503` `unavailable`; `plants` serves queries while it cannot consume events |
| idempotency | every operation is safe to repeat, because the gateway repeats a failed call |
| timeout | the gateway waits 5 seconds for an answer and then counts the call as failed |
| health | `GET /healthz`, which [service-calls](service-calls.md) defines for the container host, answers `200` while the database is reachable, also while the event bus is not, and `503` otherwise |

## Parts

### list-plants

Kind: operation

```http
GET /v1/plants
X-Owner-Id: <owner id>
```

Pre: `X-Owner-Id` is present.
Result: `200` with the plants of the owner, as the public API defines.
Errors: `400` `invalid_request` without the owner header; `503` `unavailable`.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| no owner header | | `GET /v1/plants` without `X-Owner-Id` | `400` `invalid_request` |
| database down | the database cannot be reached | `GET /v1/plants` with `X-Owner-Id` A | `503` `unavailable` |

### put-plant

Kind: operation

```http
PUT /v1/plants/{plant_id}
X-Owner-Id: <owner id>
```

Pre: `X-Owner-Id` is present; the body is the plant as the public API defines.
Result: the plant is created or replaced in one transaction, as the public API defines.
Errors: those of the public API; `400` `invalid_request` without the owner header; `503` `unavailable`; `409` `sensor_already_attached` for the loser of a race for one sensor stick.
Examples: the plant P of owner A has the sensor stick `00a1b2c3d4e5f607` attached.

| Case | Input | Expected |
|---|---|---|
| race for a sensor stick | two `PUT` requests that attach one free sensor stick to two plants, at the same moment | one `200`, one `409` `sensor_already_attached` |

### get-plant

Kind: operation

```http
GET /v1/plants/{plant_id}
X-Owner-Id: <owner id>
```

Pre: `X-Owner-Id` is present.
Result: `200` with the plant, as the public API defines.
Errors: `404` `not_found` for a plant of another owner; `400` `invalid_request` without the owner header; `503` `unavailable`.
Examples:

| Case | Input | Expected |
|---|---|---|
| other owner | `GET /v1/plants/{P}` with `X-Owner-Id` B | `404` `not_found` |

### delete-plant

Kind: operation

```http
DELETE /v1/plants/{plant_id}
X-Owner-Id: <owner id>
```

Pre: `X-Owner-Id` is present.
Result: `204`; the plant, its raw readings and its aggregates are deleted and the sensor stick is detached, as the public API defines.
Errors: `404` `not_found` for a plant of another owner; `400` `invalid_request` without the owner header; `503` `unavailable`.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| delete | | `DELETE /v1/plants/{P}` with `X-Owner-Id` A | `204` |
| twice | P was deleted already | `DELETE /v1/plants/{P}` with `X-Owner-Id` A | `204` |
| other owner | | `DELETE /v1/plants/{P}` with `X-Owner-Id` B | `404` `not_found` |

### get-history

Kind: operation

```http
GET /v1/plants/{plant_id}/history?from=&to=&resolution=&limit=&cursor=
X-Owner-Id: <owner id>
```

Pre: `X-Owner-Id` is present.
Result: `200` with the history as the public API defines, built from the events as `## Use` says.
Errors: those of the public API; `400` `invalid_request` without the owner header; `503` `unavailable`.
Examples: the plant P of owner A has the sensor stick `00a1b2c3d4e5f607` attached.

| Case | Given | Input | Expected |
|---|---|---|---|
| event twice | the event of reading 4711 of the sensor stick arrived twice | `GET /v1/plants/{P}/history?resolution=hour` with `X-Owner-Id` A | `200`; the hour of the reading has `count` 1 |
| late event | events arrived for 14:30, then for 14:15 | `GET /v1/plants/{P}/history?resolution=hour` with `X-Owner-Id` A | `200`; one item for 14:00 with `count` 2 |
| unattached | an event arrived for a sensor stick that is attached to no plant | `GET /v1/plants/{P}/history` with `X-Owner-Id` A | `200`; the history is unchanged |

### lookup-by-sensor

Kind: operation

```http
GET /internal/v1/sensors/{sensor_id}/plant
```

Pre: no `X-Owner-Id`; the caller acts for itself and has a reading in hand.
Result: `200` with the plant to which the sensor stick is attached now.

```json
{
  "plant_id": "0b6f6f0e-2c1d-4f7a-9d42-6f1f0c8a7e11",
  "owner_id": "5b0e2d0a-8f0c-4d0e-9a57-0c1a2f3b4c5d",
  "name": "Monstera in the hall",
  "thresholds": {
    "soil_moisture": {"min": 30.0},
    "temperature": {"min": 12.0, "max": 32.0}
  }
}
```

| Field | Content |
|---|---|
| `plant_id` | the plant to which the sensor stick is attached now |
| `owner_id` | the owner of that plant |
| `name` | the name of the plant |
| `thresholds` | per quantity an object with `min`, `max` or both; a quantity without thresholds is absent; a plant without thresholds has `{}` |

Errors: `404` `not_found` when the sensor stick is attached to no plant; `400` `invalid_request` when `sensor_id` is not 16 lower-case hex digits; `503` `unavailable`.
Examples: the plant P of owner A has the sensor stick `00a1b2c3d4e5f607` attached.

| Case | Given | Input | Expected |
|---|---|---|---|
| lookup | | `GET /internal/v1/sensors/00a1b2c3d4e5f607/plant` | `200` with `plant_id` P and `owner_id` A |
| after detaching | a `PUT` of P without `sensor_id` was answered | `GET /internal/v1/sensors/00a1b2c3d4e5f607/plant` | `404` `not_found` |
| bad id | | `GET /internal/v1/sensors/00A1/plant` | `400` `invalid_request` |

## Fake

Replays the examples and those of the public API: an HTTP server in the test that answers the requests of the tables; a test of `plant-lookup` scripts the answer of `lookup-by-sensor` per sensor id. Faults it can inject: `503` `unavailable`, no response within 5 seconds, a body that cannot be read.
