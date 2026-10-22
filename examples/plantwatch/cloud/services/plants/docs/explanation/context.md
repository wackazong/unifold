# Context of plants

What this unit inherits from the levels above. This is the only file of the unit that links upward. Each item is restated so that the unit can be understood when the link is not available.

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
<!-- unifold:cites sha=b3af8439 -->

Says: a subscription is named after its service. A consumer confirms an event it can never handle and leaves one unconfirmed that fails for a passing reason.

Here: the subscription is named `plants`. Events of an unknown type are confirmed and counted.

### [cloud: calls between services](../../../../docs/references/service-calls.md)
<!-- unifold:cites sha=7282b622 -->

Says: a public operation keeps its path and requires `X-Owner-Id`; an internal one lies below `/internal/v1/` without owner. Services answer `GET /healthz`.

Here: the two groups of operations of `plants-api`, and its health check.

### [cloud: public API, plants](../../../../../docs/references/public-api/plants.md)
<!-- unifold:cites sha=5aad3303 -->

Says, as the contract that this unit implements:

- A plant has `id`, `name` (1 to 60 characters), an optional `sensor_id`, optional `thresholds` with `min`, `max` or both per quantity, and the server fields `latest_reading`, `created_at` and `updated_at`.
- `PUT /v1/plants/{plant_id}` creates or replaces all client fields; `GET` reads one plant or lists all; `DELETE` removes the plant with its history and answers `204` also when the plant does not exist.
- A sensor stick is attached to at most one plant across all owners.
- `GET /v1/plants/{plant_id}/history` returns items in ascending order of time with the resolutions `raw` (90 days), `hour` and `day` (2 years). An aggregate has `start`, `count` and `min`, `mean`, `max` per quantity.

Here: the contract of the operations for an owner. `plants` serves them exactly as defined.

### [cloud: public API, general rules](../../../../../docs/references/public-api/index.md)
<!-- unifold:cites sha=d259494b -->

Says, as part of the same contract: an error has the body `{"code", "message"}`; the codes include `not_found`, `sensor_already_attached`, `plant_limit_reached` and `unavailable`. A change to a plant is visible to the next request. An owner has at most 50 plants; a page has at most 1 000 items.

Here: the errors, the limits and the consistency of `plants-api`.

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
