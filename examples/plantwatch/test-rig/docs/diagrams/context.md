<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: test-rig

[plantwatch](../../../docs/diagrams/component.md) / **test-rig** · [README](../../README.md)

`test-rig` inside `plantwatch`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    u_cloud["cloud"]
    u_device["device"]
    u_emulator["emulator"]
    u_test_drig["test-rig"]
  end
  p_root___test_dreport(["test-report"])
  u_test_drig -->|"device-under-test → ble-link (real)"| u_device
  u_test_drig -.->|"device-under-test → ble-link (simulated)"| u_emulator
  u_test_drig -->|"scenario-control (optional)"| u_emulator
  u_test_drig -->|"cloud-api → public-api"| u_cloud
  p_root___test_dreport --> u_test_drig
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud,u_device,u_emulator,u_test_drig planned
  class u_test_drig focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [cloud](../../../cloud/README.md) | system | Server side that turns uploaded readings into plant history and alerts | **planned** | [component](../../../cloud/docs/diagrams/component.md) |
| [device](../../../device/README.md) | firmware | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | **planned** | [component](../../../device/docs/diagrams/component.md) |
| [emulator](../../../emulator/README.md) | tool | Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware | **planned** | [context](../../../emulator/docs/diagrams/context.md) |
| [test-rig](../../README.md) | test | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware | **planned** | [context](context.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability | Verified by |
|---|---|---|---|---|---|
| device-under-test | protocol | [contract](../../../docs/references/ble-profile/index.md) | [device/link](../../../device/link/README.md) (planned) (real) | ble-link |  |
| device-under-test | protocol | [contract](../../../docs/references/ble-profile/index.md) | [emulator](../../../emulator/README.md) (planned) (simulated) | ble-link |  |
| scenario-control | http | [contract](../../../docs/references/scenario-control.md) | [emulator](../../../emulator/README.md) (planned) | scenario-control |  |
| cloud-api | http | [contract](../../../docs/references/public-api/index.md) | [cloud/services/gateway](../../../cloud/services/gateway/README.md) (planned) | public-api |  |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need |
|---|---|---|---|---|---|
| test-report | file | [contract](../references/test-report.md) |  | outside the project, as capability `test-report` of the root | |
