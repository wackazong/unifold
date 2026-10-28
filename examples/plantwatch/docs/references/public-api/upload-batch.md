# upload-batch

Kind: command

```http
POST /v1/sensors/{sensor_id}/batches
Authorization: Bearer <token>

{"readings": [ { "...": "one reading" }, { "...": "one reading" } ]}
```

Pre: `sensor_id` is the sensor id of the sensor stick that took the readings; each element of `readings` is one reading as a JSON object in the form that the [reading schema](../reading-schema.md) defines, major version 1; at most 500 readings and 1 MB. The server does not check that the sensor stick is attached to a plant of the caller, or to any plant; a client attaches the sensor stick to a plant before it uploads ([put-plant](put-plant.md)). A client uploads in ascending order of sequence number, because alerts follow the order of acceptance.
Result: `200` with one result per uploaded reading, in the same order, also when every reading is rejected:

```json
{
  "results": [
    {"sequence_number": 4711, "status": "new"},
    {"sequence_number": 4712, "status": "duplicate"},
    {"sequence_number": 4713, "status": "rejected",
     "code": "value_out_of_range",
     "message": "soil moisture 104.2 is outside 0 to 100"}
  ]
}
```

| Field | Content |
|---|---|
| `sequence_number` | The sequence number of the reading. Absent if it cannot be read. |
| `status` | `new`: the reading is accepted now; the client may delete its copy. `duplicate`: a reading of this sensor stick with this sequence number was accepted earlier; the client may delete its copy. `rejected`: the reading is not accepted and will not be accepted when sent again; the client does not send it again. |
| `code`, `message` | Only with `rejected`: the reason |

| `code` of a rejection | Reason |
|---|---|
| `malformed_reading` | The object does not conform to the [reading schema](../reading-schema.md). |
| `value_out_of_range` | A measured value lies outside the range of its quantity. |
| `time_in_future` | The time of the reading is more than 24 hours ahead of the server's clock. |
| `too_old` | The time of the reading is more than 90 days in the past. |

The server recognises a duplicate by sensor id and sequence number alone; it does not compare the content with the reading it accepted earlier. The server keeps fields of a reading that it does not know. The server accepts readings in any order; a reading that is older than one already evaluated for the same sensor stick enters history and does not change an alert. A reading with an estimated time is accepted, enters history and does not change an alert. Readings of a sensor stick that is attached to no plant are accepted, enter no history and cause no alert. An empty `readings` array is valid and returns an empty `results` array. After `200` the client deletes or marks as delivered every reading with `new` or `duplicate` and drops or sets aside every `rejected` reading.
Errors: an error status means that no reading of the batch was looked at: `400` `invalid_request` for a body that is not of the form above or a malformed `sensor_id`; `413` `payload_too_large` for more than 500 readings or more than 1 MB; and the [errors](error.md) every operation can answer. After `503`, `429` or no response the client keeps all readings and sends the same batch again later; after `401` it renews the token, then sends the same batch again; after `400` or `413` the batch is built wrongly, and sending it again unchanged does not help.
Examples: uploads for the sensor stick `00a1b2c3d4e5f607` at 2026-10-06T09:00:00Z; unless stated, a reading is valid and was taken at 08:45:00Z.

| Case | Uploaded | Response |
|---|---|---|
| New reading | Sequence number 4711, never uploaded | `200`, `4711` is `new` |
| The same batch again | Sequence number 4711 once more | `200`, `4711` is `duplicate` |
| Value out of range | 4712 with `soil_moisture` 104.2 | `200`, `4712` is `rejected`, `value_out_of_range` |
| Absent quantity written as `null` | 4713 with `"light": null` | `200`, `4713` is `rejected`, `malformed_reading` |
| Time in the future | 4714, taken at 2026-10-07T09:00:01Z | `200`, `4714` is `rejected`, `time_in_future` |
| Too old | 4715, taken at 2026-07-08T08:59:59Z | `200`, `4715` is `rejected`, `too_old` |
| Mixed batch | 4716 valid, 4717 out of range, 4718 valid | `200`, results `new`, `rejected`, `new` in this order |
| Estimated time | 4719 with an estimated time | `200`, `4719` is `new`; no alert opens or closes |
| Empty batch | `{"readings": []}` | `200` with `{"results": []}` |
| Too many readings | 501 readings | `413` `payload_too_large`; no reading is looked at |
| Malformed sensor id | Path `/v1/sensors/00A1/batches` | `400` `invalid_request` |
| Body too large | A body of 1 MB and 1 byte | `413` `payload_too_large` |
