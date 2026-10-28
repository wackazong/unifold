# plants-api

Contract of `plants.plants-api`. The operations for a caller that acts for an owner, with their bodies and errors, are defined by the public API of plantwatch and cited in [context](../explanation/context.md); this contract states how `plants` serves them and defines the lookup that only this unit has. Notation: HTTP, with JSON bodies as the project conventions define them.
Sources: the public API of plantwatch, the calls between services of `cloud`, decisions 0001 and 0002 of `plants`.

## Rules for the operations of an owner

- Every request to `/v1/plants` carries `X-Owner-Id`. Without it `plants` answers `400` with `invalid_request`.
- `plants` does not verify who the caller is. It limits every read and every change to the plants of the owner in the header.
- `latest_reading` is the stored reading with the latest time, not the one that arrived last. For a plant whose raw readings are all older than 90 days it is absent.
- While the database cannot be reached, every operation answers `503` with `unavailable`. Operations on plants are answered within 200 ms and a page of history within 2 seconds while the database is healthy and within its planned size.

## History and events

- `plants` adds a reading to the history when it handles the event for it, within 5 seconds after the event reaches `plants` while `plants` and its database are healthy.
- A history request sees every reading whose event was handled before the request arrived.
- While `plants` is behind on the event stream, history is incomplete at its newest end and complete again once it has caught up. Nothing is skipped.
- A reading belongs to the plant to which its sensor stick is attached when `plants` handles the event. A reading of a sensor stick that is attached to no plant at that moment is not kept.
- A raw reading is returned as it was uploaded. `plants` does not interpret it; it uses the values that the event names.

## Parts

### list-plants

Kind: query

```http
GET /v1/plants
X-Owner-Id: <owner id>
```

Pre: `X-Owner-Id` is present.
Result: `200` with the plants of the owner, as the public API defines.
Errors: `400` `invalid_request` without the owner header; `503` `unavailable`.
Examples:

| Case | Request | Answer |
|---|---|---|
| no owner header | `GET /v1/plants` without `X-Owner-Id` | `400` `invalid_request` |
| database down | `GET /v1/plants` | `503` `unavailable` |

### put-plant

Kind: command

```http
PUT /v1/plants/{plant_id}
X-Owner-Id: <owner id>
```

Pre: `X-Owner-Id` is present; the body is the plant as the public API defines.
Result: the plant is created or replaced in one transaction, as the public API defines. Two `PUT` requests for the same plant at the same moment both succeed; the later one wins as a whole.
Errors: those of the public API; `400` `invalid_request` without the owner header; `503` `unavailable`. Two `PUT` requests that attach the same sensor stick to two plants at the same moment: one succeeds, the other gets `409` with `sensor_already_attached`.
Examples: the plant P of owner A has the sensor stick `00a1b2c3d4e5f607` attached.

| Case | Request | Answer |
|---|---|---|
| race for a sensor stick | two `PUT` requests attach one free sensor stick to two plants | one `200`, one `409` `sensor_already_attached` |

### get-plant

Kind: query

```http
GET /v1/plants/{plant_id}
X-Owner-Id: <owner id>
```

Pre: `X-Owner-Id` is present.
Result: `200` with the plant, as the public API defines.
Errors: `404` `not_found` for a plant of another owner; `400` `invalid_request` without the owner header; `503` `unavailable`.
Examples:

| Case | Request | Answer |
|---|---|---|
| other owner | `GET /v1/plants/{P}` with `X-Owner-Id` B | `404` `not_found` |

### delete-plant

Kind: command

```http
DELETE /v1/plants/{plant_id}
X-Owner-Id: <owner id>
```

Pre: `X-Owner-Id` is present.
Result: `204`; the plant, its raw readings and its aggregates are deleted and the sensor stick is detached, as the public API defines.
Errors: `400` `invalid_request` without the owner header; `503` `unavailable`.
Examples:

| Case | Request | Answer |
|---|---|---|
| twice | `DELETE /v1/plants/{P}`, then again | `204` both times |

### get-history

Kind: query

```http
GET /v1/plants/{plant_id}/history?from=&to=&resolution=&limit=&cursor=
X-Owner-Id: <owner id>
```

Pre: `X-Owner-Id` is present.
Result: `200` with the history as the public API defines, built as "History and events" says.
Errors: those of the public API; `400` `invalid_request` without the owner header; `503` `unavailable`.
Examples: the plant P of owner A has the sensor stick `00a1b2c3d4e5f607` attached.

| Case | Request | Answer |
|---|---|---|
| event twice | the event of reading 4711 of the sensor stick arrives twice | the hour of the reading has `count` 1 |
| late event | events arrive for 14:30, then for 14:15 | `hour` history has one item for 14:00 with `count` 2 |
| unattached | an event arrives for a sensor stick that is attached to no plant | no history changes |

### lookup-by-sensor

Kind: query

```http
GET /internal/v1/sensors/{sensor_id}/plant
```

Pre: no `X-Owner-Id`; the caller acts for itself and has a reading in hand.
Result: `200` with the plant to which the sensor stick is attached now, within 50 ms. The answer reflects every `PUT` and `DELETE` that was answered before the lookup arrived.

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

| Case | Request | Answer |
|---|---|---|
| lookup | `GET /internal/v1/sensors/00a1b2c3d4e5f607/plant` | `200` with `plant_id` P and `owner_id` A |
| after detaching | the same, after a `PUT` of P without `sensor_id` was answered | `404` `not_found` |
| bad id | `GET /internal/v1/sensors/00A1/plant` | `400` `invalid_request` |

### healthz

Kind: query

```http
GET /healthz
```

Pre: none.
Result: `200` while the database is reachable. It does not depend on the event bus: `plants` serves queries while it cannot consume events.
Errors: `503` otherwise.
Examples:

| Case | Request | Answer |
|---|---|---|
| bus down, database up | `GET /healthz` | `200` |

## Fake

Replays the examples and those of the public API: an HTTP server in the test that answers the requests of the tables; a test of `plant-lookup` scripts the answer of `lookup-by-sensor` per sensor id. Faults it can inject: `503` `unavailable`, no response within 5 seconds, a body that cannot be read.
