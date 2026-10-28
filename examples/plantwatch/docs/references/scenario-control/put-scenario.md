# put-scenario

Kind: command

```http
PUT /scenario

<a scenario document>
```

Pre: the body is a scenario document; the host has a usable Bluetooth controller.
Result: `200` with the [state](emulator-state.md) object. The simulated sensor stick is as new: simulated time is 0, the rate is 0, no reading from before is stored, no central is bonded, bonding is open, a connected central is disconnected, and the link settings have their defaults. The first reading of the scenario is taken before the response is sent. The program starts to advertise.
Errors: `400` `invalid_json` when the body is not a JSON object; `422` `invalid_scenario` when the scenario breaks a rule of the scenario format, with `message` naming the member; `503` `no_bluetooth_controller` when the host has no usable Bluetooth controller. The state of the program is unchanged after an error.
Examples:

| Case | Request | Expected |
|---|---|---|
| load | `PUT /scenario` with `drying-out` | `200`; `elapsed_s` 0, `readings_taken` 1, `stored` 1 from 1 to 1, `link.advertising` and `link.bonding_open` `true`, `link.bonds` 0 |
| broken scenario | `PUT /scenario` with a document whose `sampling_interval_s` is missing | `422` `invalid_scenario`, `message` names `sampling_interval_s`; the state is unchanged |
| no controller | `PUT /scenario` on a host without a usable Bluetooth controller | `503` `no_bluetooth_controller` |
