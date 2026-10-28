# Public API

Contract of `cloud.public-api`: the HTTP API through which a client acts for one owner. `mobile.cloud-api` and `test-rig.cloud-api` use it. Project terms and conventions that this contract uses are in the [glossary](../glossary.md) and the [conventions](../conventions.md). Notation: HTTP with JSON bodies, as the conventions define them.
Sources: the requirements, the product parameters and the reading schema of plantwatch; decision 0006 of plantwatch.

A reading inside an upload or a history has the form of the [reading schema](../reading-schema.md).

## Parts

| Part | Operation |
|---|---|
| [create-owner](create-owner.md) | `POST /v1/owners`: create an owner and get a token |
| [create-token](create-token.md) | `POST /v1/tokens`: get a further token for the same owner |
| [upload-batch](upload-batch.md) | `POST /v1/sensors/{sensor_id}/batches`: upload readings of one sensor stick |
| [list-plants](list-plants.md) | `GET /v1/plants`: list the plants of the owner |
| [put-plant](put-plant.md) | `PUT /v1/plants/{plant_id}`: create or replace a plant |
| [get-plant](get-plant.md) | `GET /v1/plants/{plant_id}`: read a plant |
| [delete-plant](delete-plant.md) | `DELETE /v1/plants/{plant_id}`: delete a plant and its history |
| [get-history](get-history.md) | `GET /v1/plants/{plant_id}/history`: read the history of a plant |
| [list-alerts](list-alerts.md) | `GET /v1/alerts`: list alerts of the owner |
| [get-alert](get-alert.md) | `GET /v1/alerts/{alert_id}`: read an alert |
| [plant](plant.md) | the plant |
| [alert](alert.md) | the alert, what is judged, and its life |
| [error](error.md) | the error response and its codes |

## General rules

- Every path starts with `/v1`. A change that would break a client gets a new prefix; `/v1` stays available beside it.
- Bodies, field names, identifiers and times follow the project [conventions](../conventions.md).
- A client ignores response fields it does not know.
- A field without a value is absent. `null` is not used.

## Tokens

Every request except `POST /v1/owners` carries a token:

```http
Authorization: Bearer <token>
```

A token stands for one owner. It is an opaque string for the client and is valid for 365 days.

- A client renews its token before it expires. With an expired token the owner's data can no longer be reached.
- Several devices act for the same owner when each holds a token of that owner. How a token gets from one device to another is outside this API.
- A token cannot be withdrawn before it expires.

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

## Fake

Replays the examples of the parts: an HTTP server in the test that answers the requests of the tables with the responses given and `404` for everything else. Faults it can inject: `503` `unavailable`, `429` `rate_limited` with `Retry-After`, `401` `unauthenticated`, no response.
