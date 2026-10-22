<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: sync

[plantwatch](../../../../docs/diagrams/component.md) / [mobile](../../../docs/diagrams/component.md) / **sync** · [README](../../README.md)

`sync` inside `mobile`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_mobile["mobile"]
    u_mobile__ble_dclient["ble-client"]
    u_mobile__sync["sync"]
    u_mobile__ui["ui"]
  end
  n_mobile___cloud_dapi{{"cloud-api"}}
  u_mobile__sync -->|"sensor-readings"| u_mobile__ble_dclient
  u_mobile__ui -->|"plant-data"| u_mobile__sync
  u_mobile__sync -->|"cloud-api"| n_mobile___cloud_dapi
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_mobile__ble_dclient,u_mobile__sync,u_mobile__ui planned
  class u_mobile__sync focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [ble-client](../../../ble-client/README.md) | library | Finds sensor sticks and fetches their readings over BLE | **planned** | [context](../../../ble-client/docs/diagrams/context.md) |
| [sync](../../README.md) | library | Keeps plants, history and alerts on the phone and in step with the server | **planned** | [context](context.md) |
| [ui](../../../ui/README.md) | library | Screens of the phone app | **planned** | [context](../../../ui/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability | Verified by |
|---|---|---|---|---|---|
| sensor-readings | library | [contract](../../../docs/references/sensor-readings.md) | [mobile/ble-client](../../../ble-client/README.md) (planned) | sensor-readings |  |
| cloud-api | http | [contract](../../../../docs/references/public-api/index.md) | [cloud/services/gateway](../../../../cloud/services/gateway/README.md) (planned) (passed up by name) | public-api |  |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need |
|---|---|---|---|---|---|
| plant-data | library | [contract](../../../docs/references/plant-data.md) |  | [mobile/ui](../../../ui/README.md) (planned) | plant-data |
