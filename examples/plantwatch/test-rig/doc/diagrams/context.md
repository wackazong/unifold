<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: test-rig

[plantwatch](../../../doc/diagrams/component.md) / **test-rig** · [README](../../README.md)

`test-rig` among its siblings inside `plantwatch`. Only connections that touch `test-rig` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

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
  p_root___test_dreport(["test-report"])
  p_root___test_dreport --> u_test_drig
  u_test_drig -->|"device-under-test → ble-link (real)"| u_device
  u_test_drig -.->|"device-under-test → ble-link (simulated)"| u_emulator
  u_test_drig -->|"scenario-control"| u_emulator
  u_test_drig -->|"cloud-api → public-api"| u_cloud
  u_test_drig -->|"link-profile → ble-profile, reading-format → reading-schema"| u_protocol
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_root,u_cloud,u_device,u_emulator,u_mobile,u_protocol,u_test_drig planned
  class u_test_drig focus
```

| Unit | Kind | Diagram |
|---|---|---|
| [plantwatch](../../../README.md) | system | [component](../../../doc/diagrams/component.md) |
| [cloud](../../../cloud/README.md) | system | [component](../../../cloud/doc/diagrams/component.md) |
| [device](../../../device/README.md) | firmware | [component](../../../device/doc/diagrams/component.md) |
| [emulator](../../../emulator/README.md) | tool | [context](../../../emulator/doc/diagrams/context.md) |
| [mobile](../../../mobile/README.md) | app | [component](../../../mobile/doc/diagrams/component.md) |
| [protocol](../../../protocol/README.md) | specification | [context](../../../protocol/doc/diagrams/context.md) |
| [test-rig](../../README.md) | test | [context](context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Port | Their contract |
|---|---|---|---|---|---|
| device-under-test | protocol |  | [device/link](../../../device/link/README.md) (real) | ble-link |  |
| device-under-test | protocol |  | [emulator](../../../emulator/README.md) (simulated) | ble-link |  |
| scenario-control | http |  | [emulator](../../../emulator/README.md) | scenario-control | [contract](../../../emulator/doc/references/scenario-control-api.md) |
| cloud-api | http |  | [cloud/services/gateway](../../../cloud/services/gateway/README.md) | public-api | [contract](../../../cloud/services/gateway/doc/references/public-api.md) |
| link-profile | specification |  | [protocol](../../../protocol/README.md) | ble-profile | [contract](../../../protocol/doc/references/ble-profile/index.md) |
| reading-format | specification |  | [protocol](../../../protocol/README.md) | reading-schema | [contract](../../../protocol/doc/references/reading-schema.md) |

### Who uses what this unit provides

| Port | Kind | Used by | As need | Their contract |
|---|---|---|---|---|
| test-report | file | outside the project, as port `test-report` of the root | | |
