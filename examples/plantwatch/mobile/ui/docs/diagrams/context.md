<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: ui

[plantwatch](../../../../docs/diagrams/component.md) / [mobile](../../../docs/diagrams/component.md) / **ui** · [README](../../README.md)

`ui` inside `mobile`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_mobile["mobile"]
    u_mobile__ble_dclient["ble-client"]
    u_mobile__sync["sync"]
    u_mobile__ui["ui"]
  end
  n_mobile___push_dservice{{"push-service"}}
  p_mobile___app_dui(["app-ui"])
  u_mobile__ui -->|"plant-data"| u_mobile__sync
  u_mobile__ui -->|"pairing"| u_mobile__ble_dclient
  u_mobile__ui -->|"push-service"| n_mobile___push_dservice
  p_mobile___app_dui --> u_mobile__ui
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_mobile__ble_dclient,u_mobile__sync,u_mobile__ui planned
  class u_mobile__ui focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [ble-client](../../../ble-client/README.md) | library | Finds sensor sticks and fetches their readings over BLE | **planned** | [context](../../../ble-client/docs/diagrams/context.md) |
| [sync](../../../sync/README.md) | library | Keeps plants, history and alerts on the phone and in step with the server | **planned** | [context](../../../sync/docs/diagrams/context.md) |
| [ui](../../README.md) | library | Screens of the phone app | **planned** | [context](context.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability | Verified by |
|---|---|---|---|---|---|
| plant-data | library | [contract](../../../docs/references/plant-data.md) | [mobile/sync](../../../sync/README.md) (planned) | plant-data |  |
| pairing | library | [contract](../../../docs/references/pairing.md) | [mobile/ble-client](../../../ble-client/README.md) (planned) | pairing |  |
| push-service | http | [contract](../../../../docs/references/push-service.md) | outside the project, as need `push-service` of the root | | |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need |
|---|---|---|---|---|---|
| app-ui | ui | [contract](../../../../docs/references/app-ui.md) |  | outside the project, as capability `app-ui` of the root | |
