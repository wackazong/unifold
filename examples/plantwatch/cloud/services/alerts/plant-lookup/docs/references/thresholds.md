# Thresholds lookup

The contract of the capability `thresholds`: the function `lookup`, how
`plant-lookup` turns the answers of whoever provides `plants-api` into its
three answers, and how long it keeps them. The rules for calls that it
follows are cited in [context](../explanation/context.md).

## The function

`lookup(sensor_id)` returns one of three answers.

| Answer | Content |
|---|---|
| `attached` | `plant` and `thresholds` |
| `unattached` | Nothing |
| `unavailable` | Nothing |

| Part of `attached` | Content |
|---|---|
| `plant.plant_id`, `plant.owner_id` | UUIDs in lower-case text form |
| `plant.name` | The name of the plant, 1 to 60 characters |
| `thresholds` | Per quantity name an object with `min`, `max` or both, as numbers in the unit of the quantity. A quantity without thresholds is absent. A plant without thresholds has an empty object. |

`lookup` raises no error and has no effect that its caller can observe.

## From the registry to an answer

One request is a `GET` of the lookup by sensor id, without an owner header.

| What comes back | Answer of `lookup` | Kept |
|---|---|---|
| `200` with a plant | `attached` | 60 seconds |
| `404` with the code `not_found` | `unattached` | 60 seconds |
| `503`, no connection, or no response within 5 seconds | Repeat, see below | no |
| Any other status, or a body that cannot be read | `unavailable` | no |

- A failed request is repeated at most twice, after 0.2 and after 1
  second. After the third failure the answer is `unavailable`.
- A `sensor_id` that is not 16 lower-case hex digits gets `unattached`
  without a request.
- Quantity names and numbers in `thresholds` are passed on unchanged.

## Kept answers

- An answer is kept per sensor id, in the memory of the instance, with the
  time at which the request for it was sent.
- A call within 60 seconds after that time is answered from memory. A
  later call sends a new request; the old answer is not used again.
- At most 10 000 answers are kept. Beyond that the oldest is dropped.
- Two calls for the same sensor id at the same moment share one request.

## Timing

| Situation | `lookup` returns within |
|---|---|
| Answer from memory | 1 ms |
| The registry answers | The time of one request, at most 5 seconds |
| The registry does not answer | 17 seconds: three waits of 5 seconds and the pauses |

## Examples

The registry holds the plant P of owner A with the sensor stick
`00a1b2c3d4e5f607` and the lower threshold 30.0 for soil moisture.

| Case | Call | Requests sent | Answer |
|---|---|---|---|
| First call | `lookup("00a1b2c3d4e5f607")` at 09:00:00 | 1 | `attached`, P, A, `{soil_moisture: {min: 30.0}}` |
| Again soon | The same at 09:00:59 | 0 | The same |
| After a change | The threshold is set to 35.0 at 09:00:10; call at 09:01:01 | 1 | `attached` with `min` 35.0 |
| No thresholds | A plant without thresholds | 1 | `attached` with `{}` |
| Not attached | `lookup("ffffffffffffffff")` | 1 | `unattached` |
| Malformed id | `lookup("00A1")` | 0 | `unattached` |
| Short outage | `503`, then `200` | 2 | `attached`, after about 0.2 seconds |
| Outage | The registry refuses connections; an answer from 09:00:00 exists; call at 09:02:00 | 3 | `unavailable` |
| Unknown quantity | The plant has thresholds for `soil_ph` | 1 | `attached`; `thresholds` contains `soil_ph` |
