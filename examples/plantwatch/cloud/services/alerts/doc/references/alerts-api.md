# Alerts API

The contract of the port `alerts-api`. The alert, its life and the
operations with their parameters and errors are defined above this unit
and cited in [context](../context.md). This reference states how `alerts`
serves them.

## Operations

| Operation | Notes |
|---|---|
| `GET /v1/alerts` | Filters `state`, `plant_id`, `opened_after`; pages with `limit` and `cursor` |
| `GET /v1/alerts/{alert_id}` | `404` with `not_found` for an alert of another owner |
| `GET /healthz` | `200` while the database is reachable |

- Every request to `/v1/alerts` carries `X-Owner-Id`. Without it `alerts`
  answers `400` with `invalid_request`.
- `alerts` does not verify who the caller is. It limits every answer to
  the alerts of the owner in the header.

## Whose alert

An alert belongs to the owner that the lookup of the plant named when the
alert opened. `alerts` stores that owner id with the alert and does not
ask again. `plant_id` in a request is a filter; `alerts` does not check
that the plant exists.

## Freshness

- A request sees every alert that was stored before the request arrived.
- An alert is stored within 30 seconds after the event of its reading
  reaches `alerts`. Its notification is handed to the push service in the
  same period, unless the push service is unreachable.
- While `alerts` is behind on the event stream, or cannot fetch
  thresholds, the answers show the state as of the last judged reading.
  Nothing is skipped; `alerts` catches up in order.

## Stability of the fields

| Field | Changes after the alert is stored |
|---|---|
| `id`, `plant_id`, `quantity`, `bound`, `threshold`, `opened_at`, `opened_value` | never |
| `state`, `closed_at`, `closed_reason` | once, when the alert closes |
| `notification` | once, from `pending` to `sent` or `failed` |

## Timing

`alerts` answers a page of alerts within 200 ms while the database is
healthy.
