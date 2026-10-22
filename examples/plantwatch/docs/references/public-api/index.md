# Public API

The contract of the capability `public-api`: the HTTP API through which a client acts for one owner. Project terms and conventions that this contract uses are in the [glossary](../glossary.md) and the [conventions](../conventions.md).

## Parts

A reading inside an upload or a history has the form of the
[reading schema](../reading-schema.md).

| Part | Content |
|---|---|
| This file | Rules for all operations: versions, tokens, errors, repetition, consistency, limits |
| [uploads.md](uploads.md) | Upload a batch of readings |
| [plants.md](plants.md) | Plants, sensor sticks, thresholds and history |
| [alerts.md](alerts.md) | Open and past alerts |

## Operations

| Operation | Purpose | Part |
|---|---|---|
| `POST /v1/owners` | Create an owner and get a token | This file |
| `POST /v1/tokens` | Get a further token for the same owner | This file |
| `POST /v1/sensors/{sensor_id}/batches` | Upload readings of one sensor stick | [uploads.md](uploads.md) |
| `GET /v1/plants` | List the plants of the owner | [plants.md](plants.md) |
| `PUT /v1/plants/{plant_id}` | Create or replace a plant | [plants.md](plants.md) |
| `GET /v1/plants/{plant_id}` | Read a plant | [plants.md](plants.md) |
| `DELETE /v1/plants/{plant_id}` | Delete a plant and its history | [plants.md](plants.md) |
| `GET /v1/plants/{plant_id}/history` | Read the history of a plant | [plants.md](plants.md) |
| `GET /v1/alerts` | List alerts of the owner | [alerts.md](alerts.md) |
| `GET /v1/alerts/{alert_id}` | Read an alert | [alerts.md](alerts.md) |

## General rules

- Every path starts with `/v1`. A change that would break a client gets a new prefix; `/v1` stays available beside it.
- Bodies, field names, identifiers and times follow the project
  [conventions](../conventions.md).
- A client ignores response fields it does not know.
- A field without a value is absent. `null` is not used.

## Tokens

Every request except `POST /v1/owners` carries a token:

```http
Authorization: Bearer <token>
```

A token stands for one owner. It is an opaque string for the client and is valid for 365 days.

`POST /v1/owners` needs no token and has no body. It creates an owner. Response `201`:

```json
{
  "owner_id": "5b0e2d0a-8f0c-4d0e-9a57-0c1a2f3b4c5d",
  "token": "<token>",
  "expires_at": "2027-10-06T09:00:00Z"
}
```

`POST /v1/tokens` has no body. It returns a new token for the owner of the token in the request. The old token stays valid until it expires. Response `201`:

```json
{"token": "<token>", "expires_at": "2027-10-06T09:00:00Z"}
```

Rules:

- A client renews its token before it expires. With an expired token the owner's data can no longer be reached.
- Several devices act for the same owner when each holds a token of that owner. How a token gets from one device to another is outside this API.
- A token cannot be withdrawn before it expires.

## Errors

An error response has the body `{"code": "...", "message": "..."}`. A client decides by status and `code`. `message` is English text for developers.

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

## Repetition

Every request may be repeated, for example after a lost response.

- An upload reports readings it already has as `duplicate`.
- `PUT` and `DELETE` lead to the same state and the same response when they are sent again.
- `POST /v1/owners` creates another owner each time. A client that has lost the response uses the new owner; nothing is stored for the lost one.

## Consistency

- A change to a plant is visible to the next request.
- A reading reported as `new` appears in the history of its plant within 10 seconds after the upload response, not before it.
- An alert caused by a reading is visible, and its notification is handed to the push service, within 1 minute after the upload response.
- A changed threshold applies to readings that are evaluated more than 60 seconds after the change.

## Limits

| Limit | Value |
|---|---|
| Size of a request body | 1 MB |
| Readings per batch | 500 |
| Plants per owner | 50 |
| Items per page of a list or history | 1 000 |
| Requests per token | 120 per minute |
| `POST /v1/owners` per client address | 10 per hour |
| Age of a reading at upload | 90 days |

## Examples

| Case | Request | Response |
|---|---|---|
| First start of a client | `POST /v1/owners` without token | `201` with `owner_id`, `token`, `expires_at` |
| No token | `GET /v1/plants` without `Authorization` | `401` `unauthenticated` |
| Expired token | Any request, 366 days after the token was issued | `401` `unauthenticated` |
| Too many requests | The 121st request with one token within a minute | `429` `rate_limited` with `Retry-After` |
| Body too large | A body of 1 MB and 1 byte | `413` `payload_too_large` |
| Plant of another owner | `GET /v1/plants/{plant_id}` with the token of owner B for a plant of owner A | `404` `not_found` |
| Repeated request | The same `PUT /v1/plants/{plant_id}` twice | `200` twice, with equal bodies |
