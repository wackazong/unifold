# Context of server

What this unit takes over from the units above, and what each item means here.

## From alerts

### [alerts/0001 Evaluation and notification are libraries beside one process](../../../docs/decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md)

The service is one process with libraries beside it. The libraries keep no state; what they must remember, they return to the process.

`server` is that process. It stores the evaluation state for the library that produced it and holds no judging or wording logic.

### [alerts/0002 The alert row is the outbox of its notification](../../../docs/decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md)

An alert is stored with `notification` set to `pending`. A separate delivery step notifies, at once and on a schedule, for at most 24 hours.

`server` implements both steps and never notifies from the handling of an event. Delivery can repeat.

### [alerts: alerts API](../../../../../docs/references/alerts-api.md)

The reference is the contract of the capability `alerts-api`, which `server` implements for the whole service. Every request to `/v1/alerts` requires `X-Owner-Id`, and answers are limited to that owner. An alert belongs to the owner named when it opened. An alert is stored within 30 seconds after its event arrives. `id`, `plant_id`, `quantity`, `bound`, `threshold`, `opened_at` and `opened_value` never change; the closing fields and `notification` change once.

### [alerts: glossary](../../../docs/references/glossary.md)

The evaluation state is what judging the earlier readings of a sensor stick concluded. A notification is owed while it is `pending`.

`server` stores the evaluation state unread per sensor stick, and its delivery step takes the rows whose notification is owed.

## From cloud

### [cloud: public API, alerts](../../../../../../docs/references/public-api/alert.md)

This unit implements the following part of the reference. An alert has the fields `id`, `plant_id`, `quantity`, `bound`, `state`, `threshold`, `opened_at`, `opened_value`, `closed_at`, `closed_reason` and `notification`. It closes with `expired` when no reading of its plant was judged for 30 days. The notification is `pending`, `sent` or `failed`, and it becomes `failed` after 24 hours. Closed alerts are kept for 2 years.

These are the rows that `server` stores and the answers it gives. Expiry and retention are jobs of `server`.

### [cloud: public API, general rules](../../../../../../docs/references/public-api/index.md)

A list has at most 1 000 items per page. The error response and its codes are the part `error` of the same contract. The page size sets the paging of `alerts-api`.

### [cloud: public API, errors](../../../../../../docs/references/public-api/error.md)

An error has the body `{"code", "message"}`; `400` is `invalid_request`, `404` `not_found`, `503` `unavailable`. These are the errors of `alerts-api`.

### [cloud/0004 Every event consumer is idempotent](../../../../../docs/decisions/0004-every-event-consumer-is-idempotent.md)

An event can arrive again. The consumer's change and its record of the handled event are one transaction; the consumer confirms the event afterwards.

The evaluation state is that record. It is stored in the same transaction as the alerts.

### [cloud: events between services](../../../../../docs/references/events.md)

A subscription is named after its service. A consumer confirms an event it can never handle and leaves one unconfirmed that fails for a passing reason.

The subscription is named `alerts`. Events of an unknown type are confirmed and counted.

### [cloud: calls between services](../../../../../docs/references/service-calls.md)

A public operation is served under its public path and requires `X-Owner-Id`. Every service answers `GET /healthz` and listens on port 8080. This is how `server` listens.

## From plantwatch

### [plantwatch: conventions, identifiers and time](../../../../../../docs/references/conventions.md)

Plant, owner and alert have a UUID in lower-case text form. A time is UTC, RFC 3339 with `Z` and whole seconds.

`server` generates the alert id. All stored and returned times have this form.
