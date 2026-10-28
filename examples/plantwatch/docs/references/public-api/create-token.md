# create-token

Kind: command

```http
POST /v1/tokens
Authorization: Bearer <token>
```

Pre: a valid token; no body.
Result: `201` with a new token for the owner of the token in the request. The old token stays valid until it expires.

```json
{"token": "<token>", "expires_at": "2027-10-06T09:00:00Z"}
```

Errors: `401` `unauthenticated`; the [errors](error.md) that every operation can answer.
Examples:

| Case | Request | Response |
|---|---|---|
| Second phone | `POST /v1/tokens` with the token of the first phone | `201` with a new token; both tokens reach the same plants |
| Expired token | `POST /v1/tokens` 366 days after the token was issued | `401` `unauthenticated` |
