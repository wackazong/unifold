<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: device

[plantwatch](../../../docs/diagrams/component.md) / **device** · [README](../../README.md) · [component](component.md)

`device` inside `plantwatch`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    u_device["device (firmware)"]
    u_mobile["mobile (app)"]
    u_test_drig["test-rig (test)"]
  end
  n_root___ambient_dsensor{{"ambient-sensor"}}
  n_root___soil_dprobe{{"soil-probe"}}
  u_mobile -->|"sensor-link → ble-link (real)"| u_device
  u_test_drig -->|"device-under-test → ble-link (real)"| u_device
  u_device -->|"ambient-sensor"| n_root___ambient_dsensor
  u_device -->|"soil-probe"| n_root___soil_dprobe
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_device,u_mobile,u_test_drig planned
  class u_device focus
```

| Unit | Kind | Responsibility | Status | Diagram |
|---|---|---|---|---|
| [device](../../README.md) | firmware | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | **planned** | [component](component.md) |
| [mobile](../../../mobile/README.md) | app | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | **planned** | [component](../../../mobile/docs/diagrams/component.md) |
| [test-rig](../../../test-rig/README.md) | test | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware | **planned** | [context](../../../test-rig/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability |
|---|---|---|---|---|
| soil-probe | hardware | [contract](../../../docs/references/soil-probe.md) | outside the project, as need `soil-probe` of the root | |
| ambient-sensor | hardware | [contract](../../../docs/references/ambient-sensor.md) | outside the project, as need `ambient-sensor` of the root | |

### Who uses what this unit provides

| Capability | Kind | Contract | Used by | As need |
|---|---|---|---|---|
| ble-link | protocol | [contract](../../../docs/references/ble-profile/index.md) | [mobile/ble-client](../../../mobile/ble-client/README.md) (planned) (real) | sensor-link |
| ble-link | protocol | [contract](../../../docs/references/ble-profile/index.md) | [test-rig](../../../test-rig/README.md) (planned) (real) | device-under-test |
