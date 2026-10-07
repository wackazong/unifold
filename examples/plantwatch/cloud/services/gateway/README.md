---
unit: gateway
summary: Single entry point of the server side that authenticates callers and routes requests
kind: service
status: planned
provides:
  public-api:
    kind: http
    summary: Upload readings and query plants, history and alerts
    contract: doc/references/public-api.md
needs:
  ingest-api:
    kind: http
    summary: Accepts a batch of readings of one sensor
  plants-api:
    kind: http
    summary: Plants with their thresholds and their history
  alerts-api:
    kind: http
    summary: Open and past alerts per plant
---
# gateway

`gateway` is the one HTTP endpoint that clients reach. It issues and
verifies tokens, limits request size and request rate, and passes each
request on to whoever serves it. It keeps no data and looks into no body.

## Provides

### `public-api`

The complete HTTP API for clients, under one host and the path prefix
`/v1`. The operations and their bodies are defined above this unit and
cited in [doc/context.md](doc/context.md). `gateway` adds the following
guarantees:

- A request reaches a provider only with a valid token. The provider is
  told the owner the token stands for.
- An owner id that a client sends by itself is never passed on.
- Request and response bodies pass unchanged. What the provider answers is
  what the client receives.
- A request that no provider can answer in time gets `503` with
  `unavailable`, never a hanging connection. `gateway` gives up after at
  most 17 seconds.
- `gateway` answers the two token operations itself. They work while every
  provider is down.
- Every instance of `gateway` behaves the same and needs no other
  instance. Any number can run side by side.

Limits:

- A token cannot be withdrawn before it expires.
- Rate limits are counted per instance. With several instances a client
  can exceed the stated rate by that factor.

Example: a request without token.

```http
GET /v1/plants
```

```json
{"code": "unauthenticated", "message": "no bearer token"}
```

Contract: [public API as served by gateway](doc/references/public-api.md).

## Needs

Each of the three needs is an HTTP service inside the private network that
serves a part of the public API under the same paths, methods and bodies.
`gateway` expects of every provider:

- It trusts the header `X-Owner-Id` and limits its answer to that owner.
- It answers within 5 seconds, or with `503` when it cannot.
- Every operation can be repeated, because `gateway` repeats a call that
  failed.
- Its error bodies have the form of the public API.

### `ingest-api`

Serves the upload of a batch: every path below `/v1/sensors/`.

### `plants-api`

Serves plants, thresholds and history: `/v1/plants` and every path below
it.

### `alerts-api`

Serves alerts: `/v1/alerts` and every path below it.

## Out of scope

- Looking into, validating or changing a body.
- Combining the answers of several providers into one response.
- Storing anything: no sessions, no owners, no request log beyond the
  process log.
- Terminating TLS. Whoever publishes the port of `gateway` does that.
- Deciding what an owner may see. Each provider limits its answers to the
  owner it is told.

## More

- [AGENTS.md](AGENTS.md): why the entry point is built this way
- [doc/context.md](doc/context.md): the public API and the rules that
  `gateway` inherits
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- References: [public API as served by gateway](doc/references/public-api.md),
  [tokens](doc/references/tokens.md)
