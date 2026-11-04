# ingest-api

Contract of `ingest.ingest-api`. The operation, its bodies, the status values and the rejection codes are defined by the public API of plantwatch and cited in [context](../explanation/context.md); this contract states how `ingest` applies them. Notation: HTTP, with JSON bodies as the project conventions define them.
Sources: the public API of plantwatch, the reading schema, the calls between services of `cloud`.
Binding: http

## Use

A caller that acts for an owner uploads a batch of readings of one sensor stick, with `X-Owner-Id`. The container host and other services ask `healthz`. The connection has no state: any part may be called at any time. A batch may be sent again after `503` or a lost response.

## Qualities

| Aspect | Guarantee |
|---|---|
| latency | a batch of 500 readings is answered within 2 seconds while the event bus is healthy, and every request within 4 seconds |
| limits | a body of at most 1 MB with at most 500 readings; for a sensor stick with more than 1 000 gaps in its sequence numbers, a reading in an old gap can be reported as `duplicate` without having been accepted |
| idempotency | a batch may be sent again; a reading that was accepted earlier is reported as `duplicate`; every operation is safe to repeat, because the gateway repeats a failed call |
| timeout | the gateway waits 5 seconds for an answer and then counts the call as failed |
| delivery | for every new reading of a batch, one event is published and acknowledged by the event bus before the batch is answered |
| availability | `503` `unavailable` when the event bus has not acknowledged everything 3 seconds after the request arrived, or while the accepted ranges are not loaded yet after a start; `ingest` depends on nothing but the event bus and answers uploads with `200` while no subscriber of its events is running |

## Parts

### upload-batch

Kind: command

```http
POST /v1/sensors/{sensor_id}/batches
X-Owner-Id: <owner id>

{"readings": [ ...one reading each... ]}
```

Pre: `X-Owner-Id` is present; the request passes these checks in this order, and a failed check ends the request without any reading being looked at:

| Order | Check | On failure |
|---|---|---|
| 1 | the body is at most 1 MB | `413` `payload_too_large` |
| 2 | `sensor_id` is 16 lower-case hex digits | `400` `invalid_request` |
| 3 | the body is a JSON object with an array `readings` | `400` `invalid_request` |
| 4 | `readings` has at most 500 elements | `413` `payload_too_large` |

Result: `200` with `{"results": [...]}`, one result per reading in the order of the request. `ingest` applies these checks to every reading on its own, in this order; the first one that fails decides the result, and a reading that passes all is `new`:

| Order | Check | Result on failure |
|---|---|---|
| 1 | the element conforms to the reading schema, major version 1; fields that the format does not define are allowed | `rejected`, `malformed_reading` |
| 2 | every measured value lies within the range of its quantity | `rejected`, `value_out_of_range` |
| 3 | the time is at most 24 hours later than the clock of `ingest` | `rejected`, `time_in_future` |
| 4 | the time is at most 90 days earlier than the clock of `ingest` | `rejected`, `too_old` |
| 5 | the sequence number is not in the accepted ranges that `ingest` keeps of the sensor stick and did not occur earlier in the same batch | `duplicate` |

A reading that states a sensor id of its own which differs from the path is `rejected` with `malformed_reading`. A reading without any measured value is valid. A duplicate is recognised after the other checks: a reading that was accepted earlier and is sent again in a broken form is `rejected`. For the new readings of a batch, before it answers, `ingest` publishes one event per reading in ascending order of sequence number ([reading events](reading-events.md)), waits until the event bus has acknowledged every event, then records the sequence numbers in the accepted ranges that `ingest` keeps and waits for that acknowledgement too.
Errors: `400` `invalid_request` without the owner header or when a request check fails as above; `413` `payload_too_large`; `503` `unavailable` when the event bus has not acknowledged everything 3 seconds after the request arrived, or while the accepted ranges are not loaded yet after a start. After a `503`, or when `ingest` stops between publishing and recording, some events of the batch may be published but no reading counts as accepted; the repeated batch publishes them again with the same `id`.
Examples: cases beyond those of the public API; the accepted ranges of the sensor stick are `[[1, 4711]]` before each case, and the expected result names the events published.

| Case | Given | Input | Expected |
|---|---|---|---|
| out of order in the batch | | a batch with the readings 4713, 4712 | `200`: `new`, `new`, in the order of the request; events 4712, then 4713 |
| twice in one batch | | a batch with the readings 4712, 4712 | `200`: `new`, `duplicate`; one event, 4712 |
| known and broken | | 4711 with `soil_moisture` 104.2 | `200`: `rejected`, `value_out_of_range`; no event |
| other sensor id inside | | 4712 that states the sensor id `ffffffffffffffff` | `200`: `rejected`, `malformed_reading`; no event |
| sequence number 0 | | a reading with sequence number 0 | `200`: `rejected`, `malformed_reading`; no event |
| no measured value | | 4712 without any quantity | `200`: `new`; the event 4712 with empty `values` |
| unknown field | | 4712 with a field `soil_ph` | `200`: `new`; the event 4712, whose `data.reading` contains `soil_ph` |
| no owner header | | any batch without `X-Owner-Id` | `400` `invalid_request`; no event |
| bus unreachable | the event bus cannot be reached | a batch with the reading 4712 | `503` `unavailable` within 4 seconds; no event, or the event 4712, which the repeated batch publishes again |

### healthz

Kind: query

```http
GET /healthz
```

Pre: none.
Result: `200` while the event bus is reachable and the accepted ranges are loaded.
Errors: `503` otherwise.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| healthy | the event bus is reachable and the ranges are loaded | `GET /healthz` | `200` |
| ranges not loaded yet | `ingest` has just started | `GET /healthz` | `503` |

## Fake

Replays the examples and those of the public API: an HTTP server in the test that answers the requests of the tables and `400` for everything else. Faults it can inject: `503` `unavailable`, no response within 5 seconds.
