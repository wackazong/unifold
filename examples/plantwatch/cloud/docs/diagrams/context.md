<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: cloud

[plantwatch](../../../docs/diagrams/component.md) / **cloud** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

`cloud` inside `plantwatch`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    u_cloud["cloud"]
    u_mobile["mobile"]
    u_protocol["protocol"]
    u_test_drig["test-rig"]
  end
  n_root___push_dservice{{"push-service"}}
  n_root___container_dhost{{"container-host"}}
  u_cloud -->|"reading-format → reading-schema"| u_protocol
  u_mobile -->|"cloud-api → public-api"| u_cloud
  u_cloud -->|"push-service"| n_root___push_dservice
  u_test_drig -->|"cloud-api → public-api"| u_cloud
  u_cloud -->|"container-host"| n_root___container_dhost
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud,u_mobile,u_protocol,u_test_drig planned
  class u_cloud focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [cloud](../../README.md) | system | Server side that turns uploaded readings into plant history and alerts | **planned** | [component](component.md) |
| [mobile](../../../mobile/README.md) | app | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | **planned** | [component](../../../mobile/docs/diagrams/component.md) |
| [protocol](../../../protocol/README.md) | specification | Defines the BLE profile of the sensor stick and the format of a reading | **planned** | [context](../../../protocol/docs/diagrams/context.md) |
| [test-rig](../../../test-rig/README.md) | test | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware | **planned** | [context](../../../test-rig/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Capability | Their contract | Verified by |
|---|---|---|---|---|---|---|
| push-service | http |  | outside the project, as need `push-service` of the root | | | |
| reading-format | specification |  | [protocol](../../../protocol/README.md) (planned) | reading-schema | [contract](../../../protocol/docs/references/reading-schema.md) |  |
| container-host | infrastructure |  | outside the project, as need `container-host` of the root (passed up by name) | | | |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need | Their contract |
|---|---|---|---|---|---|---|
| public-api | http | [contract](../references/public-api/index.md) |  | [mobile/sync](../../../mobile/sync/README.md) (planned) | cloud-api |  |
| public-api | http | [contract](../references/public-api/index.md) |  | [test-rig](../../../test-rig/README.md) (planned) | cloud-api |  |
