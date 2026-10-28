# control-error

Kind: type

```json
{"code": "time_in_the_past", "message": "elapsed_s 3600 is below the current simulated time 86400"}
```

An error response has a body with `code` and `message`. The state of the program is unchanged.

| Status | `code` | When |
|---|---|---|
| 400 | `invalid_json` | the body is not a JSON object |
| 400 | `invalid_request` | a member or query parameter is unknown, has the wrong type or is out of range |
| 422 | `invalid_scenario` | the scenario breaks a rule of the scenario format; `message` names the member |
| 409 | `time_in_the_past` | `elapsed_s` is below the current simulated time |
| 404 | `not_found` | unknown path |
| 405 | `method_not_allowed` | known path, other method |
| 503 | `no_bluetooth_controller` | `PUT /scenario` when the host has no usable Bluetooth controller |
