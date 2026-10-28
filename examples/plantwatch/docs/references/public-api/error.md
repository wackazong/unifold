# error

Kind: type

```json
{"code": "rate_limited", "message": "120 requests per minute per token"}
```

An error response has the body `{"code": "...", "message": "..."}`. A client decides by status and `code`. `message` is English text for developers. Every operation can answer these:

| Status | `code` | Meaning | What the client does |
|---|---|---|---|
| 400 | `invalid_request` | Path, parameter or body is malformed | Correct the request |
| 401 | `unauthenticated` | Token missing, malformed or expired | Use a valid token |
| 404 | `not_found` | The resource does not exist or belongs to another owner | Nothing |
| 409 | `sensor_already_attached` | The sensor stick is attached to another plant | Detach it there first |
| 409 | `plant_limit_reached` | The owner already has 50 plants | Delete a plant |
| 413 | `payload_too_large` | Body or batch exceeds a limit | Send less at once |
| 429 | `rate_limited` | Too many requests | Repeat after the seconds given in the `Retry-After` header |
| 503 | `unavailable` | A part of the server cannot be reached | Repeat later, keep the data |

| Case | Request | Response |
|---|---|---|
| Expired token | Any request, 366 days after the token was issued | `401` `unauthenticated` |
| Too many requests | The 121st request with one token within a minute | `429` `rate_limited` with `Retry-After` |
