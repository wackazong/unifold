# gateway

`gateway` is the one HTTP endpoint that clients reach. It issues and
verifies tokens, limits request size and request rate, and passes each
request on to whoever serves it. It keeps no data and looks into no body.

## Why

Clients need one address and one way to prove for which owner they act.
`gateway` exists so that this is solved once: it is the only code that
understands tokens, and everything it passes a request to may trust the
owner it is told. It changes when the way a client proves its owner
changes, or when the public API gets a new group of paths.

It is cut as thin as possible. It routes by path prefix and does not look
into bodies, so a change to a resource never needs a change here. It keeps
no data, so any number of instances can run and none of them is a reason
for an upload to fail. That is why tokens
are self-contained and signed instead of looked up
([0001](docs/decisions/0001-self-contained-signed-tokens.md)), and why rate
limits are counted in memory
([0002](docs/decisions/0002-rate-limits-are-counted-per-instance.md)).

The price of statelessness: a token cannot be withdrawn, and whoever holds
the signing key can act for every owner. The key is the one secret of this
unit.

What must stay true: no request reaches a provider without a verified
token, and no owner id that came from outside is ever passed on.

## Capabilities

### `public-api`

The complete HTTP API for clients, under one host and the path prefix
`/v1`. The operations and their bodies are defined above this unit and
cited in [docs/explanation/context.md](docs/explanation/context.md). `gateway` adds the following
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

Contract: [public API as served by gateway](docs/references/public-api.md).

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
- Terminating TLS. Whoever publishes the capability of `gateway` does that.
- Deciding what an owner may see. Each provider limits its answers to the
  owner it is told.

## Read next

1. [docs/references/public-api.md](docs/references/public-api.md): how a
   request is handled and where it goes
2. [docs/references/tokens.md](docs/references/tokens.md): form, signing and
   verification of tokens
3. [docs/explanation/context.md](docs/explanation/context.md): what the unit
   inherits
4. [Context diagram](docs/diagrams/context.md),
   [decisions](docs/decisions/index.md)
