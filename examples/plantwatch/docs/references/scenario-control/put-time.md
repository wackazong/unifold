# put-time

Kind: command

```http
PUT /time

{"elapsed_s": <integer, optional>, "rate": <number 0 to 3600, optional>}
```

Pre: `elapsed_s`, if given, is not below the current simulated time.
Result: `200` with the [state](emulator-state.md) object. The program moves simulated time to `elapsed_s`, carries out every event and takes every reading that is due on the way, in order. The response is sent when all of that is done and the Status characteristic shows the result: within 5 s for every 2 880 readings taken on the way. A target equal to the current time changes nothing and succeeds. With a rate above 0, simulated time also runs by itself; readings are then no longer reproducible to the second.
Errors: `409` `time_in_the_past` when `elapsed_s` is below the current simulated time; `400` `invalid_request` when a member is unknown, has the wrong type or is out of range; `400` `invalid_json`. The state of the program is unchanged after an error.
Examples:

| Case | Request | Expected |
|---|---|---|
| one day | `PUT /time` with `{"elapsed_s": 86400}` | `200`; the state object shown in [state](emulator-state.md) |
| the same again | `PUT /time` with `{"elapsed_s": 86400}` | `200`; the same state object; no reading is added |
| back in time | `PUT /time` with `{"elapsed_s": 3600}` | `409` `time_in_the_past`; the state is unchanged |
| across the restart | `PUT /time` with `{"elapsed_s": 172800}` | `200`; `tick` is 2 / 0, `readings_taken` 193, `link.bonding_open` `true` |
| unknown member | `PUT /time` with `{"elapsed": 5}` | `400` `invalid_request` |
| overflow | freshly loaded, then `PUT /time` with `{"elapsed_s": 2592000}`, no confirm | `readings_taken` 2881, `stored` 2 880 from 2 to 2881, `overflow` `true`; `GET /readings?limit=1` returns reading 1 with `state` `overwritten` |
