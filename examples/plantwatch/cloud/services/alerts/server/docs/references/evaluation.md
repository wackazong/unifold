# Evaluation as server expects it

The contract of the need `evaluation`: the function that `server` calls
for every reading. `server` defines the interface it expects; whoever
provides the function is held to it. The terms are cited in
[context](../explanation/context.md).

## The function

`evaluate(reading, state)` returns "decided" or "cannot decide now".

| Argument | Content |
|---|---|
| `reading` | `sensor_id`, `sequence_number`, `time`, `time_estimated` and `values` by quantity name, as the event carried them |
| `state` | The `state` of the last decided result for the same sensor stick, or nothing |

| Part of "decided" | Content |
|---|---|
| `plant` | `plant_id`, `owner_id` and `name` of the plant that the reading belongs to, or nothing |
| `changes` | A list, possibly empty. Each entry has `change` (`open` or `close`), `quantity`, `bound`, `value`, `threshold` if there is one, and for a close the `reason`: `recovered` or `threshold_changed`. |
| `state` | A value that `server` stores and passes back with the next reading of the sensor stick |

"Cannot decide now" carries nothing. `server` keeps its state, leaves the
event unconfirmed and passes the same reading again later.

## Requirements

- The function changes nothing outside its result.
- It never returns `open` for a quantity and bound that are open according
  to `state`, and `close` only for one that is open.
- Given a reading a second time, with the state that the first call
  returned, it returns no changes and the same state.
- `state` is plain data of at most 4 kB that is unchanged after being
  written as JSON and read back. `server` does not look into it.
- A result with changes names a plant.
- The function returns within 20 seconds.

## Examples

| Case | Call | Expected result |
|---|---|---|
| A value beyond a threshold | A reading with soil moisture 28.4 for a plant with the lower threshold 30.0; no alert open in `state` | Decided: the plant, one `open` for `soil_moisture`/`min` with value 28.4 and threshold 30.0, a new state |
| The same reading again | The same reading with the new state | Decided: no changes, the same state |
| Still beyond | A later reading with 27.0 and the new state | Decided: no changes |
| No plant | A reading of a sensor stick that belongs to no plant | Decided: `plant` nothing, no changes |
| Thresholds cannot be had | Any reading | Cannot decide now, within 20 seconds |
