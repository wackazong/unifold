<!-- unifold:generated - do not edit; run `unifold generate` -->
# Architecture diagram: mobile

[plantwatch](../../../doc/diagrams/component.md) / **mobile** · [README](../../README.md) · [context](context.md) · [component](component.md)

`mobile` next to its siblings in `plantwatch`, opened up 3 level(s) down. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    u_cloud["cloud"]
    u_device["device"]
    u_emulator["emulator"]
    subgraph u_mobile["mobile"]
      u_mobile__ble_dclient["ble-client"]
      u_mobile__sync["sync"]
      u_mobile__ui["ui"]
    end
    u_protocol["protocol"]
    u_test_drig["test-rig"]
  end
  p_root___app_dui(["app-ui"])
  n_root___push_dservice{{"push-service"}}
  p_root___app_dui --> u_mobile__ui
  u_mobile__ble_dclient -->|"sensor-link → ble-link (real)"| u_device
  u_mobile__ble_dclient -.->|"sensor-link → ble-link (simulated)"| u_emulator
  u_mobile__sync -->|"cloud-api → public-api"| u_cloud
  u_mobile__ui -->|"push-service"| n_root___push_dservice
  u_mobile__ble_dclient -->|"link-profile → ble-profile"| u_protocol
  u_mobile__sync -->|"reading-format → reading-schema"| u_protocol
  u_mobile__sync -->|"sensor-readings"| u_mobile__ble_dclient
  u_mobile__ui -->|"plant-data"| u_mobile__sync
  u_mobile__ui -->|"pairing"| u_mobile__ble_dclient
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_root,u_cloud,u_device,u_emulator,u_mobile,u_mobile__ble_dclient,u_mobile__sync,u_mobile__ui,u_protocol,u_test_drig planned
  class u_mobile focus
```

| Unit | Kind | Diagram |
|---|---|---|
| [plantwatch](../../../README.md) | system | [component](../../../doc/diagrams/component.md) |
| [cloud](../../../cloud/README.md) | system | [component](../../../cloud/doc/diagrams/component.md) |
| [device](../../../device/README.md) | firmware | [component](../../../device/doc/diagrams/component.md) |
| [emulator](../../../emulator/README.md) | tool | [context](../../../emulator/doc/diagrams/context.md) |
| [mobile](../../README.md) | app | [component](component.md) |
| [ble-client](../../ble-client/README.md) | library | [context](../../ble-client/doc/diagrams/context.md) |
| [sync](../../sync/README.md) | library | [context](../../sync/doc/diagrams/context.md) |
| [ui](../../ui/README.md) | library | [context](../../ui/doc/diagrams/context.md) |
| [protocol](../../../protocol/README.md) | specification | [context](../../../protocol/doc/diagrams/context.md) |
| [test-rig](../../../test-rig/README.md) | test | [context](../../../test-rig/doc/diagrams/context.md) |
