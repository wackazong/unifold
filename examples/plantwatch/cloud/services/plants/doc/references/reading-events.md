# Reading events as plants expects them

The contract of the need `reading-events`: what `plants` requires of the
stream from which it builds the history. `plants` defines it; whoever
provides the stream is held to it. The envelope of an event is cited in
[context](../context.md).

## What plants reads

| Field | Requirement |
|---|---|
| `type` | `reading.accepted`. `plants` confirms and counts an event of another type and stores nothing. |
| `data.sensor_id`, `data.sequence_number` | The identity of the reading |
| `data.time` | The time of the reading |
| `data.time_estimated` | `true` if that time was estimated |
| `data.values` | The measured values under the names `soil_moisture`, `light` and `temperature`. A quantity that was not measured is absent. Every value lies within the range of its quantity. Other names may occur. |
| `data.reading` | The reading as it was uploaded, a JSON object. `plants` stores and returns it unread. |

## Key, order, delivery

| Aspect | Requirement |
|---|---|
| Key | The sensor id |
| Order | None. `plants` builds the same history from any order of events. |
| Delivery | At least once. Every accepted reading appears on the stream. |
| Retention | An event stays available for at least 7 days, so that `plants` misses nothing after an outage of that length. |
| Repeats | Allowed. Two events with the same sensor id and sequence number describe the same reading. |

## Examples

The sensor stick `00a1b2c3d4e5f607` is attached to the plant P.

| Case | Events received | History of P afterwards |
|---|---|---|
| One reading | 4711, time 14:15, `soil_moisture` 41.9 | One raw reading; hour 14:00 has `count` 1 and mean 41.9 |
| Repeat | 4711 again | Unchanged |
| Old after new | 4712 at 14:30, then 4710 at 14:00 | Three raw readings in the order 4710, 4711, 4712; hour 14:00 has `count` 3 |
| Not measured | 4713 without `light` | The raw reading has no light; the mean of light does not count it |
| Unknown name | 4714 with `soil_ph` in `values` | Stored; `soil_ph` appears only inside the raw reading |
| Unknown type | An event of the type `reading.withdrawn` | Unchanged; the event is confirmed and counted |
