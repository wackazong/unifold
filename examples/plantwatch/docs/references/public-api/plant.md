# plant

Kind: type

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
| `latest_reading` | server | The reading with the latest time among the raw readings of the plant, in the form that the [reading schema](../reading-schema.md) defines. Absent when the plant has no reading of the last 90 days. |
| `created_at`, `updated_at` | server | Times of the first and the latest `PUT` |

The quantities are `soil_moisture`, `light` and `temperature`, in the units of the project conventions. `min` is the threshold below which the plant needs attention, `max` the one above which it does. A sensor stick is attached to at most one plant, across all owners.
