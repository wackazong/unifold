# put-plant

Kind: command

```http
PUT /v1/plants/{plant_id}
Authorization: Bearer <token>

{"name": "...", "sensor_id": "...", "thresholds": {...}}
```

Pre: a valid token; the body holds the client fields of the [plant](plant.md): `name` required, `sensor_id` and `thresholds` optional; every threshold lies in the range of its quantity and `min` is below `max`.
Result: `200` with the plant. `PUT` creates the plant if the owner has none with this id and replaces it otherwise. It replaces all client fields: a field that is absent in the body is removed from the plant. The history stays. To move a sensor stick, detach it from the first plant, then attach it to the second. Sent again, the request leads to the same state and the same response.
Errors: `400` `invalid_request` when a threshold lies outside the range of its quantity or `min` is not below `max`; `409` `sensor_already_attached` when the `sensor_id` is attached to another plant; `409` `plant_limit_reached` when the request would create the 51st plant of the owner; `404` `not_found` for a plant id of another owner; and the [errors](error.md) every operation can answer.
Examples: for an owner who has the plant P with sensor stick S attached.

| Case | Request | Response |
|---|---|---|
| Create | `PUT` of a new id with `name` | `200` with the plant; `created_at` equals `updated_at` |
| Replace without thresholds | `PUT` of P with `name` only | `200`; P has no `thresholds` and no `sensor_id`; its history stays |
| Threshold out of range | `PUT` with `soil_moisture.min` 120.0 | `400` `invalid_request` |
| `min` not below `max` | `PUT` with `temperature` `{"min": 30.0, "max": 30.0}` | `400` `invalid_request` |
| Sensor stick in use | `PUT` of another plant with `sensor_id` S | `409` `sensor_already_attached` |
| 51st plant | `PUT` of a new id while the owner has 50 plants | `409` `plant_limit_reached` |
| Repeated request | The same `PUT /v1/plants/{plant_id}` twice | `200` twice, with equal bodies |
