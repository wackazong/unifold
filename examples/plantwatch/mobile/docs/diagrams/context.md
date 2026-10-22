<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: mobile

[plantwatch](../../../docs/diagrams/component.md) / **mobile** · [README](../../README.md) · [component](component.md)

`mobile` inside `plantwatch`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    u_cloud["cloud"]
    u_device["device"]
    u_emulator["emulator"]
    u_mobile["mobile"]
    u_protocol["protocol"]
  end
  n_root___push_dservice{{"push-service"}}
  p_root___app_dui(["app-ui"])
  u_mobile -->|"link-profile → ble-profile, reading-format → reading-schema"| u_protocol
  u_mobile -->|"sensor-link → ble-link (real)"| u_device
  u_mobile -.->|"sensor-link → ble-link (simulated)"| u_emulator
  u_mobile -->|"cloud-api → public-api"| u_cloud
  u_mobile -->|"push-service"| n_root___push_dservice
  p_root___app_dui --> u_mobile
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud,u_device,u_emulator,u_mobile,u_protocol planned
  class u_mobile focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [cloud](../../../cloud/README.md) | system | Server side that turns uploaded readings into plant history and alerts | **planned** | [component](../../../cloud/docs/diagrams/component.md) |
| [device](../../../device/README.md) | firmware | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | **planned** | [component](../../../device/docs/diagrams/component.md) |
| [emulator](../../../emulator/README.md) | tool | Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware | **planned** | [context](../../../emulator/docs/diagrams/context.md) |
| [mobile](../../README.md) | app | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | **planned** | [component](component.md) |
| [protocol](../../../protocol/README.md) | specification | Defines the BLE profile of the sensor stick and the format of a reading | **planned** | [context](../../../protocol/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Capability | Their contract | Verified by |
|---|---|---|---|---|---|---|
| sensor-link | protocol |  | [device/link](../../../device/link/README.md) (planned) (real) | ble-link |  |  |
| sensor-link | protocol |  | [emulator](../../../emulator/README.md) (planned) (simulated) | ble-link |  |  |
| cloud-api | http |  | [cloud/services/gateway](../../../cloud/services/gateway/README.md) (planned) | public-api | [contract](../../../cloud/services/gateway/docs/references/public-api.md) |  |
| link-profile | specification |  | [protocol](../../../protocol/README.md) (planned) | ble-profile | [contract](../../../protocol/docs/references/ble-profile/index.md) |  |
| reading-format | specification |  | [protocol](../../../protocol/README.md) (planned) | reading-schema | [contract](../../../protocol/docs/references/reading-schema.md) |  |
| push-service | http |  | outside the project, as need `push-service` of the root | | | |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need | Their contract |
|---|---|---|---|---|---|---|
| app-ui | ui | [contract](../references/app-ui.md) |  | outside the project, as capability `app-ui` of the root | | |
