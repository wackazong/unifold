# Context of gateway

What this unit inherits from the levels above. This is the only file of the unit that links upward. Each item is restated so that the unit can be understood when the link is not available.

## From cloud

### [cloud/0003 One gateway is the only public entry](../../../../docs/decisions/0003-one-gateway-is-the-only-public-entry.md)
<!-- unifold:cites sha=2ad10b42 -->

Says: one service is reachable from outside. It authenticates and routes and does not change bodies. The services behind it trust the owner id it passes.

Here: this unit is that service. It never passes on a request without a verified token, and never an owner id that came from outside.

### [cloud: public API](../../../../../docs/references/public-api/index.md)
<!-- unifold:cites sha=d259494b -->

Says, as far as this unit implements it:

- All operations lie under `/v1`: `POST /v1/owners` and `POST /v1/tokens` for tokens, paths below `/v1/sensors/` for uploads, `/v1/plants` and below for plants and history, `/v1/alerts` and below for alerts.
- Every request except `POST /v1/owners` carries `Authorization: Bearer <token>`. A token stands for one owner, is opaque to the client and valid for 365 days. Both token operations answer `201` with `token` and `expires_at`; the first also with `owner_id`.
- Limits: 1 MB per request body, 120 requests per minute per token, 10 new owners per hour per client address.
- Errors have the body `{"code", "message"}`: `401` `unauthenticated`, `404` `not_found`, `413` `payload_too_large`, `429` `rate_limited` with the header `Retry-After`, `503` `unavailable`.
- Every request may be repeated.

Here: the contract of the capability `public-api`. `gateway` implements the token operations, the limits and these errors itself. It passes the three groups of paths on to the needs `ingest-api`, `plants-api` and `alerts-api` without looking at their bodies.

### [cloud: calls between services](../../../../docs/references/service-calls.md)
<!-- unifold:cites sha=7282b622 -->

Says, as the rules that this unit implements: the service that verified the token sets `X-Owner-Id`; the first service sets `X-Request-Id`. A caller waits at most 5 seconds and repeats a failed call at most twice, after 0.2 and 1 second. Paths below `/internal/` are never served to a client. Every service answers `GET /healthz`.

Here: `gateway` sets both headers, removes an incoming `X-Owner-Id`, keeps the time limits, and answers `404` for `/internal/`.

### [cloud: glossary](../../../../docs/references/glossary.md)
<!-- unifold:cites sha=2e1d860c -->

Says: a client is a program that calls the public API for one owner. A token is the string it sends to prove for which owner it acts.

Here: the two things `gateway` deals with. The form of a token is its own business, see [tokens](../references/tokens.md).

## From plantwatch

### [plantwatch: conventions, identifiers](../../../../../docs/references/conventions.md#identifiers)
<!-- unifold:cites sha=e6aec781 -->

Says: an owner has a UUID in lower-case text form.

Here: the owner id in a token and in `X-Owner-Id`.

### [plantwatch: glossary](../../../../../docs/references/glossary.md)
<!-- unifold:cites sha=082ae761 -->

Says: the owner is the user a plant belongs to.

Here: a token stands for exactly one owner. `gateway` creates an owner by issuing the first token for a new UUID.
