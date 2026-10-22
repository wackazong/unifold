<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: protocol

[plantwatch](../../../docs/diagrams/component.md) / **protocol** · [README](../../README.md)

`protocol` inside `plantwatch`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    u_cloud["cloud"]
    u_device["device"]
    u_emulator["emulator"]
    u_mobile["mobile"]
    u_protocol["protocol"]
    u_test_drig["test-rig"]
  end
  u_device -->|"link-profile → ble-profile"| u_protocol
  u_emulator -->|"link-profile → ble-profile"| u_protocol
  u_mobile -->|"link-profile → ble-profile, reading-format → reading-schema"| u_protocol
  u_test_drig -->|"link-profile → ble-profile, reading-format → reading-schema"| u_protocol
  u_cloud -->|"reading-format → reading-schema"| u_protocol
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud,u_device,u_emulator,u_mobile,u_protocol,u_test_drig planned
  class u_protocol focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [cloud](../../../cloud/README.md) | system | Server side that turns uploaded readings into plant history and alerts | **planned** | [component](../../../cloud/docs/diagrams/component.md) |
| [device](../../../device/README.md) | firmware | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | **planned** | [component](../../../device/docs/diagrams/component.md) |
| [emulator](../../../emulator/README.md) | tool | Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware | **planned** | [context](../../../emulator/docs/diagrams/context.md) |
| [mobile](../../../mobile/README.md) | app | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | **planned** | [component](../../../mobile/docs/diagrams/component.md) |
| [protocol](../../README.md) | specification | Defines the BLE profile of the sensor stick and the format of a reading | **planned** | [context](context.md) |
| [test-rig](../../../test-rig/README.md) | test | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware | **planned** | [context](../../../test-rig/docs/diagrams/context.md) |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need | Their contract |
|---|---|---|---|---|---|---|
| ble-profile | specification | [contract](../references/ble-profile/index.md) |  | [device/link](../../../device/link/README.md) (planned) | link-profile |  |
| ble-profile | specification | [contract](../references/ble-profile/index.md) |  | [emulator](../../../emulator/README.md) (planned) | link-profile |  |
| ble-profile | specification | [contract](../references/ble-profile/index.md) |  | [mobile/ble-client](../../../mobile/ble-client/README.md) (planned) | link-profile |  |
| ble-profile | specification | [contract](../references/ble-profile/index.md) |  | [test-rig](../../../test-rig/README.md) (planned) | link-profile |  |
| reading-schema | specification | [contract](../references/reading-schema.md) |  | [cloud/services/ingest](../../../cloud/services/ingest/README.md) (planned) | reading-format |  |
| reading-schema | specification | [contract](../references/reading-schema.md) |  | [mobile/sync](../../../mobile/sync/README.md) (planned) | reading-format |  |
| reading-schema | specification | [contract](../references/reading-schema.md) |  | [test-rig](../../../test-rig/README.md) (planned) | reading-format |  |
