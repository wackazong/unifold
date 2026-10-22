# Routing

What `gateway` does with a request to its capability `public-api`. The operations, bodies, error codes and limits themselves are defined in its contract, the [public API](../../../../../docs/references/public-api/index.md), and cited in [context](../explanation/context.md).

## Order of handling

`gateway` applies these checks to every request, in this order. The first one that fails ends the request.

| Step | Check | On failure |
|---|---|---|
| 1 | The declared or received body is at most 1 MB | `413` `payload_too_large` |
| 2 | The path belongs to a route (see below) | `404` `not_found` |
| 3 | For `POST /v1/owners`: fewer than 10 owners were created from this client address within the last hour | `429` `rate_limited` |
| 4 | For every other operation: the `Authorization` header holds a valid token ([tokens](tokens.md)) | `401` `unauthenticated` |
| 5 | Fewer than 120 requests with this token were handled within the last minute | `429` `rate_limited` |

Steps 3 and 5 count per instance ([0002](../decisions/0002-rate-limits-are-counted-per-instance.md)). A `429` response carries the header `Retry-After` with the seconds until the next request is accepted.

## Routes

| Method and path | Handled by |
|---|---|
| `POST /v1/owners` | `gateway` itself |
| `POST /v1/tokens` | `gateway` itself |
| any method, `/v1/sensors/...` | the need `ingest-api` |
| any method, `/v1/plants` and `/v1/plants/...` | the need `plants-api` |
| any method, `/v1/alerts` and `/v1/alerts/...` | the need `alerts-api` |
| `GET /healthz` | `gateway` itself, without token |
| everything else, including `/internal/...` | nobody: `404` `not_found` |

A route is chosen by the path alone. `gateway` does not know which operations exist below a prefix. An unknown operation is answered by the provider.

## Passing a request on

| Part of the request | What `gateway` does |
|---|---|
| Method, path, query string | Unchanged |
| Body | Unchanged, not parsed |
| `Authorization` | Removed |
| `X-Owner-Id` from the client | Removed |
| `X-Owner-Id` | Set to the owner id of the verified token |
| `X-Request-Id` | Set to a new UUID; a value from the client is replaced |
| `Content-Type`, `Accept` | Unchanged |
| Other headers | Removed |

| Part of the response | What `gateway` does |
|---|---|
| Status and body | Unchanged, also for errors |
| `Content-Type`, `Retry-After` | Unchanged |
| `X-Request-Id` | Added, so that a client can report it |
| Other headers | Removed |

## When a provider does not answer

- `gateway` waits at most 5 seconds for a response.
- It repeats a call that timed out, could not connect or answered `503` at most twice, after 0.2 and after 1 second.
- After the third failure it answers `503` `unavailable`.
- It repeats calls of every method. Every operation of the public API can be repeated.

## The token operations

`gateway` answers both without calling anyone.

| Operation | Effect |
|---|---|
| `POST /v1/owners` | Generates a random UUID as owner id and issues a token for it. Nothing is stored. |
| `POST /v1/tokens` | Issues a new token for the owner of the verified token |

## Examples

| Case | Request | What `gateway` does |
|---|---|---|
| No token | `GET /v1/plants` without `Authorization` | Answers `401` `unauthenticated`; calls no provider |
| Valid token of owner A | `GET /v1/plants` | Calls `plants-api` with `X-Owner-Id` A and without `Authorization`; returns status and body unchanged |
| Forged owner | A valid token of owner A and the header `X-Owner-Id: B` | Calls the provider with `X-Owner-Id` A |
| Internal path | `GET /internal/v1/anything` with a valid token | Answers `404` `not_found`; calls no provider |
| Body too large | A body of 1 MB and 1 byte, without token | Answers `413`; step 1 comes before the token check |
| Rate limit | The 121st request with one token within a minute, at one instance | Answers `429` with `Retry-After` |
| Provider down | `ingest-api` refuses connections | Tries 3 times, answers `503` `unavailable` after about 1.2 seconds |
| Provider hangs | `alerts-api` never answers | Answers `503` `unavailable` after at most 17 seconds |
| Providers down | `POST /v1/tokens` while all three providers are down | Answers `201` with a new token |

## Health

`GET /healthz` answers `200` when the instance has a signing key and can serve. It does not check the providers: an instance stays in service while a provider is down, because the token operations and the other routes still work.
