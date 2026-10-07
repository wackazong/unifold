# Plants API

The contract of the port `plants-api`. The operations for a caller that
acts for an owner, with their bodies and errors, are defined above this
unit and cited in [context](../context.md). This reference states how
`plants` serves them and defines the operation that only this unit has.

## Operations for an owner

| Operation | Notes |
|---|---|
| `GET /v1/plants` | |
| `PUT /v1/plants/{plant_id}` | |
| `GET /v1/plants/{plant_id}` | |
| `DELETE /v1/plants/{plant_id}` | Also deletes the raw readings and the aggregates of the plant |
| `GET /v1/plants/{plant_id}/history` | |

- Every request carries `X-Owner-Id`. Without it `plants` answers `400`
  with `invalid_request`.
- `plants` does not verify who the caller is. It limits every read and
  every change to the plants of the owner in the header.
- A `PUT` is one transaction. Two `PUT` requests for the same plant at the
  same moment both succeed; the later one wins as a whole.
- Two `PUT` requests that attach the same sensor stick to two plants at
  the same moment: one succeeds, the other gets `409` with
  `sensor_already_attached`.
- `latest_reading` is the stored reading with the latest time, not the one
  that arrived last. For a plant whose raw readings are all older than 90
  days it is absent.

## Lookup by sensor id

For a caller that acts for itself and has a reading in hand.

```http
GET /internal/v1/sensors/{sensor_id}/plant
```

No `X-Owner-Id`. Response `200`:

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
| `plant_id` | The plant to which the sensor stick is attached now |
| `owner_id` | The owner of that plant |
| `name` | The name of the plant |
| `thresholds` | Per quantity an object with `min`, `max` or both. A quantity without thresholds is absent. A plant without thresholds has `{}`. |

| Case | Answer |
|---|---|
| The sensor stick is attached to a plant | `200` |
| The sensor stick is attached to no plant | `404` with `not_found` |
| `sensor_id` is not 16 lower-case hex digits | `400` with `invalid_request` |

The answer reflects every `PUT` and `DELETE` that was answered before the
lookup arrived.

## History and events

- `plants` adds a reading to the history when it handles the event for
  it, within 5 seconds after the event reaches `plants` while `plants`
  and its database are healthy.
- A history request sees every reading whose event was handled before the
  request arrived.
- While `plants` is behind on the event stream, history is incomplete at
  its newest end and complete again once it has caught up. Nothing is
  skipped.

## Examples

The plant P of owner A has the sensor stick `00a1b2c3d4e5f607` attached.

| Case | Request | Answer |
|---|---|---|
| No owner header | `GET /v1/plants` without `X-Owner-Id` | `400` `invalid_request` |
| Other owner | `GET /v1/plants/{P}` with `X-Owner-Id` B | `404` `not_found` |
| Lookup | `GET /internal/v1/sensors/00a1b2c3d4e5f607/plant` | `200` with `plant_id` P and `owner_id` A |
| Lookup after detaching | The same, after a `PUT` of P without `sensor_id` was answered | `404` `not_found` |
| Lookup with a bad id | `GET /internal/v1/sensors/00A1/plant` | `400` `invalid_request` |
| Race for a sensor stick | Two `PUT` requests attach one free sensor stick to two plants | One `200`, one `409` `sensor_already_attached` |
| Event twice | The event of reading 4711 of the sensor stick arrives twice | The hour of the reading has `count` 1 |
| Late event | Events arrive for 14:30, then for 14:15 | `hour` history has one item for 14:00 with `count` 2 |
| Unattached | An event arrives for a sensor stick that is attached to no plant | No history changes |
| Database down | Any operation | `503` `unavailable` |

## Timing

| Operation | Answered within |
|---|---|
| Lookup by sensor id | 50 ms |
| Operations on plants | 200 ms |
| A page of history, any resolution | 2 seconds |

The values hold while the database is healthy and within its planned
size.

## Health

`GET /healthz` answers `200` while the database is reachable. It does not
depend on the event bus: `plants` serves queries while it cannot consume
events.
