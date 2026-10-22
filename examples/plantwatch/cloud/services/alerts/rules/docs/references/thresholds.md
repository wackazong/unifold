# Thresholds lookup as rules expects it

The contract of the need `thresholds`: the interface through which `rules`
asks to which plant a sensor stick belongs and what the thresholds of that
plant are. `rules` defines it; whoever provides it is held to it.

## The function

`lookup(sensor_id)` returns one of three answers.

| Answer | Content | What `rules` does |
|---|---|---|
| `attached` | `plant` and `thresholds` | Judges the reading |
| `unattached` | Nothing | Decides that the reading belongs to no plant |
| `unavailable` | Nothing | Returns "cannot decide now" |

| Part of `attached` | Content |
|---|---|
| `plant.plant_id`, `plant.owner_id` | UUIDs in lower-case text form |
| `plant.name` | The name of the plant |
| `thresholds` | Per quantity name an object with `min`, `max` or both, as numbers in the unit of the quantity. A quantity without thresholds is absent. The object may be empty. |

## Requirements

- `lookup` gives one of the three answers and raises no error.
- An `attached` or `unattached` answer shows the plants as they were at
  most 60 seconds before the call.
- `lookup` returns within 18 seconds, with `unavailable` if it has nothing
  better by then.
- `lookup` changes nothing that `rules` can observe. `rules` may call it
  for the same sensor id any number of times.
- `thresholds` may contain quantity names that `rules` does not judge.
  `rules` ignores them.

## Examples

| Case | Call | Expected answer |
|---|---|---|
| A plant with a lower threshold | `lookup("00a1b2c3d4e5f607")` | `attached`, plant `0b6f6f0e-…` of owner `5b0e2d0a-…` named "Monstera in the hall", thresholds `{soil_moisture: {min: 30.0}}` |
| A plant without thresholds | The same for such a plant | `attached` with thresholds `{}` |
| A sensor stick in no pot | `lookup("ffffffffffffffff")` | `unattached` |
| The source cannot be reached | Any call | `unavailable` within 18 seconds |
| A threshold was changed 61 seconds ago | Any call for its plant | `attached` with the new threshold |
