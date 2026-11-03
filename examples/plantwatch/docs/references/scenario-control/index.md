# scenario-control

Contract of `emulator.scenario-control`: the HTTP API with which a client drives the simulated sensor stick. The scenario document itself is defined in the [scenario format](../scenario-format.md). Notation: HTTP with JSON bodies, member names lower-case with underscores.
Sources: the scenario format and the BLE profile of plantwatch.

## Use

A client loads a scenario with `put-scenario`, which resets the simulated sensor stick. Then it moves simulated time forward with `put-time`, sets radio range and transfer faults with `put-link`, and reads the state and the readings. Every request states a target state, so it may be repeated. The only order the API enforces is that simulated time never goes back: a `put-time` below the current time fails.

## General

| Property | Value |
|---|---|
| address | `http://127.0.0.1:8650`; the port is set with the command-line option `--control-port` |
| bodies | JSON in UTF-8, member names lower-case with underscores |
| authentication | none; the API is reachable from the local machine only |
| concurrency | the program handles one request at a time, in the order of arrival |
| repeating a request | always allowed; every request states a target state, not a step |

## Parts

| Part | What it is |
|---|---|
| [get-state](get-state.md) | returns the state object |
| [put-scenario](put-scenario.md) | loads the scenario in the body and resets the simulated sensor stick |
| [put-time](put-time.md) | moves simulated time forward to a given value, or sets the rate |
| [put-link](put-link.md) | sets radio range and transfer faults |
| [get-readings](get-readings.md) | returns the readings taken since the scenario was loaded |
| [state](emulator-state.md) | the state object |
| [error](control-error.md) | the error response |

## Examples

The examples of the parts use the scenario `drying-out` from the [scenario format](../scenario-format.md): 900 s interval, a restart at 172 800 s. Each case follows the one before unless it says otherwise.

## Fake

Replays the examples: an HTTP server in the test that answers the requests of the tables with the responses given. Faults it can inject: `503` `no_bluetooth_controller`.
