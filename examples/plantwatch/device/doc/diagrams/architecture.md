<!-- unifold:generated - do not edit; run `unifold generate` -->
# Architecture diagram: device

[plantwatch](../../../doc/diagrams/component.md) / **device** · [README](../../README.md) · [context](context.md) · [component](component.md)

`device` next to its siblings in `plantwatch`, opened up 3 level(s) down. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    u_cloud["cloud"]
    subgraph u_device["device"]
      u_device__hal["hal"]
      u_device__link["link"]
      u_device__sampling["sampling"]
      u_device__store["store"]
    end
    u_emulator["emulator"]
    u_mobile["mobile"]
    u_protocol["protocol"]
    u_test_drig["test-rig"]
  end
  n_root___soil_dprobe{{"soil-probe"}}
  n_root___ambient_dsensor{{"ambient-sensor"}}
  u_device__hal -->|"soil-probe"| n_root___soil_dprobe
  u_device__hal -->|"ambient-sensor"| n_root___ambient_dsensor
  u_mobile -->|"sensor-link → ble-link (real)"| u_device__link
  u_test_drig -->|"device-under-test → ble-link (real)"| u_device__link
  u_device__link -->|"link-profile → ble-profile"| u_protocol
  u_device__sampling -->|"sensor-io, timer"| u_device__hal
  u_device__store -->|"flash"| u_device__hal
  u_device__store -->|"readings"| u_device__sampling
  u_device__link -->|"radio"| u_device__hal
  u_device__link -->|"reading-log"| u_device__store
  u_device__link -->|"live-readings → readings"| u_device__sampling
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_root,u_cloud,u_device,u_device__hal,u_device__link,u_device__sampling,u_device__store,u_emulator,u_mobile,u_protocol,u_test_drig planned
  class u_device focus
```

| Unit | Kind | Diagram |
|---|---|---|
| [plantwatch](../../../README.md) | system | [component](../../../doc/diagrams/component.md) |
| [cloud](../../../cloud/README.md) | system | [component](../../../cloud/doc/diagrams/component.md) |
| [device](../../README.md) | firmware | [component](component.md) |
| [hal](../../hal/README.md) | library | [context](../../hal/doc/diagrams/context.md) |
| [link](../../link/README.md) | library | [context](../../link/doc/diagrams/context.md) |
| [sampling](../../sampling/README.md) | library | [context](../../sampling/doc/diagrams/context.md) |
| [store](../../store/README.md) | library | [context](../../store/doc/diagrams/context.md) |
| [emulator](../../../emulator/README.md) | tool | [context](../../../emulator/doc/diagrams/context.md) |
| [mobile](../../../mobile/README.md) | app | [component](../../../mobile/doc/diagrams/component.md) |
| [protocol](../../../protocol/README.md) | specification | [context](../../../protocol/doc/diagrams/context.md) |
| [test-rig](../../../test-rig/README.md) | test | [context](../../../test-rig/doc/diagrams/context.md) |
