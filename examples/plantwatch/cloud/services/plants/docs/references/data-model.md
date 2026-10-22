# Data model of plants

What `plants` stores in its database schema and how long. It is internal:
only `plants` reads these tables ([context](../explanation/context.md)). The reasons
are in the [decisions](../decisions/index.md).

## Tables

| Table | One row per | Key |
|---|---|---|
| `plant` | plant | `plant_id` |
| `reading` | accepted reading that belongs to a plant | `sensor_id`, `sequence_number` |
| `hour_aggregate` | plant and hour with at least one reading | `plant_id`, `hour_start` |

### `plant`

| Column | Content |
|---|---|
| `plant_id` | UUID chosen by the client |
| `owner_id` | UUID of the owner. Never changes. |
| `name` | 1 to 60 characters |
| `sensor_id` | The attached sensor stick, or empty. Unique among all rows that have one. |
| `thresholds` | The thresholds as the JSON object of the API |
| `created_at`, `updated_at` | Times of the first and the latest `PUT` |

### `reading`

| Column | Content |
|---|---|
| `sensor_id`, `sequence_number` | The identity of the reading |
| `plant_id` | The plant to which the sensor stick was attached when the event was handled |
| `time`, `time_estimated` | The time of the reading and its flag |
| `soil_moisture`, `light`, `temperature` | The values from the event. Empty for a quantity that was not measured. |
| `reading` | The uploaded reading as JSON, as the event carried it |

### `hour_aggregate`

| Column | Content |
|---|---|
| `plant_id`, `hour_start` | The plant and the full hour, UTC |
| `count` | Number of readings of the plant in that hour |
| `<quantity>_min`, `<quantity>_mean`, `<quantity>_max` | Per quantity; empty when no reading of the hour measured it |

## How an event changes the tables

`plants` handles one event of an accepted reading in one transaction.

| Condition | Change |
|---|---|
| The sensor stick is attached to no plant | None. The event is confirmed and counted as unattached. |
| The time of the reading is more than 90 days in the past | None. The event is confirmed. |
| A row with the same `sensor_id` and `sequence_number` exists | None. The event is confirmed. |
| Otherwise | A row in `reading`. The row of `hour_aggregate` for the plant and the hour of the reading is computed anew from all rows of `reading` of that plant and hour. |

`latest_reading` of a plant is not stored. It is the row of `reading` of
the plant with the latest `time`.

## Derived values

| Value | Computed |
|---|---|
| Hourly `min`, `mean`, `max` | From the raw readings of the hour, when a reading of that hour is stored |
| Daily aggregate | At query time from the up to 24 hourly aggregates of the UTC day; `mean` is weighted by `count` |

## Retention

A job runs once per hour.

| Rows | Deleted when |
|---|---|
| `reading` | `time` is more than 90 days in the past |
| `hour_aggregate` | `hour_start` is more than 2 years in the past |
| `reading` and `hour_aggregate` of a plant | The plant is deleted, in the same transaction |

An hourly aggregate is final once its raw readings are deleted.

## Size

| Table | Rows per plant, at most |
|---|---|
| `reading` | 25 920 (90 days at a sampling interval of 5 minutes) |
| `hour_aggregate` | 17 520 (2 years) |
