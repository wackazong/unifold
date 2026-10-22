# Calls between services

Rules for HTTP calls from one service of `cloud` to another inside the
private network. The reason for trusting the caller is in
[0003](../decisions/0003-one-gateway-is-the-only-public-entry.md).

## Headers

| Header | Set by | Content |
|---|---|---|
| `X-Owner-Id` | The service that has verified the client's token | The UUID of the owner the request acts for |
| `X-Request-Id` | The first service that sees a request | A UUID that every service passes on and writes to its log |

- A service that serves an operation of the
  [public API](public-api/index.md) requires `X-Owner-Id` and limits its
  answer to that owner. Without the header it answers `400` with
  `invalid_request`.
- A service does not verify tokens. It trusts `X-Owner-Id`, because it is
  reachable only from the private network.
- A `X-Owner-Id` header that arrives from outside the private network is
  removed before the request is passed on.

## Paths

| Kind of operation | Path | Caller |
|---|---|---|
| Operation of the public API | The same method, path, parameters and bodies as the [public API](public-api/index.md) defines | A service that acts for a client and sends `X-Owner-Id` |
| Internal operation | Starts with `/internal/v1/` | A service that acts for itself; no `X-Owner-Id` |
| Health | `GET /healthz` | The container host and other services |

- A path that starts with `/internal/` is never served to a client.
- `GET /healthz` answers `200` when the service can do its work and `503`
  when something it needs cannot be reached.
- Every service listens on port 8080 of its container.

## Errors

- Error bodies and codes are those of the
  [public API](public-api/index.md).
- A service that cannot reach something it needs answers `503` with
  `unavailable`.
- A service passes on the error of a service it called for a client
  unchanged.

## Time limits and repetition

- A caller waits at most 5 seconds for a response.
- Every operation can be repeated. A caller repeats a call that timed out
  or answered `503` at most twice, after 0.2 and after 1 second. Then it
  reports `503` to its own caller.
- An event consumer that cannot complete a call leaves the event
  unconfirmed ([events](events.md)).
