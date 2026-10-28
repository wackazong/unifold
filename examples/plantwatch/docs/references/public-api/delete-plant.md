# delete-plant

Kind: command

```http
DELETE /v1/plants/{plant_id}
Authorization: Bearer <token>
```

Pre: a valid token.
Result: `204`; the plant and its history are removed and the sensor stick is detached. `DELETE` of a plant that does not exist answers `204`. Open alerts of the plant end when they expire.
Errors: `404` `not_found` for a plant id that belongs to another owner; the [errors](error.md) that every operation can answer.
Examples:

| Case | Request | Response |
|---|---|---|
| Delete twice | `DELETE` of P, then again | `204` both times |
