# ingest-api

Contract of `ingest.ingest-api`. The operation, its bodies, the status values and the rejection codes are defined by the public API of plantwatch and cited in [context](../explanation/context.md); this contract states how `ingest` applies them. Notation: HTTP, with JSON bodies as the project conventions define them.
Sources: the public API of plantwatch, the reading schema, the calls between services of `cloud`.

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

A reading that states a sensor id of its own which differs from the path is `rejected` with `malformed_reading`. A reading without any measured value is valid. A duplicate is recognised after the other checks: a reading that was accepted earlier and is sent again in a broken form is `rejected`. For the new readings of a batch, before it answers, `ingest` publishes one event per reading in ascending order of sequence number ([reading events](reading-events.md)), waits until the event bus has acknowledged every event, then records the sequence numbers in the accepted ranges that `ingest` keeps and waits for that acknowledgement too. `ingest` answers a batch of 500 readings within 2 seconds while the event bus is healthy, and every request within 4 seconds.
Errors: `400` `invalid_request` without the owner header or when a request check fails as above; `413` `payload_too_large`; `503` `unavailable` when the event bus has not acknowledged everything 3 seconds after the request arrived, or while the accepted ranges are not loaded yet after a start. After a `503`, or when `ingest` stops between publishing and recording, some events of the batch may be published but no reading counts as accepted; the repeated batch publishes them again with the same `id`.
Examples: cases beyond those of the public API; the accepted ranges of the sensor stick are `[[1, 4711]]` before each case.

| Case | Request | Result | Events published |
|---|---|---|---|
| out of order in the batch | readings 4713, 4712 | `new`, `new`, in the order of the request | 4712, then 4713 |
| twice in one batch | readings 4712, 4712 | `new`, `duplicate` | 4712 once |
| known and broken | 4711 with `soil_moisture` 104.2 | `rejected`, `value_out_of_range` | none |
| other sensor id inside | 4712 that states the sensor id `ffffffffffffffff` | `rejected`, `malformed_reading` | none |
| sequence number 0 | a reading with sequence number 0 | `rejected`, `malformed_reading` | none |
| no measured value | 4712 without any quantity | `new` | 4712 with empty `values` |
| unknown field | 4712 with a field `soil_ph` | `new` | 4712; `data.reading` contains `soil_ph` |
| no owner header | any batch without `X-Owner-Id` | `400` `invalid_request` | none |
| bus unreachable | reading 4712 | `503` `unavailable` within 4 seconds | none, or 4712; the repeated batch publishes it again |

### healthz

Kind: query

```http
GET /healthz
```

Pre: none.
Result: `200` while the event bus is reachable and the accepted ranges are loaded.
Errors: `503` otherwise.
Examples:

| Case | Request | Answer |
|---|---|---|
| healthy | `GET /healthz` | `200` |
| ranges not loaded yet | `GET /healthz` right after a start | `503` |

## Fake

Replays the examples and those of the public API: an HTTP server in the test that answers the requests of the tables and `400` for everything else. Faults it can inject: `503` `unavailable`, no response within 5 seconds.
