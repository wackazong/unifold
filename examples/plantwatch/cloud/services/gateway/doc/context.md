# Context of gateway

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

| Source | What it says | What it means here |
|---|---|---|
| [cloud/0003 One gateway is the only public entry](../../../doc/decisions/0003-one-gateway-is-the-only-public-entry.md) | One service is reachable from outside. It authenticates and routes; it does not change bodies. The services behind it trust the owner id it passes on. | This unit is that service. It must never pass on a request without a verified token, and never an owner id that came from outside. |
| [cloud: public API](../../../doc/references/public-api/index.md) | The contract with clients: all operations under `/v1`, tokens that are opaque to the client and valid for 365 days, the error codes, the limits (1 MB per body, 120 requests per minute per token, 10 new owners per hour per client address). | The contract of the port `public-api`. `gateway` implements the token operations, the limits and the errors `unauthenticated`, `payload_too_large`, `rate_limited` and `unavailable` itself and passes everything else on. |
| [cloud: public API, uploads](../../../doc/references/public-api/uploads.md) | `POST /v1/sensors/{sensor_id}/batches` uploads a batch. | Paths below `/v1/sensors/` go to the need `ingest-api`. |
| [cloud: public API, plants](../../../doc/references/public-api/plants.md) | Operations on `/v1/plants` and below read and change plants and read history. | These paths go to the need `plants-api`. |
| [cloud: public API, alerts](../../../doc/references/public-api/alerts.md) | Operations on `/v1/alerts` and below read alerts. | These paths go to the need `alerts-api`. |
| [cloud: calls between services](../../../doc/references/service-calls.md) | The service that verified the token sets `X-Owner-Id`; the first service sets `X-Request-Id`. A caller waits at most 5 seconds and repeats a failed call at most twice, after 0.2 and 1 second. Paths below `/internal/` are never served to a client. Every service answers `GET /healthz`. | `gateway` sets both headers, removes an incoming `X-Owner-Id`, follows the time limits, and answers `404` for `/internal/`. |
| [plantwatch: HTTP ports](../../../../doc/references/conventions.md) | Bodies are JSON in UTF-8; an error has the fields `code` and `message`; a repeated request succeeds again. | The errors that `gateway` produces itself have this form. |
| [plantwatch: identifiers](../../../../doc/references/conventions.md) | An owner has a UUID in lower-case text form. | The owner id in a token and in `X-Owner-Id`. |
| [plantwatch: owner](../../../../doc/references/glossary.md) | The user a plant belongs to. | A token stands for exactly one owner. `gateway` creates an owner by issuing the first token for a new UUID. |
