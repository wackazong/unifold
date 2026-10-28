# list-plants

Kind: query

```http
GET /v1/plants
Authorization: Bearer <token>
```

Pre: a valid token.
Result: `200` with `{"items": [plant, ...]}`, every [plant](plant.md) of the owner, ordered by `name`.
Errors: the [errors](error.md) that every operation can answer.
Examples:

| Case | Request | Response |
|---|---|---|
| No token | `GET /v1/plants` without `Authorization` | `401` `unauthenticated` |
| Too many requests | The 121st request with one token within a minute | `429` `rate_limited` with `Retry-After` |
| Two plants | An owner with "Monstera" and "Basil" | `200`; items "Basil", then "Monstera" |
