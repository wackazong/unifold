# list-alerts

Kind: query

```http
GET /v1/alerts?state=open&plant_id=...&opened_after=...&limit=...&cursor=...
Authorization: Bearer <token>
```

Pre: a valid token. The parameters:

| Parameter | Default | Content |
|---|---|---|
| `state` | `open` | `open`, `closed` or `all` |
| `plant_id` | all plants of the owner | Only alerts of this plant |
| `opened_after` | none | Only alerts with `opened_at` later than this time |
| `limit` | 1 000 | Items per page, at most 1 000 |
| `cursor` | none | The `next` value of the previous page |

Result: `200` with `{"items": [alert, ...], "next": "<cursor>"}`: the [alerts](alert.md) of the owner in descending order of `opened_at`; `next` is present when more items exist. An alert belongs to the owner that the plant had when the alert opened. No operation changes an alert; a client cannot close or acknowledge one.
Errors: `400` `invalid_request` for a malformed parameter; the [errors](error.md) that every operation can answer.
Examples: owner A has the plant P with one closed alert X and one open alert Y.

| Case | Request | Response |
|---|---|---|
| Default list | `GET /v1/alerts` | `200`, items: Y |
| All alerts | `GET /v1/alerts?state=all` | `200`, items: Y, then X |
| Unknown plant | `GET /v1/alerts?plant_id=<unknown>` | `200`, no items |
