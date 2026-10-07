# Public API: alerts

Part of the [public API](index.md). The general rules, errors and limits
are in the index.

## The alert

An alert says that one quantity of one plant is beyond one threshold.

```json
{
  "id": "7d2c1c1e-52a0-4b0b-8a3e-1f2d3c4b5a69",
  "plant_id": "0b6f6f0e-2c1d-4f7a-9d42-6f1f0c8a7e11",
  "quantity": "soil_moisture",
  "bound": "min",
  "state": "closed",
  "threshold": 30.0,
  "opened_at": "2026-10-05T14:15:00Z",
  "opened_value": 28.4,
  "closed_at": "2026-10-06T08:30:00Z",
  "closed_reason": "recovered",
  "notification": "sent"
}
```

| Field | Content |
|---|---|
| `id` | UUID of the alert |
| `plant_id` | The plant that needs attention |
| `quantity` | `soil_moisture`, `light` or `temperature` |
| `bound` | `min`: the judged value is below the lower threshold. `max`: it is above the upper one. |
| `state` | `open` or `closed` |
| `threshold` | The value of the threshold when the alert opened |
| `opened_at` | The time of the reading that opened the alert |
| `opened_value` | The judged value of that reading |
| `closed_at` | When the alert closed. Absent while it is open. |
| `closed_reason` | `recovered`, `threshold_changed` or `expired`. Absent while it is open. |
| `notification` | `pending`, `sent` or `failed` |

## What is judged

| Quantity | Judged value |
|---|---|
| `soil_moisture` | The value of the reading |
| `temperature` | The value of the reading |
| `light` | The highest light value among the readings of the day that ends with the reading: the hour of the reading and the 24 full hours before it |

- A quantity that a reading did not measure is not judged for that
  reading.
- Light is not judged during the first 24 hours after the first reading
  of a sensor stick for a plant.
- A reading with an estimated time, and a reading that is not newer than
  the last judged reading of the same sensor stick, is not judged.

## Life of an alert

- An alert opens when the judged value of a reading is below `min` or above
  `max` and no alert is open for the same plant, quantity and bound.
- At most one alert is open per plant, quantity and bound. While it is
  open, further readings beyond the threshold change nothing.
- An alert closes with `recovered` when the judged value is back on the
  good side of the threshold by a margin. The margin prevents an alert from
  opening and closing with every small change. Its size is not part of this
  contract, but it is bounded: an alert never closes with `recovered` while
  the judged value is beyond the threshold, and it always closes when the
  value is on the good side by 10 percent of the range of its quantity
  (10.0 percent soil moisture, 10 000 lux, 8.0 °C).
- An alert closes with `threshold_changed` when the plant no longer has the
  threshold, or the threshold has moved so that the last judged value is on
  its good side. The server notices this with the next reading.
- An alert closes with `expired` when no reading of its plant was judged
  for 30 days. This also ends the alerts of a deleted plant and of a plant
  without sensor stick.
- A closed alert never opens again. A new violation is a new alert with a
  new `id`.
- `opened_at` and, for `recovered` and `threshold_changed`, `closed_at` are
  times of readings. A batch that is uploaded late can open and close an
  alert in the past.
- The server keeps a closed alert for 2 years after `closed_at`.

Example: a plant with the lower threshold 30.0 for soil moisture. The
readings arrive in the order of their times.

| Reading | Soil moisture | Effect |
|---|---|---|
| 1 | 31.0 | None |
| 2 | 28.4 | Alert A opens with `opened_value` 28.4 and `threshold` 30.0; one notification |
| 3 | 27.0 | None. A stays open; no second notification |
| 4 | 27.5, estimated time | None. The reading is not judged |
| 5 | 40.0 | A closes with `recovered` |
| 6 | 29.9 | Alert B opens with a new `id`; one notification |
| 7 | none measured | None. B stays open |
| 8 | 29.0, 2 minutes after a `PUT` removed the threshold | B closes with `threshold_changed` |

## Notification

Each alert leads to one notification to the owner, sent when the alert
opens. Closing an alert sends nothing.

| `notification` | Meaning |
|---|---|
| `pending` | Not yet handed to the push service |
| `sent` | The push service has taken the notification. Whether a phone showed it is not known. |
| `failed` | The push service refused the notification for good, or did not take it within 24 hours |

The notification carries the alert `id` and the `plant_id`, so that a
client can show the alert it belongs to.

## Operations

| Operation | Response |
|---|---|
| `GET /v1/alerts` | `200` with `{"items": [alert, ...], "next": "<cursor>"}` |
| `GET /v1/alerts/{alert_id}` | `200` with the alert |

Parameters of `GET /v1/alerts`:

| Parameter | Default | Content |
|---|---|---|
| `state` | `open` | `open`, `closed` or `all` |
| `plant_id` | all plants of the owner | Only alerts of this plant |
| `opened_after` | none | Only alerts with `opened_at` later than this time |
| `limit` | 1 000 | Items per page, at most 1 000 |
| `cursor` | none | The `next` value of the previous page |

Rules:

- Items are in descending order of `opened_at`.
- `next` is present when more items exist.
- An alert belongs to the owner that the plant had when the alert opened.
- No operation changes an alert. A client cannot close or acknowledge one.
