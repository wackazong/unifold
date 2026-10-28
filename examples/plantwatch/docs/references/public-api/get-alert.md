# get-alert

Kind: query

```http
GET /v1/alerts/{alert_id}
Authorization: Bearer <token>
```

Pre: a valid token.
Result: `200` with the [alert](alert.md).
Errors: `404` `not_found` when the alert does not exist or belongs to another owner; the [errors](error.md) that every operation can answer.
Examples: owner A has the plant P with the open alert Y.

| Case | Request | Response |
|---|---|---|
| Own alert | `GET /v1/alerts/{Y}` with a token of A | `200` with Y |
| Other owner | `GET /v1/alerts/{Y}` with a token of B | `404` `not_found` |
