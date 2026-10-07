# Context of server

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From alerts

| Source | What it says | What it means here |
|---|---|---|
| [alerts/0001 Evaluation and notification are libraries beside one process](../../doc/decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md) | The service is one process and two libraries. The libraries have no state and no database access; what they must remember, they return to the process. | `server` is that process. It stores the evaluation state for the library that produced it and holds no judging or wording logic. |
| [alerts/0002 The alert row is the outbox of its notification](../../doc/decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md) | An alert is stored with `notification` set to `pending`. A separate delivery step has pending alerts notified, right after storing and on a schedule, for at most 24 hours. Delivery can repeat. | `server` implements both steps and never notifies from the handling of an event. |
| [alerts: alerts API](../../doc/references/alerts-api.md) | The API requires `X-Owner-Id` and limits answers to that owner. An alert belongs to the owner named when it opened. An alert is stored within 30 seconds after its event arrives. Most fields never change after storing. | The contract of the port `alerts-api`, which `server` implements for the whole service. |

## From cloud

| Source | What it says | What it means here |
|---|---|---|
| [cloud: public API, alerts](../../../../doc/references/public-api/alerts.md) | Defines the alert with its fields, the states `open` and `closed`, the reasons `recovered`, `threshold_changed` and `expired` (no reading judged for 30 days), the notification states `pending`, `sent`, `failed`, and the operations `GET /v1/alerts` and `GET /v1/alerts/{alert_id}`. Closed alerts are kept for 2 years. | The rows `server` stores and the answers it gives. Expiry and retention are jobs of `server`. |
| [cloud: public API, general rules](../../../../doc/references/public-api/index.md) | Error bodies have `code` and `message`. A list has at most 1 000 items per page. | The errors and the paging of `alerts-api`. |
| [cloud/0004 Every event consumer is idempotent](../../../../doc/decisions/0004-every-event-consumer-is-idempotent.md) | An event can arrive again. The consumer's change and the record that the event was handled are one transaction; the event is confirmed after it. | The evaluation state is that record. It is stored in the same transaction as the alerts. |
| [cloud/0002 Each service owns its data and nobody else reads it](../../../../doc/decisions/0002-each-service-owns-its-data.md) | One schema per service. | `server` owns the whole schema of the alerts service. |
| [cloud: events between services](../../../../doc/references/events.md) | An event has `id`, `type`, `source`, `time`, `key`, `data`. A subscription is named after the service. A consumer confirms an event it can never handle and counts it; it leaves an event unconfirmed when the failure passes. | The subscription is named `alerts`. Events of unknown type are confirmed. |
| [cloud: calls between services](../../../../doc/references/service-calls.md) | Operations of the public API are served under the same path, with `X-Owner-Id`. Every service answers `GET /healthz` and listens on port 8080. | How `server` listens. |

## From plantwatch

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch: time from upload to notification](../../../../../doc/references/product-parameters.md) | Under 1 minute. | `server` handles an event as it arrives and starts delivery right after the commit, not on the next schedule. |
| [plantwatch: identifiers and time](../../../../../doc/references/conventions.md) | Plant, owner and alert have a UUID in lower-case text form. Times are UTC, RFC 3339 with `Z`. | `server` generates the alert id. All stored and returned times have this form. |
| [plantwatch: alert, notification](../../../../../doc/references/glossary.md) | An alert opens once, stays open while the reason lasts, and closes. A notification is one message per alert. | What a row of `server` stands for. |
