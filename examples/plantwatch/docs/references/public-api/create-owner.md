# create-owner

Kind: command

```http
POST /v1/owners
```

Pre: no token and no body; at most 10 requests per client address per hour.
Result: `201`; an owner is created, with a token that is valid for 365 days:

```json
{
  "owner_id": "5b0e2d0a-8f0c-4d0e-9a57-0c1a2f3b4c5d",
  "token": "<token>",
  "expires_at": "2027-10-06T09:00:00Z"
}
```

Errors: `429` `rate_limited` beyond 10 per hour from one client address; the [errors](error.md) that every operation can answer.
Examples:

| Case | Request | Response |
|---|---|---|
| First start of a client | `POST /v1/owners` without token | `201` with `owner_id`, `token`, `expires_at` |
| Repeated | `POST /v1/owners` twice | Two owners; a client that has lost the first response uses the second owner |
