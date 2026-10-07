# Context of server

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From alerts

### [alerts/0001 Evaluation and notification are libraries beside one process](../../doc/decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md)

Says: the service is one process with libraries beside it. The libraries
keep no state; what they must remember, they return to the process.

Here: `server` is that process. It stores the evaluation state for the
library that produced it and holds no judging or wording logic.

### [alerts/0002 The alert row is the outbox of its notification](../../doc/decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md)

Says: an alert is stored with `notification` set to `pending`. A separate
delivery step notifies, at once and on a schedule, for at most 24 hours.

Here: `server` implements both steps and never notifies from the handling
of an event. Delivery can repeat.

### [alerts: alerts API](../../doc/references/alerts-api.md)

Says, as the contract that this unit implements: every request to
`/v1/alerts` requires `X-Owner-Id`, and answers are limited to that owner.
An alert belongs to the owner named when it opened. An alert is stored
within 30 seconds after its event arrives. `id`, `plant_id`, `quantity`,
`bound`, `threshold`, `opened_at` and `opened_value` never change; the
closing fields and `notification` change once.

Here: the contract of the port `alerts-api`, which `server` implements for
the whole service.

### [alerts: glossary](../../doc/references/glossary.md)

Says: the evaluation state is what judging the earlier readings of a sensor
stick concluded. A notification is owed while it is `pending`.

Here: the value that `server` stores unread per sensor stick, and the rows
that its delivery step takes.

## From cloud

### [cloud: public API, alerts](../../../../doc/references/public-api/alerts.md)

Says, as far as this unit implements it: an alert has the fields `id`,
`plant_id`, `quantity`, `bound`, `state`, `threshold`, `opened_at`,
`opened_value`, `closed_at`, `closed_reason` and `notification`. It closes
with `expired` when no reading of its plant was judged for 30 days. The
notification is `pending`, `sent` or `failed`, and `failed` after 24 hours.
Closed alerts are kept for 2 years. `GET /v1/alerts` lists in descending
order of `opened_at`; `GET /v1/alerts/{alert_id}` reads one.

Here: the rows that `server` stores and the answers it gives. Expiry and
retention are jobs of `server`.

### [cloud: public API, general rules](../../../../doc/references/public-api/index.md)

Says: an error has the body `{"code", "message"}`. A list has at most 1 000
items per page.

Here: the errors and the paging of `alerts-api`.

### [cloud/0004 Every event consumer is idempotent](../../../../doc/decisions/0004-every-event-consumer-is-idempotent.md)

Says: an event can arrive again. The consumer's change and its record of the
handled event are one transaction; it confirms the event afterwards.

Here: the evaluation state is that record. It is stored in the same
transaction as the alerts.

### [cloud: events between services](../../../../doc/references/events.md)

Says: a subscription is named after its service. A consumer confirms an event
it can never handle and leaves one unconfirmed that fails for a passing reason.

Here: the subscription is named `alerts`. Events of an unknown type are
confirmed and counted.

### [cloud: calls between services](../../../../doc/references/service-calls.md)

Says: a public operation is served under its public path and requires
`X-Owner-Id`. Every service answers `GET /healthz` and listens on port 8080.

Here: how `server` listens.

## From plantwatch

### [plantwatch: conventions, identifiers and time](../../../../../doc/references/conventions.md)

Says: plant, owner and alert have a UUID in lower-case text form. A time is
UTC, RFC 3339 with `Z` and whole seconds.

Here: `server` generates the alert id. All stored and returned times have
this form.
