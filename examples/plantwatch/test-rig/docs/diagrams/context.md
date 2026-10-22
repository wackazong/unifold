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
    u_protocol["protocol"]
    u_test_drig["test-rig"]
  end
  p_root___test_dreport(["test-report"])
  u_test_drig -->|"link-profile → ble-profile, reading-format → reading-schema"| u_protocol
  u_test_drig -->|"device-under-test → ble-link (real)"| u_device
  u_test_drig -.->|"device-under-test → ble-link (simulated)"| u_emulator
  u_test_drig -->|"scenario-control (optional)"| u_emulator
  u_test_drig -->|"cloud-api → public-api"| u_cloud
  p_root___test_dreport --> u_test_drig
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud,u_device,u_emulator,u_protocol,u_test_drig planned
  class u_test_drig focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [cloud](../../../cloud/README.md) | system | Server side that turns uploaded readings into plant history and alerts | **planned** | [component](../../../cloud/docs/diagrams/component.md) |
| [device](../../../device/README.md) | firmware | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | **planned** | [component](../../../device/docs/diagrams/component.md) |
| [emulator](../../../emulator/README.md) | tool | Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware | **planned** | [context](../../../emulator/docs/diagrams/context.md) |
| [protocol](../../../protocol/README.md) | specification | Defines the BLE profile of the sensor stick and the format of a reading | **planned** | [context](../../../protocol/docs/diagrams/context.md) |
| [test-rig](../../README.md) | test | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware | **planned** | [context](context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Capability | Their contract | Verified by |
|---|---|---|---|---|---|---|
| device-under-test | protocol |  | [device/link](../../../device/link/README.md) (planned) (real) | ble-link |  |  |
| device-under-test | protocol |  | [emulator](../../../emulator/README.md) (planned) (simulated) | ble-link |  |  |
| scenario-control | http |  | [emulator](../../../emulator/README.md) (planned) | scenario-control | [contract](../../../emulator/docs/references/scenario-control-api.md) |  |
| cloud-api | http |  | [cloud/services/gateway](../../../cloud/services/gateway/README.md) (planned) | public-api | [contract](../../../cloud/services/gateway/docs/references/public-api.md) |  |
| link-profile | specification |  | [protocol](../../../protocol/README.md) (planned) | ble-profile | [contract](../../../protocol/docs/references/ble-profile/index.md) |  |
| reading-format | specification |  | [protocol](../../../protocol/README.md) (planned) | reading-schema | [contract](../../../protocol/docs/references/reading-schema.md) |  |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need | Their contract |
|---|---|---|---|---|---|---|
| test-report | file | [contract](../references/test-report.md) |  | outside the project, as capability `test-report` of the root | | |
