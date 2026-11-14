# Context of alerts

What this unit takes over from the units above, and what each item means here.

## From cloud

### [cloud/0001 Services learn about readings through events, not calls](../../../../docs/decisions/0001-services-learn-about-readings-through-events.md)

Accepted readings are announced as events. State that changes rarely, such as thresholds, is asked for with a call; no copy is kept current.

`alerts` subscribes to readings and asks for thresholds when it judges one. It keeps no copy of thresholds beyond 60 seconds.

### [cloud/0002 Each service owns its data and nobody else reads it](../../../../docs/decisions/0002-each-service-owns-its-data.md)

Each service has one schema, and no tables are shared. Alerts and evaluation state live in the schema of `alerts`. Plants are reached through the need `plants-api` only.

### [cloud/0004 Every event consumer is idempotent](../../../../docs/decisions/0004-every-event-consumer-is-idempotent.md)

Events arrive at least once, and a consumer's result must not change with a repeat. An effect outside the databases needs its own safeguard.

A reading is judged once. The notification is the outside effect; see [0002](../decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md).

### [cloud: events between services](../../../../docs/references/events.md)

Events with the same `key` arrive in order. A subscription is named after its service. An event that fails for a passing reason stays unconfirmed.

The subscription is named `alerts`. An event stays unconfirmed while plant and thresholds cannot be had.

### [cloud: calls between services](../../../../docs/references/service-calls.md)

A public operation keeps its path and requires `X-Owner-Id`. A caller waits at most 5 seconds and repeats a failed call at most twice. These rules govern how `alerts-api` is served and how the registry of plants is asked.

### [cloud: public API, alerts](../../../../../docs/references/public-api/alert.md)

The page is part of the public API. The contract this unit implements is `alerts-api`, which serves the behaviour the page describes:

- An alert has `id`, `plant_id`, `quantity`, `bound` (`min` or `max`), `state`, `threshold`, `opened_at`, `opened_value`, the closing fields and `notification` (`pending`, `sent`, `failed`).
- Soil moisture and temperature are judged per reading, light by the highest value of a day. A reading with an estimated time, or not newer than the last judged one of its sensor stick, is not judged.
- At most one alert is open per plant, quantity and bound. It closes with `recovered` by a margin of at most 10 percent of the range of the quantity, with `threshold_changed`, or with `expired` after 30 days without a judged reading. A closed alert never opens again.
- Each alert leads to one notification, which becomes `failed` after 24 hours. Closed alerts are kept for 2 years.

### [cloud: public API, general rules](../../../../../docs/references/public-api/index.md)

An alert and its notification follow the upload response within 1 minute. A changed threshold applies to readings evaluated more than 60 seconds later.

The first rule sets the time budget of `alerts`. The second sets the longest time an answer about thresholds may be reused.

### [cloud: glossary](../../../../docs/references/glossary.md)

A bound is the side of a threshold. The judged value is what is compared with it. A collapse identifier merges two notifications into one.

`alerts` uses these terms, and "registry" and "margin", as defined there. Its own terms are in its [glossary](../references/glossary.md).

## From plantwatch

### [plantwatch/0006 The server side alone decides whether a plant needs attention](../../../../../docs/decisions/0006-the-server-side-alone-decides-what-needs-attention.md)

The server side judges every reading. Every other part shows or carries what the server side decided.

`alerts` is the one place of judgement. Nothing outside it compares a reading with a threshold.

### [plantwatch: glossary](../../../../../docs/references/glossary.md)

An alert is the state "this plant needs attention for this reason"; it opens once and closes. A notification is one message per alert to the owner.

These are the two things this unit is about. "Reason" here is a quantity and a bound. "Attached" is used as defined there.
