# Scenario format

Defines the scenario document: the course of sensor values over simulated
time that the program plays instead of reading sensors. A scenario is one
JSON document. It is the same in a file and in the body of a request to the
[scenario-control API](scenario-control-api.md).

## File

| Property | Value |
|---|---|
| Encoding | JSON in UTF-8 |
| File name | `<name>.scenario.json`, with `<name>` equal to the member `name` |
| Member names | Lower-case with underscores |
| Unknown members | The program rejects the scenario |

## Example

A plant dries out over three days. Light follows a daily cycle. The sensor
stick restarts after two days.

```json
{
  "scenario_version": 1,
  "name": "drying-out",
  "description": "Soil falls from 60 % to 18 % in three days",
  "sensor_id": "00a1b2c3d4e5f607",
  "sampling_interval_s": 900,
  "tracks": {
    "soil_moisture": {
      "points": [
        {"at_s": 0, "value": 60.0},
        {"at_s": 259200, "value": 18.0}
      ]
    },
    "light": {
      "repeat_s": 86400,
      "points": [
        {"at_s": 0, "value": 0, "step": true},
        {"at_s": 21600, "value": 0},
        {"at_s": 43200, "value": 12000},
        {"at_s": 64800, "value": 0}
      ]
    },
    "temperature": {
      "points": [{"at_s": 0, "value": 21.4}]
    }
  },
  "events": [
    {"at_s": 172800, "type": "restart"}
  ]
}
```

## Top-level members

| Member | Type | Required | Default | Meaning |
|---|---|---|---|---|
| `scenario_version` | integer | yes | | Version of this format: 1 |
| `name` | string | yes | | Lower-case letters, digits and `-`, at most 40 characters |
| `description` | string | no | empty | For people |
| `sensor_id` | string | no | `e0e0e0e0e0e00001` | Sensor id of the simulated sensor stick, 16 lower-case hex digits |
| `sampling_interval_s` | integer | no | 900 | Sampling interval in simulated seconds, 300 to 3600 |
| `quantities` | array of strings | no | all three | Quantities the simulated sensor stick can measure |
| `start` | object | no | see below | Counters at the start of the scenario |
| `bonding` | string | no | `always` | `always`: a new bond is accepted at any time. `after-start`: only in the first 300 simulated seconds after each start. |
| `tracks` | object | yes | | One member per quantity, see below |
| `events` | array | no | empty | Things that happen at a given time, see below |

The names of the quantities are `soil_moisture`, `light` and `temperature`.

### `start`

| Member | Type | Default | Meaning |
|---|---|---|---|
| `boot_counter` | integer, 1 to 65 535 | 1 | Boot counter at the start |
| `first_sequence_number` | integer, 1 to 4 294 967 295 | 1 | Sequence number of the first reading |

## Time

All times in a scenario are whole simulated seconds since the scenario was
loaded, in members named `at_s`. The simulated sensor stick takes a reading
when its seconds since boot are 0 and then at every multiple of the
sampling interval. The first reading therefore exists as soon as the
scenario is loaded.

## Tracks

A track gives the value of one quantity at every moment.

| Member | Type | Required | Meaning |
|---|---|---|---|
| `points` | array of points | yes | At least one point, in ascending order of `at_s` |
| `repeat_s` | integer | no | The track repeats with this period. Every `at_s` of the track is below it. |

A point:

| Member | Type | Required | Meaning |
|---|---|---|---|
| `at_s` | integer, 0 or more | yes | Time of the point |
| `value` | number or `null` | yes | Value in the unit of the quantity. `null`: the quantity cannot be measured from here on. |
| `step` | boolean | no | `true`: the value holds until the next point. Default `false`. |

The value between two points:

| Situation | Value |
|---|---|
| Before the first point | The value of the first point |
| Between two points with numbers | On the straight line between them |
| After a point with `step` | The value of that point, until the next point |
| After a point with `null` | Absent, until the next point |
| After the last point, without `repeat_s` | The value of the last point |
| After the last point, with `repeat_s` | The line towards the first point of the next period |

The program rounds the value to the resolution of the quantity, half away
from zero. A reading in which a quantity is absent has that quantity
absent on the radio link, not zero.

A quantity without a track is absent in every reading. A quantity that is
not listed in `quantities` must not have a track.

| Quantity | Unit | Allowed values | Resolution |
|---|---|---|---|
| `soil_moisture` | percent | 0 to 100 | 0.1 |
| `light` | lux | 0 to 100 000 | 1 |
| `temperature` | °C | -20 to 60 | 0.1 |

## Events

An event has a time `at_s` and a `type`. Events with the same time happen
in the order of the array, before the reading of that time is taken.

| `type` | Further members | Effect |
|---|---|---|
| `restart` | `skip_sequence_numbers`: integer, default 0 | The simulated sensor stick restarts: the boot counter rises by one, seconds since boot start at 0, a connection is dropped. Stored readings and delivered marks stay. The next reading gets the next sequence number plus `skip_sequence_numbers`. |

## When the program rejects a scenario

The program checks the whole document when it is loaded and rejects it as
a whole. The earlier scenario stays loaded.

- A required member is missing, a member is unknown, or a type is wrong.
- `scenario_version` is not 1.
- A value lies outside the allowed values of its quantity.
- Points of a track are not in ascending order, or two have the same time.
- An `at_s` of a repeating track is not below `repeat_s`.
- A quantity has a track but is not in `quantities`.
