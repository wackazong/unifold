# Evaluation

The contract of the port `evaluation` and the rules by which `rules`
judges a reading. What a client of the product sees of these rules is
cited in [context](../context.md); this reference adds the exact
procedure, the margins and the state.

## The function

`evaluate(reading, state)` returns a result.

| Input | Content |
|---|---|
| `reading.sensor_id` | The sensor stick |
| `reading.sequence_number` | The sequence number |
| `reading.time` | The time of the reading |
| `reading.time_estimated` | `true` if the time was estimated |
| `reading.values` | The measured values by name: `soil_moisture`, `light`, `temperature`. A quantity that was not measured is absent. |
| `state` | The `state` of the previous result for the same sensor stick, or nothing |

| Result | Content |
|---|---|
| Decided | `plant`, `changes`, `state` |
| Cannot decide now | Nothing else. The caller keeps its state and passes the same reading again later. |

| Part of a decided result | Content |
|---|---|
| `plant` | `plant_id`, `owner_id`, `name` of the plant the sensor stick is attached to; nothing if it is attached to none |
| `changes` | A list, possibly empty, of changes |
| `state` | The value to pass with the next reading of this sensor stick |

| Field of a change | Content |
|---|---|
| `change` | `open` or `close` |
| `quantity`, `bound` | What the alert is about; `bound` is `min` or `max` |
| `value` | The judged value |
| `threshold` | The threshold the value was compared with. Absent in a close because the threshold is gone. |
| `reason` | Only in a close: `recovered` or `threshold_changed` |

## Order of an evaluation

| Step | Condition or action | Outcome |
|---|---|---|
| 1 | `time_estimated` is `true` | Decided: no changes, `state` unchanged, `plant` nothing. No lookup. |
| 2 | `state` exists and its last time is not earlier than `reading.time` | As step 1 |
| 3 | Look up plant and thresholds for the sensor id | Lookup fails: cannot decide now |
| 4 | The sensor stick is attached to no plant | Decided: `plant` nothing, no changes, empty `state` |
| 5 | The plant differs from the plant in `state` | Continue with an empty `state` for the new plant. Nothing is closed for the old plant. |
| 6 | Add the light value of the reading to the light memory | |
| 7 | Judge every quantity and bound that has a threshold or is open in `state` | The changes |
| 8 | Set the last time to `reading.time` | Decided: `plant`, changes, new `state` |

## Judged value

| Quantity | Judged value | Not judged when |
|---|---|---|
| `soil_moisture` | The value of the reading | The reading lacks the value |
| `temperature` | The value of the reading | The reading lacks the value |
| `light` | The highest light value in the light memory, which covers the hour of the reading and the 24 full hours before it | The reading lacks the value, or the first judged reading for this plant is less than 24 hours older than this one |

A quantity that is not judged causes no change. What is open stays open.

## Opening and closing

For a bound, let v be the judged value, T the threshold now, T0 the
threshold remembered in `state` for an open alert, and m the margin.

| Bound | Open in `state` | Condition | Change |
|---|---|---|---|
| `min` | no | T exists and v < T | `open` with v and T |
| `min` | yes | T does not exist | `close`, `threshold_changed` |
| `min` | yes | T differs from T0 and v >= T | `close`, `threshold_changed` |
| `min` | yes | T differs from T0 and v < T | none; `state` remembers T as T0 |
| `min` | yes | T equals T0 and v >= T + m | `close`, `recovered` |
| `min` | yes | T equals T0 and v < T + m | none |
| `max` | no | T exists and v > T | `open` with v and T |
| `max` | yes | T does not exist | `close`, `threshold_changed` |
| `max` | yes | T differs from T0 and v <= T | `close`, `threshold_changed` |
| `max` | yes | T differs from T0 and v > T | none; `state` remembers T as T0 |
| `max` | yes | T equals T0 and v <= T - m | `close`, `recovered` |
| `max` | yes | T equals T0 and v > T - m | none |

## Margins

| Quantity | Margin m |
|---|---|
| `soil_moisture` | 5.0 percentage points |
| `temperature` | 1.0 degree Celsius |
| `light` | 10 percent of the threshold, at least 50 lux |

Why closing has a margin and opening has none is recorded in
[0001](../decisions/0001-flapping-is-prevented-by-a-margin-on-closing.md).

## State

The state is a JSON object. Its caller treats it as opaque.

```json
{
  "v": 1,
  "plant_id": "0b6f6f0e-2c1d-4f7a-9d42-6f1f0c8a7e11",
  "since": "2026-10-01T08:00:00Z",
  "last": "2026-10-05T14:15:00Z",
  "open": [
    {"quantity": "soil_moisture", "bound": "min", "threshold": 30.0}
  ],
  "light": [["2026-10-05T13:00:00Z", 2400], ["2026-10-05T14:00:00Z", 1800]]
}
```

| Field | Content |
|---|---|
| `v` | Version of the form, now 1 |
| `plant_id` | The plant the state is about |
| `since` | Time of the first judged reading for this plant |
| `last` | Time of the last judged reading |
| `open` | The quantities and bounds that are open, each with T0 |
| `light` | The light memory: per full hour the highest light value, for at most 25 hours |

An empty state is nothing, or an object without `plant_id`. A state is at
most 4 kB long.

## Lookup of thresholds

| Answer of whoever provides `thresholds` | Meaning for `rules` |
|---|---|
| A plant with thresholds | Used, and reused for the same sensor id for at most 60 seconds |
| The sensor stick is attached to no plant | Step 4; reused for at most 60 seconds |
| An error, or no answer after the allowed repeats | Cannot decide now; nothing is reused |
