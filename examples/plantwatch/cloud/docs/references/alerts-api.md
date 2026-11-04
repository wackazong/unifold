# alerts-api

Contract of `alerts.alerts-api`. The alert, its life and the operations with their parameters are defined by the public API of plantwatch and cited in [context](../explanation/context.md); this contract states how `alerts` serves them. Notation: HTTP, with JSON bodies as the project conventions define them.
Sources: the public API of plantwatch, the calls between services of `cloud`.
Binding: http

## Use

A caller that acts for an owner lists the owner's alerts and reads single alerts, with `X-Owner-Id` in every request. The container host and other services ask `healthz`. The connection has no state: any part may be called at any time, and every request may be repeated.

- Every request to `/v1/alerts` carries `X-Owner-Id`. Without it `alerts` answers `400` with `invalid_request`.
- `alerts` does not verify who the caller is. It limits every answer to the alerts of the owner in the header.
- An alert belongs to the owner that the lookup of the plant named when the alert opened. `alerts` stores that owner id with the alert and does not ask again. `plant_id` in a request is a filter; `alerts` does not check that the plant exists.
- While the database cannot be reached, every operation answers `503` with `unavailable`.
- An alert opens only on a decision of the evaluation, and closes only on such a decision or by expiry; no call of this API changes an alert.

## Qualities

| Aspect | Guarantee |
|---|---|
| latency | a page of alerts is answered within 200 ms while the database is healthy; the first attempt to notify follows at once when an alert is stored; a changed threshold, or a sensor stick moved to another plant, applies to the judgement of readings after at most 60 seconds |
| freshness | a request sees every alert that was stored before the request arrived; an alert is stored within 30 seconds after the event of its reading reaches `alerts`, and its notification is handed to the push service in the same period, unless the push service is unreachable |
| consistency | while `alerts` is behind on the event stream, or cannot fetch thresholds, the answers show the state as of the last judged reading; nothing is skipped, and `alerts` catches up in order |
| stability | after an alert is stored, `id`, `plant_id`, `quantity`, `bound`, `threshold`, `opened_at` and `opened_value` never change; `state`, `closed_at` and `closed_reason` change once, when the alert closes; `notification` changes once, from `pending` to `sent` or `failed` |
| availability | while the database cannot be reached, every operation answers `503` `unavailable` |
| idempotency | every request may be repeated, because the gateway repeats a failed call; every notification for the same alert carries the same collapse identifier, so a repetition replaces the earlier notification on a phone |
| timeout | the gateway waits 5 seconds for an answer and then counts the call as failed |
| concurrency | at most one alert is open per plant, quantity and bound, also when events repeat or several instances run |

## Parts

### list-alerts

Kind: query

```http
GET /v1/alerts?state=&plant_id=&opened_after=&limit=&cursor=
X-Owner-Id: <owner id>
```

Pre: `X-Owner-Id` is present. Parameters and the body are those of the public API.
Result: `200` with the alerts of the owner, filtered by `state`, `plant_id` and `opened_after`, paged with `limit` and `cursor`, in descending order of `opened_at`.
Errors: `400` `invalid_request` without the owner header; `503` `unavailable` while the database cannot be reached.
Examples: owner A has the plant P with one closed alert X and one open alert Y.

| Case | Given | Input | Expected |
|---|---|---|---|
| default list | | `GET /v1/alerts` with `X-Owner-Id` A | `200`, items: Y |
| all alerts | | `GET /v1/alerts?state=all` with `X-Owner-Id` A | `200`, items in descending order of `opened_at`: Y, then X |
| no owner header | | `GET /v1/alerts` | `400` `invalid_request` |
| unknown plant | | `GET /v1/alerts?plant_id=<unknown>` with `X-Owner-Id` A | `200`, no items |
| event of a reading that opens an alert | the event arrived at 09:00:00 | `GET /v1/alerts` with `X-Owner-Id` A at 09:00:30 | `200`, items contain the new alert |
| the same event again | the same event arrived a second time | `GET /v1/alerts?state=all` with `X-Owner-Id` A | `200`, no new alert; no second notification was sent |

### get-alert

Kind: query

```http
GET /v1/alerts/{alert_id}
X-Owner-Id: <owner id>
```

Pre: `X-Owner-Id` is present.
Result: `200` with the alert, in the form the public API defines.
Errors: `404` `not_found` for an alert of another owner; `400` `invalid_request` without the owner header; `503` `unavailable` while the database cannot be reached.
Examples: as for `list-alerts`.

| Case | Given | Input | Expected |
|---|---|---|---|
| other owner | | `GET /v1/alerts/{X}` with `X-Owner-Id` B | `404` `not_found` |
| P was deleted | the plant P was deleted | `GET /v1/alerts/{Y}` with `X-Owner-Id` A | `200`; Y stays open until it expires |

### healthz

Kind: query

```http
GET /healthz
```

Pre: none.
Result: `200` while the database is reachable.
Errors: `503` otherwise.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| healthy | the database is reachable | `GET /healthz` | `200` |
| database down | the database cannot be reached | `GET /healthz` | `503` |

## Fake

Replays the examples: an HTTP server in the test that answers the requests of the table with the responses given and `404` for everything else. Faults it can inject: `503` `unavailable`, no response within 5 seconds.
