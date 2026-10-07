<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: mobile

[plantwatch](../../../doc/diagrams/component.md) / **mobile** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

`mobile` among its siblings inside `plantwatch`. Only connections that touch `mobile` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

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
  p_root___app_dui(["app-ui"])
  n_root___push_dservice{{"push-service"}}
  p_root___app_dui --> u_mobile
  u_mobile -->|"sensor-link → ble-link (real)"| u_device
  u_mobile -.->|"sensor-link → ble-link (simulated)"| u_emulator
  u_mobile -->|"cloud-api → public-api"| u_cloud
  u_mobile -->|"push-service"| n_root___push_dservice
  u_mobile -->|"link-profile → ble-profile, reading-format → reading-schema"| u_protocol
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_root,u_cloud,u_device,u_emulator,u_mobile,u_protocol,u_test_drig planned
  class u_mobile focus
```

| Unit | Kind | Diagram |
|---|---|---|
| [plantwatch](../../../README.md) | system | [component](../../../doc/diagrams/component.md) |
| [cloud](../../../cloud/README.md) | system | [component](../../../cloud/doc/diagrams/component.md) |
| [device](../../../device/README.md) | firmware | [component](../../../device/doc/diagrams/component.md) |
| [emulator](../../../emulator/README.md) | tool | [context](../../../emulator/doc/diagrams/context.md) |
| [mobile](../../README.md) | app | [component](component.md) |
| [protocol](../../../protocol/README.md) | specification | [context](../../../protocol/doc/diagrams/context.md) |
| [test-rig](../../../test-rig/README.md) | test | [context](../../../test-rig/doc/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Port | Their contract |
|---|---|---|---|---|---|
| sensor-link | protocol |  | [device/link](../../../device/link/README.md) (real) | ble-link |  |
| sensor-link | protocol |  | [emulator](../../../emulator/README.md) (simulated) | ble-link |  |
| cloud-api | http |  | [cloud/services/gateway](../../../cloud/services/gateway/README.md) | public-api | [contract](../../../cloud/services/gateway/doc/references/public-api.md) |
| link-profile | specification |  | [protocol](../../../protocol/README.md) | ble-profile | [contract](../../../protocol/doc/references/ble-profile/index.md) |
| reading-format | specification |  | [protocol](../../../protocol/README.md) | reading-schema | [contract](../../../protocol/doc/references/reading-schema.md) |
| push-service | http |  | outside the project, as need `push-service` of the root | | |

### Who uses what this unit provides

| Port | Kind | Used by | As need | Their contract |
|---|---|---|---|---|
| app-ui | ui | outside the project, as port `app-ui` of the root | | |
