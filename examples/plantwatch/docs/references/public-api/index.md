# Public API

Contract of `cloud.public-api`: the HTTP API through which a client acts for one owner. `mobile.cloud-api` and `test-rig.cloud-api` use it. Project terms and conventions that this contract uses are in the [glossary](../glossary.md) and the [conventions](../conventions.md). Notation: HTTP with JSON bodies, as the conventions define them.
Sources: the requirements, the product parameters and the reading schema of plantwatch.
Binding: http
Version: 1

A reading inside an upload or a history has the form of the [reading schema](../reading-schema.md).

## Use

A client creates an owner once and keeps the token it gets. It sends that token with every other request and renews it before it expires. Before it uploads the readings of a sensor stick, it attaches the sensor stick to a plant with `put-plant`. It uploads readings in ascending order of sequence number. The API keeps no session: every request stands alone, any part may be called at any time, and every request may be repeated.

Rules that hold for every part:

- Every path starts with `/v1`. A change that would break a client gets a new prefix; `/v1` stays available beside it.
- Bodies, field names, identifiers and times follow the project [conventions](../conventions.md).
- A client ignores response fields it does not know.
- A field without a value is absent. `null` is not used.
- Request and response bodies pass through the gateway unchanged; what the provider answers is what the client receives.

Every request except `POST /v1/owners` carries a token:

```http
Authorization: Bearer <token>
```

A token stands for one owner. It is an opaque string for the client and is valid for 365 days. A client renews its token before it expires; with an expired token the owner's data can no longer be reached. Several devices act for the same owner when each holds a token of that owner; how a token gets from one device to another is outside this API. A token cannot be withdrawn before it expires.

Every request may be repeated, for example after a lost response. An upload reports readings it already has as `duplicate`. `PUT` and `DELETE` lead to the same state and the same response when they are sent again. `POST /v1/owners` creates another owner each time; a client that has lost the response uses the new owner, and nothing is stored for the lost one.

## Qualities

| Aspect | Guarantee |
|---|---|
| consistency | a change to a plant is visible to the next request |
| latency | a reading reported as `new` appears in the history of its plant within 10 seconds after the upload response, not before it; an alert caused by a reading is visible, and its notification is handed to the push service, within 1 minute after the upload response; a changed threshold applies to readings that are evaluated more than 60 seconds after the change |
| idempotency | every request may be repeated; an upload reports a known reading as `duplicate`, and a repeated `PUT` or `DELETE` gives the same state and response |
| security | a token stands for one owner, is opaque, is valid for 365 days and cannot be withdrawn before it expires; a request reaches a provider only with a valid token, and the provider is told the owner the token stands for; an owner id that a client sends by itself is never passed on |
| limits | a request body of 1 MB; 500 readings per batch; 50 plants per owner; 1 000 items per page of a list or history; a reading at most 90 days old at upload |
| throughput | 120 requests per minute per token; 10 `POST /v1/owners` per hour per client address; rate limits are counted per gateway instance, so with several instances a client can exceed the stated rate by that factor |
| timeout | a request that no provider can answer in time gets `503` with `unavailable`, never a hanging connection; the gateway gives up after at most 17 seconds; a client counts a request without an answer after 20 seconds as "try again later" |
| availability | the two token operations are answered by the gateway itself and work while every provider is down; any number of gateway instances run side by side, and none needs another |

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
| [plant](plant.md) | the plant |
| [alert](alert.md) | the alert, what is judged, and its life |
| [error](error.md) | the error response and its codes |

## Fake

Replays the examples of the parts: an HTTP server in the test that answers the requests of the tables with the responses given and `404` for everything else. Faults it can inject: `503` `unavailable`, `429` `rate_limited` with `Retry-After`, `401` `unauthenticated`, no response.
