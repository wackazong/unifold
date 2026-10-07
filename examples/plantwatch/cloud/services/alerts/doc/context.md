# Context of alerts

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From cloud

| Source | What it says | What it means here |
|---|---|---|
| [cloud/0001 Services learn about readings through events, not calls](../../../doc/decisions/0001-services-learn-about-readings-through-events.md) | Accepted readings are announced as events. Current state that changes rarely, such as thresholds, is fetched by a call. | `alerts` is a subscriber of readings and asks for thresholds when it judges a reading. It keeps no copy of thresholds beyond a short cache. |
| [cloud/0002 Each service owns its data and nobody else reads it](../../../doc/decisions/0002-each-service-owns-its-data.md) | One schema per service; no shared tables. | Alerts and evaluation state live in the schema of `alerts`. Plants are reached through the need `plants-api` only. |
| [cloud/0004 Every event consumer is idempotent](../../../doc/decisions/0004-every-event-consumer-is-idempotent.md) | Events arrive at least once; a consumer's result must not change when an event arrives again. An effect outside the databases, such as a notification, needs its own way to make a repeat harmless. | A reading is judged once. The notification is the outside effect; see [0002](decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md). |
| [cloud: events between services](../../../doc/references/events.md) | An event has `id`, `type`, `source`, `time`, `key`, `data`. Events with the same `key` arrive in order. A subscription is named after the consuming service. A consumer leaves an event unconfirmed when it fails for a passing reason. | The subscription is named `alerts`. An event stays unconfirmed while thresholds cannot be fetched. |
| [cloud: calls between services](../../../doc/references/service-calls.md) | An operation of the public API is served under the same path and requires `X-Owner-Id`. A caller waits at most 5 seconds and repeats a failed call at most twice. Every service answers `GET /healthz`. | How `alerts-api` is served and how thresholds are fetched. |
| [cloud: public API, alerts](../../../doc/references/public-api/alerts.md) | Defines the alert with `quantity`, `bound`, `state`, `closed_reason` and `notification`; what is judged (light over 24 hours); when an alert opens, closes with `recovered` or `threshold_changed`, and expires after 30 days; one notification per alert, `failed` after 24 hours; the operations on `/v1/alerts`. | The contract of `alerts-api` and the behaviour that this unit implements. |
| [cloud: public API, general rules](../../../doc/references/public-api/index.md) | An alert is visible and its notification handed over within 1 minute after the upload response. A changed threshold applies to readings evaluated more than 60 seconds after the change. Error bodies have `code` and `message`. | The time budget of `alerts` and the longest time thresholds may be cached. |

## From plantwatch

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0001 The phone relays between sensor stick and server](../../../../doc/decisions/0001-the-phone-relays-between-sensor-and-server.md) | Readings reach the server only when a phone was near. Alerts can be late by as long as the phone was away. | `alerts` judges readings that are hours or days old and still notifies. |
| [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | Some readings have an estimated time and are flagged. | Such a reading is not judged. |
| [plantwatch: measured quantities](../../../../doc/references/conventions.md) | Soil moisture in percent, light in lux, temperature in degrees Celsius, with fixed ranges and resolutions. An unmeasured quantity is absent. | The quantities that can cause an alert. An absent quantity is not judged. |
| [plantwatch: time from upload to notification](../../../../doc/references/product-parameters.md) | Under 1 minute. | `alerts` handles events as they arrive and hands a notification over at once. |
| [plantwatch: history kept on the server](../../../../doc/references/product-parameters.md) | 2 years per plant. | Closed alerts are kept for 2 years. |
| [plantwatch: threshold, alert, notification](../../../../doc/references/glossary.md) | A threshold is a limit for one quantity of a plant. An alert is the state "this plant needs attention for this reason"; it opens once, stays open while the reason lasts, and closes. A notification is a message to the owner about an alert that has opened, one per alert. | The three things this unit is about. "Reason" here is a quantity and a bound. |
