# evaluation

Contract of `rules.evaluation`: the function `evaluate` and the rules by which `rules` judges a reading. What a client of the product sees of these rules is cited in [context](../explanation/context.md); this contract adds the exact procedure, the margins and the state. Why closing has a margin and opening has none is recorded in decision 0001 of `rules`. Notation: wit.
Sources: the alert as the public API of plantwatch defines it; decision 0001 of `rules`.

## Parts

### evaluate

Kind: query

```wit
evaluate: func(reading: reading, state: option<state>) -> evaluation-result;
```

Pre: `state` is the `state` of the previous result for the same sensor stick, or nothing; the caller passes the readings of one sensor stick one after the other and hands the state back exactly as returned. `evaluate` cannot detect a state that belongs to another sensor stick.
Result: decided, with `plant`, `changes` and `state`, or cannot decide now. The same reading, the same state and the same answer of `thresholds` give the same result: `evaluate` uses no clock and no random value, keeps nothing between calls, and does nothing outside its result but one call of `thresholds`, whose answer it uses as it is given. A lost state makes `evaluate` start afresh: an alert that was open can open again. An evaluation takes at most 10 ms beyond the time that the call of `thresholds` takes. The steps, in order:

| Step | Condition or action | Outcome |
|---|---|---|
| 1 | `time_estimated` is `true` | decided: no changes, `state` unchanged, `plant` nothing; `thresholds` is not called |
| 2 | `state` exists and its last time is not earlier than `reading.time` | as step 1 |
| 3 | call `thresholds` with the sensor id, once | answer `unavailable`: cannot decide now |
| 4 | the answer is `unattached` | decided: `plant` nothing, no changes, empty `state` |
| 5 | the plant differs from the plant in `state` | continue with an empty `state` for the new plant; nothing is closed for the old plant |
| 6 | add the light value of the reading to the light memory | |
| 7 | judge every quantity and bound that has a threshold or is open in `state` | the changes |
| 8 | set the last time to `reading.time` | decided: `plant`, changes, new `state` |

The judged value per quantity, and when it is not judged; a quantity that is not judged causes no change, and what is open stays open:

| Quantity | Judged value | Not judged when |
|---|---|---|
| `soil_moisture` | the value of the reading | the reading lacks the value |
| `temperature` | the value of the reading | the reading lacks the value |
| `light` | the highest light value in the light memory, which covers the hour of the reading and the 24 full hours before it | the reading lacks the value, or the first judged reading for this plant is less than 24 hours older than this one |

Opening and closing, for a bound with the judged value v, the threshold now T, the threshold remembered in `state` for an open alert T0, and the margin m:

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

| Quantity | Margin m |
|---|---|
| `soil_moisture` | 5.0 percentage points |
| `temperature` | 1.0 degree Celsius |
| `light` | 10 percent of the threshold, at least 50 lux |

Errors: none; `cannot-decide` is a result, not an error. The caller keeps its state and passes the same reading again later.
Examples: one sensor stick, attached to the plant P with the lower threshold 30.0 for soil moisture; each call gets the state that the call before it returned.

| Call | Reading | Answer of `thresholds` | Result |
|---|---|---|---|
| 1 | 14:00, 31.0, no state | `attached` P, `min` 30.0 | P, no changes |
| 2 | 14:15, 28.4 | the same | P, `open` `soil_moisture`/`min`, value 28.4, threshold 30.0 |
| 3 | 14:30, 33.0 | the same | P, no changes: 33.0 is below 30.0 + 5.0 |
| 4 | 14:30, 33.0 again | not called | no changes, state unchanged |
| 5 | 14:45, 35.0 | the same | P, `close` `soil_moisture`/`min`, `recovered`, value 35.0 |
| 6 | 15:00, 29.0, estimated time | not called | no changes, state unchanged |
| 7 | 15:00, 29.0 | `unavailable` | cannot decide now |
| 8 | 15:00, 29.0 | `attached` P, `min` 30.0 | P, `open` `soil_moisture`/`min`, value 29.0, threshold 30.0 |
| 9 | 15:15, 29.5 | `attached` P, thresholds `{}` | P, `close` `soil_moisture`/`min`, `threshold_changed`, no threshold |
| 10 | 15:30, 29.5 | `unattached` | `plant` nothing, no changes, empty state |
| light 1 | 02:00 of the next day, light 0; lower threshold 800 lux; the plant has been judged for two days; 2 400 lux were measured at 13:00 | `attached` P, `light` `min` 800 | no changes: the judged value is 2 400 |
| light 2 | 14:00 of the next day, light 600, nothing brighter since 14:00 of the day before | the same | `open` `light`/`min`, value 600, threshold 800 |

### reading

Kind: type

```wit
record reading {
  sensor-id: string,
  sequence-number: u32,
  time: string,
  time-estimated: bool,
  values: list<tuple<string, f64>>,
}
```

| Field | Content |
|---|---|
| sensor-id | the sensor stick |
| sequence-number | the sequence number |
| time | the time of the reading |
| time-estimated | `true` if the time was estimated |
| values | the measured values by name: `soil_moisture`, `light`, `temperature`; a quantity that was not measured is absent |

### evaluation-result

Kind: type

```wit
variant evaluation-result {
  decided(decision),
  cannot-decide,
}
record decision { plant: option<plant-ref>, changes: list<change>, state: state }
record plant-ref { plant-id: string, owner-id: string, name: string }
```

| Part of a decided result | Content |
|---|---|
| plant | `plant_id`, `owner_id`, `name` of the plant the sensor stick is attached to; nothing if it is attached to none |
| changes | a list, possibly empty, of changes |
| state | the value to pass with the next reading of this sensor stick |

### change

Kind: type

```wit
record change {
  change: string,
  quantity: string,
  bound: string,
  value: f64,
  threshold: option<f64>,
  reason: option<string>,
}
```

| Field | Content |
|---|---|
| change | `open` or `close` |
| quantity, bound | what the alert is about; `bound` is `min` or `max` |
| value | the judged value |
| threshold | the threshold the value was compared with; absent in a close because the threshold is gone |
| reason | only in a close: `recovered` or `threshold_changed` |

### state

Kind: type

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

The state is a JSON object of at most 4 kB that its caller treats as opaque. An empty state is nothing, or an object without `plant_id`.

| Field | Content |
|---|---|
| v | version of the form, now 1 |
| plant_id | the plant the state is about |
| since | time of the first judged reading for this plant |
| last | time of the last judged reading |
| open | the quantities and bounds that are open, each with T0 |
| light | the light memory: per full hour the highest light value, for at most 25 hours |

## Fake

Replays the examples: a test of the consumer scripts the result per reading. Any other call fails with `unexpected-call`. Faults it can inject: `cannot-decide` for the next call.
