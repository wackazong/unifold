<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: emulator

[plantwatch](../../../doc/diagrams/component.md) / **emulator** · [README](../../README.md)

`emulator` among its siblings inside `plantwatch`. Only connections that touch `emulator` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

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
  u_mobile -.->|"sensor-link → ble-link (simulated)"| u_emulator
  u_test_drig -.->|"device-under-test → ble-link (simulated)"| u_emulator
  u_test_drig -->|"scenario-control"| u_emulator
  u_emulator -->|"link-profile → ble-profile"| u_protocol
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_root,u_cloud,u_device,u_emulator,u_mobile,u_protocol,u_test_drig planned
  class u_emulator focus
```

| Unit | Kind | Diagram |
|---|---|---|
| [plantwatch](../../../README.md) | system | [component](../../../doc/diagrams/component.md) |
| [cloud](../../../cloud/README.md) | system | [component](../../../cloud/doc/diagrams/component.md) |
| [device](../../../device/README.md) | firmware | [component](../../../device/doc/diagrams/component.md) |
| [emulator](../../README.md) | tool | [context](context.md) |
| [mobile](../../../mobile/README.md) | app | [component](../../../mobile/doc/diagrams/component.md) |
| [protocol](../../../protocol/README.md) | specification | [context](../../../protocol/doc/diagrams/context.md) |
| [test-rig](../../../test-rig/README.md) | test | [context](../../../test-rig/doc/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Port | Their contract |
|---|---|---|---|---|---|
| link-profile | specification |  | [protocol](../../../protocol/README.md) | ble-profile | [contract](../../../protocol/doc/references/ble-profile/index.md) |

### Who uses what this unit provides

| Port | Kind | Used by | As need | Their contract |
|---|---|---|---|---|
| ble-link | protocol | [mobile/ble-client](../../../mobile/ble-client/README.md) | sensor-link |  |
| ble-link | protocol | [test-rig](../../../test-rig/README.md) | device-under-test |  |
| scenario-control | http | [test-rig](../../../test-rig/README.md) | scenario-control |  |
