# Public API: plants

Part of the [public API](index.md). The general rules, errors and limits
are in the index.

## The plant

```json
{
  "id": "0b6f6f0e-2c1d-4f7a-9d42-6f1f0c8a7e11",
  "name": "Monstera in the hall",
  "sensor_id": "00a1b2c3d4e5f607",
  "thresholds": {
    "soil_moisture": {"min": 30.0},
    "light": {"min": 800},
    "temperature": {"min": 12.0, "max": 32.0}
  },
  "latest_reading": { "...": "one reading" },
  "created_at": "2026-10-06T09:00:00Z",
  "updated_at": "2026-10-06T09:00:00Z"
}
```

| Field | Set by | Content |
|---|---|---|
| `id` | client, in the path | UUID that the client generates |
| `name` | client, required | 1 to 60 characters |
| `sensor_id` | client, optional | The sensor stick attached to the plant. Absent: none. |
| `thresholds` | client, optional | Per quantity an object with `min`, `max` or both. A quantity without thresholds is absent. |
| `latest_reading` | server | The reading with the latest time among the raw readings of the plant, in the form that `reading-format` defines. Absent when the plant has no reading of the last 90 days. |
| `created_at`, `updated_at` | server | Times of the first and the latest `PUT` |

The quantities are `soil_moisture`, `light` and `temperature`, in the units
of the project conventions. `min` is the threshold below which the plant
needs attention, `max` the one above which it does.

## Operations

| Operation | Request body | Response |
|---|---|---|
| `GET /v1/plants` | none | `200` with `{"items": [plant, ...]}`, ordered by `name` |
| `PUT /v1/plants/{plant_id}` | `name`, `sensor_id`, `thresholds` | `200` with the plant |
| `GET /v1/plants/{plant_id}` | none | `200` with the plant |
| `DELETE /v1/plants/{plant_id}` | none | `204` |

Rules:

- `PUT` creates the plant if the owner has none with this id and replaces
  it otherwise. It replaces all client fields: a field that is absent in
  the body is removed from the plant. The history stays.
- `PUT` answers `400` when a threshold lies outside the range of its
  quantity or `min` is not below `max`.
- A sensor stick is attached to at most one plant, across all owners. `PUT`
  with a `sensor_id` that is attached to another plant answers `409` with
  `sensor_already_attached`. To move a sensor stick, detach it from the
  first plant, then attach it to the second.
- `PUT` answers `409` with `plant_limit_reached` when it would create the
  51st plant of the owner.
- `DELETE` removes the plant and its history and detaches the sensor stick.
  `DELETE` of a plant that does not exist answers `204`.
- `GET`, `PUT` and `DELETE` with a plant id that belongs to another owner
  answer `404`.

## History

The history of a plant consists of the accepted readings of the sensor
stick that was attached to the plant when the server processed the reading.
Detaching a sensor stick leaves the history with the plant.

```http
GET /v1/plants/{plant_id}/history?from=...&to=...&resolution=hour
```

| Parameter | Default | Content |
|---|---|---|
| `from` | 24 hours before `to` | Start of the period, inclusive |
| `to` | now | End of the period, exclusive |
| `resolution` | `raw` | `raw`, `hour` or `day` |
| `limit` | 1 000 | Items per page, at most 1 000 |
| `cursor` | none | The `next` value of the previous page |

| `resolution` | An item is | Available for |
|---|---|---|
| `raw` | one reading, in the form that `reading-format` defines | readings with a time in the last 90 days |
| `hour` | an aggregate over one hour, starting at the full hour | 2 years |
| `day` | an aggregate over one UTC day | 2 years |

Response `200` with `resolution=hour`:

```json
{
  "resolution": "hour",
  "items": [
    {
      "start": "2026-10-05T14:00:00Z",
      "count": 4,
      "soil_moisture": {"min": 41.2, "mean": 41.9, "max": 42.5},
      "light": {"min": 310, "mean": 1250, "max": 2400},
      "temperature": {"min": 21.4, "mean": 21.6, "max": 21.9}
    }
  ],
  "next": "<cursor>"
}
```

Rules:

- Items are in ascending order of time. Raw readings with the same time are
  in ascending order of sequence number.
- `next` is present when more items exist. The next request repeats all
  parameters and adds `cursor`.
- `count` is the number of readings in the aggregate. An hour or a day
  without readings has no item.
- A quantity that no reading of the period measured is absent from the
  aggregate.
- `mean` has the resolution of its quantity.
- A reading that arrives late changes the aggregates of its hour and day.
  A client that caches aggregates fetches a period again after it has
  uploaded readings from that period.
- The server deletes raw readings after 90 days and aggregates after 2
  years, counted from the time of the reading.
