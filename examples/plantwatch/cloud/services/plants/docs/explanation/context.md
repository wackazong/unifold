# Context of plants

What this unit inherits from the units above. This is the only file of the unit that links upward. Each item is restated so that the unit can be understood when the link is not available.

## From cloud

### [cloud/0001 Services learn about readings through events, not calls](../../../../docs/decisions/0001-services-learn-about-readings-through-events.md)
<!-- unifold:cites sha=47d0b62c -->

Says: accepted readings are announced as events on a durable bus. State that changes rarely, such as thresholds, is asked for with a call.

Here: `plants` builds history as a subscriber. It serves thresholds by call and announces no changes of plants.

### [cloud/0002 Each service owns its data and nobody else reads it](../../../../docs/decisions/0002-each-service-owns-its-data.md)
<!-- unifold:cites sha=00e4a092 -->

Says: one schema per service. What another service needs, it gets through a capability.

Here: plants and history are reachable only through `plants-api`. That is why the lookup by sensor id exists.

### [cloud/0004 Every event consumer is idempotent](../../../../docs/decisions/0004-every-event-consumer-is-idempotent.md)
<!-- unifold:cites sha=02a8c4c1 -->

Says: events arrive at least once. A consumer's result is the same when an event arrives again, and it confirms only after its change is durable.

Here: the key of a stored reading is sensor id and sequence number. Aggregates are recomputed, never added to.

### [cloud: events between services](../../../../docs/references/events.md)
<!-- unifold:cites sha=0f4bf135 -->

Says: a subscription is named after its service. A consumer confirms an event it can never handle and leaves one unconfirmed that fails for a passing reason.

Here: the subscription is named `plants`. Events of an unknown type are confirmed and counted.

### [cloud: calls between services](../../../../docs/references/service-calls.md)
<!-- unifold:cites sha=f87b1f71 -->

Says: a public operation keeps its path and requires `X-Owner-Id`; an internal one lies below `/internal/v1/` without owner. Services answer `GET /healthz`.

Here: the two groups of operations of `plants-api`, and its health check.

### [cloud: public API, plants](../../../../../docs/references/public-api/plant.md)
<!-- unifold:cites sha=66992485 -->

Says, as the contract that this unit implements:

- A plant has `id`, `name` (1 to 60 characters), an optional `sensor_id`, optional `thresholds` with `min`, `max` or both per quantity, and the server fields `latest_reading`, `created_at` and `updated_at`.
- A sensor stick is attached to at most one plant across all owners.

Here: the plant as `plants` stores and returns it; `list-plants` and `get-plant` of the same contract return it as it is.

### [cloud: public API, put a plant](../../../../../docs/references/public-api/put-plant.md)
<!-- unifold:cites sha=cb997ef6 -->

Says: `PUT /v1/plants/{plant_id}` creates the plant or replaces all its client fields; a field absent in the body is removed; the history stays. `400` for a threshold out of range or `min` not below `max`; `409` `sensor_already_attached` and `409` `plant_limit_reached` at the 51st plant.

Here: `plants` serves it exactly as defined, as one transaction.

### [cloud: public API, delete a plant](../../../../../docs/references/public-api/delete-plant.md)
<!-- unifold:cites sha=d5590cd0 -->

Says: `DELETE` removes the plant and its history, detaches the sensor stick, and answers `204` also when the plant does not exist.

Here: `plants` also deletes the aggregates of the plant.

### [cloud: public API, history](../../../../../docs/references/public-api/get-history.md)
<!-- unifold:cites sha=a522b196 -->

Says: `GET /v1/plants/{plant_id}/history` returns items in ascending order of time with the resolutions `raw` (90 days), `hour` and `day` (2 years). An aggregate has `start`, `count` and `min`, `mean`, `max` per quantity. A late reading changes the aggregates of its hour and day.

Here: what `plants` stores and how long; [data model](../references/data-model.md) says how.

### [cloud: public API, general rules](../../../../../docs/references/public-api/index.md)
<!-- unifold:cites sha=81a51124 -->

Says, as part of the same contract: a change to a plant is visible to the next request. An owner has at most 50 plants; a page has at most 1 000 items.

Here: the limits and the consistency of `plants-api`.

### [cloud: public API, errors](../../../../../docs/references/public-api/error.md)
<!-- unifold:cites sha=6973d698 -->

Says: an error has the body `{"code", "message"}`; the codes include `invalid_request`, `not_found`, `sensor_already_attached`, `plant_limit_reached` and `unavailable`.

Here: the errors of `plants-api`.

## From plantwatch

### [plantwatch: conventions, measured quantities](../../../../../docs/references/conventions.md#measured-quantities)
<!-- unifold:cites sha=c9226f2c -->

Says: soil moisture 0 to 100 percent in steps of 0.1, light 0 to 100 000 lux in steps of 1, temperature -20 to 60 °C in steps of 0.1. Unmeasured means absent.

Here: the ranges allowed for thresholds, the rounding of `mean`, and the rule that an aggregate omits a quantity without values.

### [plantwatch: product parameters](../../../../../docs/references/product-parameters.md)
<!-- unifold:cites sha=b11fccd4 -->

Says: the server keeps 2 years of history per plant. A sensor stick takes a reading every 5 to 60 minutes.

Here: the retention of aggregates. At most 12 readings per hour and 25 920 raw readings in 90 days per plant.

### [plantwatch: glossary](../../../../../docs/references/glossary.md)
<!-- unifold:cites sha=082ae761 -->

Says: a plant has a name, thresholds and one owner. A sensor stick sits in the pot of one plant. A threshold is a limit for one measured quantity.

Here: the things this unit stores.
