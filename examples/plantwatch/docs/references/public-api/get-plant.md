# get-plant

Kind: query

```http
GET /v1/plants/{plant_id}
Authorization: Bearer <token>
```

Pre: a valid token.
Result: `200` with the [plant](plant.md).
Errors: `404` `not_found` when the plant does not exist or belongs to another owner; the [errors](error.md) that every operation can answer.
Examples:

| Case | Request | Response |
|---|---|---|
| Own plant | `GET /v1/plants/{P}` with a token of the owner of P | `200` with P |
| Plant of another owner | `GET /v1/plants/{plant_id}` with the token of owner B for a plant of owner A | `404` `not_found` |
