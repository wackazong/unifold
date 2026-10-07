# Context of plants

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From cloud

| Source | What it says | What it means here |
|---|---|---|
| [cloud/0001 Services learn about readings through events, not calls](../../../doc/decisions/0001-services-learn-about-readings-through-events.md) | Accepted readings are announced as events on a durable bus. Current state that changes rarely, such as thresholds, is fetched by a call. | `plants` builds history as a subscriber. It serves thresholds by call and announces no changes. |
| [cloud/0002 Each service owns its data and nobody else reads it](../../../doc/decisions/0002-each-service-owns-its-data.md) | One schema per service; what another service needs, it gets through a port. | Plants and history are reachable only through `plants-api`. That is why the lookup by sensor id exists. |
| [cloud/0004 Every event consumer is idempotent](../../../doc/decisions/0004-every-event-consumer-is-idempotent.md) | Events arrive at least once. A consumer's result is the same when an event arrives again; it confirms only after its change is durable. | The key of a stored reading is sensor id and sequence number; aggregates are recomputed, never added to. |
| [cloud: events between services](../../../doc/references/events.md) | An event has `id`, `type`, `source`, `time`, `key`, `data`. A subscription is named after the consuming service. A consumer confirms an event it can never handle and leaves one unconfirmed that fails for a passing reason. | The subscription is named `plants`. Events of unknown type are confirmed and counted. |
| [cloud: calls between services](../../../doc/references/service-calls.md) | An operation of the public API is served under the same path and requires `X-Owner-Id`. Internal operations start with `/internal/v1/` and carry no owner. Every service answers `GET /healthz`. A caller waits at most 5 seconds. | The two groups of operations of `plants-api`, and the time budget of a history query. |
| [cloud: public API, plants](../../../doc/references/public-api/plants.md) | Defines the plant with `name`, `sensor_id`, `thresholds` and `latest_reading`, the operations on `/v1/plants`, and the history with the resolutions `raw` (90 days), `hour` and `day` (2 years). | The contract of the first group of operations. `plants` serves them exactly as defined. |
| [cloud: public API, general rules](../../../doc/references/public-api/index.md) | Error bodies have `code` and `message`; codes include `not_found`, `sensor_already_attached`, `plant_limit_reached`, `unavailable`. A change to a plant is visible to the next request. At most 50 plants per owner, 1 000 items per page. | The errors, the limits and the consistency of `plants-api`. |

## From plantwatch

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | A reading is identified by sensor id and sequence number and never changes. | A stored reading is never updated. A second event for the same identity is ignored. |
| [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | Some readings have an estimated time and are flagged. | Such a reading is stored and aggregated under its estimated time. |
| [plantwatch: measured quantities](../../../../doc/references/conventions.md) | Soil moisture 0 to 100 percent with resolution 0.1, light 0 to 100 000 lux with resolution 1, temperature -20 to 60 degrees Celsius with resolution 0.1. An unmeasured quantity is absent. | The ranges allowed for thresholds, the rounding of `mean`, and the rule that an aggregate omits a quantity without values. |
| [plantwatch: identifiers and time](../../../../doc/references/conventions.md) | Plant and owner have a UUID in lower-case text form, a sensor id is 16 lower-case hex digits. Times are UTC, RFC 3339 with `Z`. | The forms that `plants-api` accepts and returns. |
| [plantwatch: history kept on the server](../../../../doc/references/product-parameters.md) | 2 years per plant. | The retention of aggregates. |
| [plantwatch: sampling interval](../../../../doc/references/product-parameters.md) | 5 to 60 minutes. | At most 12 readings per hour and 25 920 raw readings in 90 days per plant. |
| [plantwatch: plant, owner, sensor stick, threshold](../../../../doc/references/glossary.md) | A plant has a name, thresholds and one owner. A sensor stick sits in the pot of one plant. A threshold is a limit for one measured quantity. | The things this unit stores. |
