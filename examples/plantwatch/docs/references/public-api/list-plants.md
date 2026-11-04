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

| Case | Given | Input | Expected |
|---|---|---|---|
| No token | | `GET /v1/plants` without `Authorization` | `401` `unauthenticated` |
| Too many requests | 120 requests with one token within this minute | the 121st request, `GET /v1/plants` with that token | `429` `rate_limited` with `Retry-After` |
| Two plants | the owner has "Monstera" and "Basil" | `GET /v1/plants` | `200`; items "Basil", then "Monstera" |
