# Context of plants

What this unit takes over from the units above, and what each item means here.

## From cloud

### [cloud/0001 Services learn about readings through events, not calls](../../../../docs/decisions/0001-services-learn-about-readings-through-events.md)

Accepted readings are announced as events on a durable bus. State that changes rarely, such as thresholds, is asked for with a call.

`plants` builds history as a subscriber. It serves thresholds by call and announces no changes of plants.

### [cloud/0002 Each service owns its data and nobody else reads it](../../../../docs/decisions/0002-each-service-owns-its-data.md)

Each service has one schema. What another service needs, it gets through a capability.

Plants and history are reachable only through `plants-api`. That is why the lookup by sensor id exists.

### [cloud/0004 Every event consumer is idempotent](../../../../docs/decisions/0004-every-event-consumer-is-idempotent.md)

Events arrive at least once. A consumer's result is the same when an event arrives again, and it confirms only after its change is durable.

The key of a stored reading is sensor id and sequence number. Aggregates are recomputed, never added to.

### [cloud: events between services](../../../../docs/references/events.md)

A subscription is named after its service. A consumer confirms an event it can never handle and leaves one unconfirmed that fails for a passing reason.

The subscription is named `plants`. Events of an unknown type are confirmed and counted.

### [cloud: calls between services](../../../../docs/references/service-calls.md)

A public operation keeps its path and requires `X-Owner-Id`; an internal one lies below `/internal/v1/` without owner. Services answer `GET /healthz`.

These rules define the two groups of operations of `plants-api`, and its health check.

### [cloud: public API, plants](../../../../../docs/references/public-api/plant.md)

The page is part of the public API. The contract this unit implements is `plants-api`, which serves it:

- A plant has `id`, `name` (1 to 60 characters), an optional `sensor_id`, optional `thresholds` with `min`, `max` or both per quantity, and the server fields `latest_reading`, `created_at` and `updated_at`.
- A sensor stick is attached to at most one plant across all owners.

`plants` stores and returns the plant in this form; `list-plants` and `get-plant` of the public API return it as it is.

### [cloud: public API, put a plant](../../../../../docs/references/public-api/put-plant.md)

`PUT /v1/plants/{plant_id}` creates the plant or replaces all its client fields; a field absent in the body is removed; the history stays. The operation answers `400` for a threshold out of range or `min` not below `max`, and `409` `sensor_already_attached` and `409` `plant_limit_reached` at the 51st plant.

`plants` serves the operation exactly as defined, as one transaction.

### [cloud: public API, delete a plant](../../../../../docs/references/public-api/delete-plant.md)

`DELETE` removes the plant and its history, detaches the sensor stick, and answers `204` also when the plant does not exist. `plants` also deletes the aggregates of the plant.

### [cloud: public API, history](../../../../../docs/references/public-api/get-history.md)

`GET /v1/plants/{plant_id}/history` returns items in ascending order of time with the resolutions `raw` (90 days), `hour` and `day` (2 years). An aggregate has `start`, `count` and `min`, `mean`, `max` per quantity. A late reading changes the aggregates of its hour and day.

This is what `plants` stores and for how long; [data model](../references/data-model.md) says how.

### [cloud: public API, general rules](../../../../../docs/references/public-api/index.md)

As part of the public API, a change to a plant is visible to the next request. An owner has at most 50 plants; a page has at most 1 000 items.

These rules set the limits and the consistency of `plants-api`.

### [cloud: public API, errors](../../../../../docs/references/public-api/error.md)

An error has the body `{"code", "message"}`; the codes include `invalid_request`, `not_found`, `sensor_already_attached`, `plant_limit_reached` and `unavailable`. These are the errors of `plants-api`.

## From plantwatch

### [plantwatch: conventions, measured quantities](../../../../../docs/references/conventions.md#measured-quantities)

Soil moisture ranges from 0 to 100 percent in steps of 0.1, light from 0 to 100 000 lux in steps of 1, and temperature from -20 to 60 °C in steps of 0.1. Unmeasured means absent.

These conventions set the ranges allowed for thresholds, the rounding of `mean`, and the rule that an aggregate omits a quantity without values.

### [plantwatch: product parameters](../../../../../docs/references/product-parameters.md)

The server keeps 2 years of history per plant. A sensor stick takes a reading every 5 to 60 minutes.

The 2 years set the retention of aggregates. A plant has at most 12 readings per hour and 25 920 raw readings in 90 days.

### [plantwatch: glossary](../../../../../docs/references/glossary.md)

A plant has a name, thresholds and one owner. A sensor stick sits in the pot of one plant. A threshold is a limit for one measured quantity.

These are the things this unit stores.
