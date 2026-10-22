# scenario-control API

The contract of the capability `scenario-control`: the HTTP API with which a client drives the simulated sensor stick. The scenario document itself is defined in the [scenario format](scenario-format.md).

## General

| Property | Value |
|---|---|
| Address | `http://127.0.0.1:8650`. The capability is set with the command-line option `--control-capability`. |
| Bodies | JSON in UTF-8, member names lower-case with underscores |
| Authentication | None. The API is reachable from the local machine only. |
| Concurrency | The program handles one request at a time, in the order of arrival |
| Repeating a request | Always allowed. Every request states a target state, not a step. |

## Requests

| Request | Purpose | Success |
|---|---|---|
| `GET /state` | Returns the state object | 200 |
| `PUT /scenario` | Loads the scenario in the body and resets the simulated sensor stick | 200 with the state object |
| `PUT /time` | Moves simulated time forward to a given value, or sets the rate | 200 with the state object |
| `PUT /link` | Sets radio range and transfer faults | 200 with the state object |
| `GET /readings` | Returns the readings taken since the scenario was loaded | 200 |

## The state object

```json
{
  "scenario": "drying-out",
  "elapsed_s": 86400,
  "rate": 0,
  "tick": {"boot_counter": 1, "seconds_since_boot": 86400},
  "sampling_interval_s": 900,
  "readings_taken": 97,
  "stored": {"count": 97, "oldest": 1, "newest": 97},
  "confirmed_up_to": 0,
  "overflow": false,
  "link": {
    "in_range": true,
    "advertising": true,
    "connected": false,
    "bonds": 0,
    "bonding_open": false,
    "drop_fetch_after": null
  }
}
```

| Member | Meaning |
|---|---|
| `scenario` | Name of the loaded scenario. At start it is the built-in scenario `steady`, running at rate 1. |
| `elapsed_s` | Simulated seconds since the scenario was loaded |
| `rate` | Simulated seconds per real second. 0: time stands still. |
| `tick` | The tick count of the simulated sensor stick |
| `readings_taken` | Number of readings taken since the scenario was loaded |
| `stored` | Readings taken and not confirmed: their number, and the lowest and highest sequence number, each 0 if none |
| `confirmed_up_to` | Highest sequence number a central has confirmed, 0 if none |
| `overflow` | `true` if a stored reading has been overwritten since the last confirm or restart |
| `link.in_range` | As set with `PUT /link` |
| `link.advertising`, `link.connected` | What the radio side is doing now |
| `link.bonds` | Number of centrals that have bonded |
| `link.bonding_open` | `true` while a new bond is accepted |
| `link.drop_fetch_after` | As set with `PUT /link`, `null` once it has taken effect |

## PUT /scenario

The body is a scenario document. On success the simulated sensor stick is as new: simulated time is 0, the rate is 0, no reading from before is stored, no central is bonded, bonding is open, a connected central is disconnected, and the link settings have their defaults. The first reading of the scenario is taken before the response is sent. The program starts to advertise.

## PUT /time

| Member | Type | Meaning |
|---|---|---|
| `elapsed_s` | integer | Target for simulated time. Optional. |
| `rate` | number, 0 to 3600 | New rate. Optional. |

- The program moves simulated time to `elapsed_s`, carries out every event and takes every reading that is due on the way, in order.
- The response is sent when all of that is done and the Status characteristic shows the result: within 5 s for every 2 880 readings taken on the way.
- A target equal to the current time changes nothing and succeeds.
- A target below the current time fails with `time_in_the_past`.
- With a rate above 0, simulated time also runs by itself. Readings are then no longer reproducible to the second.

## PUT /link

| Member | Type | Default | Meaning |
|---|---|---|---|
| `in_range` | boolean | `true` | `false`: the program drops a connection at once and stops advertising, as if the sensor stick were out of radio range. Sampling goes on. |
| `drop_fetch_after` | integer or `null` | `null` | The program drops the connection during the next fetch after it has sent this many records, without sending a fetch result. Takes effect once. |

Members that are left out keep their value.

## GET /readings

| Query parameter | Default | Meaning |
|---|---|---|
| `from` | 0 | Lowest sequence number to return |
| `limit` | 1000 | Largest number of readings to return, at most 5000 |

```json
{
  "readings": [
    {
      "sequence_number": 1,
      "boot_counter": 1,
      "seconds_since_boot": 0,
      "elapsed_s": 0,
      "soil_moisture": 60.0,
      "light": 0,
      "temperature": 21.4,
      "state": "stored"
    }
  ],
  "more": false
}
```

A quantity that is absent in a reading has no member. `state` is `stored`, `delivered` (covered by a confirm) or `overwritten` (discarded to make room before any confirm). `more` is `true` when readings with a higher sequence number exist.

## Errors

An error response has a body with `code` and `message`. The state of the program is unchanged.

| Status | `code` | When |
|---|---|---|
| 400 | `invalid_json` | The body is not a JSON object |
| 400 | `invalid_request` | A member or query parameter is unknown, has the wrong type or is out of range |
| 422 | `invalid_scenario` | The scenario breaks a rule of the scenario format. `message` names the member. |
| 409 | `time_in_the_past` | `elapsed_s` is below the current simulated time |
| 404 | `not_found` | Unknown path |
| 405 | `method_not_allowed` | Known path, other method |
| 503 | `no_bluetooth_controller` | `PUT /scenario` when the host has no usable Bluetooth controller |

## Examples

The scenario is `drying-out` from the [scenario format](scenario-format.md): 900 s interval, a restart at 172 800 s. Each case follows the one before unless it says otherwise.

| Case | Request | Expected |
|---|---|---|
| At start | `GET /state` | 200. `scenario` is `steady`, `rate` 1, `link.advertising` `true` |
| Load | `PUT /scenario` with `drying-out` | 200. `elapsed_s` 0, `readings_taken` 1, `stored` 1 from 1 to 1, `link.advertising` and `link.bonding_open` `true`, `link.bonds` 0 |
| One day | `PUT /time` with `{"elapsed_s": 86400}` | 200. The state object shown above. |
| The same again | `PUT /time` with `{"elapsed_s": 86400}` | 200. The same state object; no reading is added. |
| Back in time | `PUT /time` with `{"elapsed_s": 3600}` | 409 `time_in_the_past`. The state is unchanged. |
| Across the restart | `PUT /time` with `{"elapsed_s": 172800}` | 200. `tick` is 2 / 0, `readings_taken` 193, `link.bonding_open` `true` |
| Unknown member | `PUT /time` with `{"elapsed": 5}` | 400 `invalid_request` |
| Out of range | `PUT /link` with `{"in_range": false}` while a central is connected | 200. `link.connected` and `link.advertising` `false`. Time and sampling are untouched. |
| A cut fetch | `PUT /link` with `{"in_range": true, "drop_fetch_after": 10}`, then a central fetches | The central gets 10 records and no fetch result. Afterwards `link.drop_fetch_after` is `null` and `stored.count` is as before. |
| Overflow | Freshly loaded, then `PUT /time` with `{"elapsed_s": 2592000}`, no confirm | `readings_taken` 2881, `stored` 2 880 from 2 to 2881, `overflow` `true`. `GET /readings?limit=1` returns reading 1 with `state` `overwritten`. |
