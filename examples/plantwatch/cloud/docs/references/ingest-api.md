# Ingest API

The contract of the capability `ingest-api`. The operation, its bodies, the status values and the rejection codes are defined above this unit and cited in [context](../explanation/context.md). This reference states how `ingest` applies them.

## Operation

| Item | Value |
|---|---|
| Method and path | `POST /v1/sensors/{sensor_id}/batches` |
| Required header | `X-Owner-Id`. Without it: `400` `invalid_request`. |
| Request body | `{"readings": [...]}`, each element one reading |
| Response | `200` with `{"results": [...]}`, one result per reading in the order of the request |
| Health | `GET /healthz`: `200` while the event bus is reachable and the accepted ranges are loaded, else `503` |

## Checks on the request

A failed check ends the request. No reading is looked at.

| Order | Check | On failure |
|---|---|---|
| 1 | The body is at most 1 MB | `413` `payload_too_large` |
| 2 | `sensor_id` is 16 lower-case hex digits | `400` `invalid_request` |
| 3 | The body is a JSON object with an array `readings` | `400` `invalid_request` |
| 4 | `readings` has at most 500 elements | `413` `payload_too_large` |

## Checks on each reading

`ingest` applies the checks in this order to every reading on its own. The first one that fails decides the result.

| Order | Check | Result on failure |
|---|---|---|
| 1 | The element conforms to the reading schema, major version 1. Fields that the format does not define are allowed. | `rejected`, `malformed_reading` |
| 2 | Every measured value lies within the range of its quantity | `rejected`, `value_out_of_range` |
| 3 | The time is at most 24 hours later than the clock of `ingest` | `rejected`, `time_in_future` |
| 4 | The time is at most 90 days earlier than the clock of `ingest` | `rejected`, `too_old` |
| 5 | The sequence number is not in the accepted ranges that `ingest` keeps of the sensor stick and did not occur earlier in the same batch | `duplicate` |

A reading that passes all checks is `new`.

- A reading that states a sensor id of its own which differs from the path is `rejected` with `malformed_reading`.
- A reading without any measured value is valid.
- A duplicate is recognised after the other checks. A reading that was accepted earlier and is sent again in a broken form is `rejected`.

## Accepting

For the new readings of a batch `ingest` does the following before it answers:

- It publishes one event per reading, in ascending order of sequence number ([reading events](reading-events.md)).
- It waits until the event bus has acknowledged every event.
- It records the sequence numbers in the accepted ranges that `ingest` keeps and waits for that acknowledgement too.

## Failures

| Situation | Answer | State afterwards |
|---|---|---|
| The event bus has not acknowledged everything 3 seconds after the request arrived | `503` `unavailable` | Some events of the batch may be published. No reading counts as accepted. The repeated batch publishes them again with the same `id`. |
| `ingest` stops between publishing and recording | none | As above |
| The accepted ranges are not loaded yet after a start | `503` `unavailable` | Nothing happened |

## Timing

`ingest` answers a batch of 500 readings within 2 seconds while the event bus is healthy, and every request within 4 seconds.

## Examples

Cases beyond those of the operation as it is defined above this unit. The accepted ranges of the sensor stick are `[[1, 4711]]` before each case.

| Case | Request | Result | Events published |
|---|---|---|---|
| Out of order in the batch | Readings 4713, 4712 | `new`, `new`, in the order of the request | 4712, then 4713 |
| Twice in one batch | Readings 4712, 4712 | `new`, `duplicate` | 4712 once |
| Known and broken | 4711 with `soil_moisture` 104.2 | `rejected`, `value_out_of_range` | none |
| Other sensor id inside | 4712 that states the sensor id `ffffffffffffffff` | `rejected`, `malformed_reading` | none |
| Sequence number 0 | A reading with sequence number 0 | `rejected`, `malformed_reading` | none |
| No measured value | 4712 without any quantity | `new` | 4712 with empty `values` |
| Unknown field | 4712 with a field `soil_ph` | `new` | 4712; `data.reading` contains `soil_ph` |
| No owner header | Any batch without `X-Owner-Id` | `400` `invalid_request` | none |
| Bus unreachable | Reading 4712 | `503` `unavailable` within 4 seconds | none, or 4712; the repeated batch publishes it again |
