# Reading events as server expects them

The contract of the need `reading-events`: what `server` requires of the
stream of accepted readings. `server` defines it; whoever provides the
stream is held to it. The envelope of an event is cited in
[context](../context.md).

## What server reads

| Field | Requirement |
|---|---|
| `type` | `reading.accepted`. `server` confirms and counts an event of another type and does nothing else with it. |
| `data.sensor_id`, `data.sequence_number` | The identity of the reading |
| `data.time` | The time of the reading |
| `data.time_estimated` | `true` if that time was estimated |
| `data.values` | The measured values by quantity name. A quantity that was not measured is absent. |

`server` hands these fields to `evaluation` as one reading and looks at no
value itself.

## Key, order, delivery

| Aspect | Requirement |
|---|---|
| Key | The sensor id. Events of one sensor stick go to one instance at a time. |
| Order | Events of one sensor stick arrive in the order in which the readings were accepted. A reading that arrives after a newer one of the same sensor stick is not judged, so a wrong order would lose alerts. |
| Delivery | At least once. Every accepted reading appears on the stream. |
| Retention | An event stays available for at least 7 days, so that `server` misses nothing after an outage of that length. |
| Repeats | Allowed. A repeated event describes the same reading and changes no alert. |

## Examples

| Case | Events received for one sensor stick | What `server` does |
|---|---|---|
| In order | 4711, then 4712 | Has both judged, in this order |
| Repeat | 4711, 4712, then 4711 again | Has all three judged; the third leads to no change |
| Late batch | 4800, then 4700, which was taken earlier | Has both judged; 4700 leads to no change |
| Unknown type | An event of the type `reading.withdrawn` | Confirms and counts it |
| Outage of 2 days | The events of those days, after `server` is back | Has them judged in order; no event is missing |
