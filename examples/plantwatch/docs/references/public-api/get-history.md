# get-history

Kind: query

```http
GET /v1/plants/{plant_id}/history?from=...&to=...&resolution=hour&limit=...&cursor=...
Authorization: Bearer <token>
```

Pre: a valid token. The parameters:

| Parameter | Default | Content |
|---|---|---|
| `from` | 24 hours before `to` | Start of the period, inclusive |
| `to` | now | End of the period, exclusive |
| `resolution` | `raw` | `raw`, `hour` or `day` |
| `limit` | 1 000 | Items per page, at most 1 000 |
| `cursor` | none | The `next` value of the previous page |

Result: `200` with the history of the plant: the accepted readings of the sensor stick that was attached to the plant when the server processed the reading. Detaching a sensor stick leaves the history with the plant.

| `resolution` | An item is | Available for |
|---|---|---|
| `raw` | one reading, in the form that the [reading schema](../reading-schema.md) defines | readings with a time in the last 90 days |
| `hour` | an aggregate over one hour, starting at the full hour | 2 years |
| `day` | an aggregate over one UTC day | 2 years |

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

Items are in ascending order of time; raw readings with the same time are in ascending order of sequence number. `next` is present when more items exist; the next request repeats all parameters and adds `cursor`. `count` is the number of readings in the aggregate; an hour or a day without readings has no item. A quantity that no reading of the period measured is absent from the aggregate. `mean` has the resolution of its quantity. A reading that arrives late changes the aggregates of its hour and day; a client that caches aggregates fetches a period again after it has uploaded readings from that period. The server deletes raw readings after 90 days and aggregates after 2 years, counted from the time of the reading.
Errors: `404` `not_found` when the plant does not exist or belongs to another owner; `400` `invalid_request` for a malformed parameter; the [errors](error.md) that every operation can answer.
Examples:

| Case | Request | Response |
|---|---|---|
| One hour | `resolution=hour` for an hour with 4 readings | The item shown above, `count` 4 |
| Late reading | A reading of 14:15 is uploaded after the hour 14:00 was fetched | The aggregate of 14:00 has changed at the next request |
| More than a page | 1 500 raw readings in the period | `200` with 1 000 items and `next`; the next request with `cursor` returns the rest |
