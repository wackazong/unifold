<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: ui

[plantwatch](../../../../doc/diagrams/component.md) / [mobile](../../../doc/diagrams/component.md) / **ui** · [README](../../README.md)

`ui` among its siblings inside `mobile`. Only connections that touch `ui` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

```mermaid
flowchart LR
  subgraph u_mobile["mobile"]
    u_mobile__ble_dclient["ble-client"]
    u_mobile__sync["sync"]
    u_mobile__ui["ui"]
  end
  p_mobile___app_dui(["app-ui"])
  n_mobile___push_dservice{{"push-service"}}
  p_mobile___app_dui --> u_mobile__ui
  u_mobile__ui -->|"plant-data"| u_mobile__sync
  u_mobile__ui -->|"pairing"| u_mobile__ble_dclient
  u_mobile__ui -->|"push-service"| n_mobile___push_dservice
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_mobile,u_mobile__ble_dclient,u_mobile__sync,u_mobile__ui planned
  class u_mobile__ui focus
```

| Unit | Kind | Diagram |
|---|---|---|
| [mobile](../../../README.md) | app | [component](../../../doc/diagrams/component.md) |
| [ble-client](../../../ble-client/README.md) | library | [context](../../../ble-client/doc/diagrams/context.md) |
| [sync](../../../sync/README.md) | library | [context](../../../sync/doc/diagrams/context.md) |
| [ui](../../README.md) | library | [context](context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Port | Their contract |
|---|---|---|---|---|---|
| plant-data | library | [contract](../references/plant-data.md) | [mobile/sync](../../../sync/README.md) | plant-data | [contract](../../../sync/doc/references/plant-data.md) |
| pairing | library |  | [mobile/ble-client](../../../ble-client/README.md) | pairing | [contract](../../../ble-client/doc/references/pairing.md) |
| push-service | http |  | outside the project, as need `push-service` of the root | | |

### Who uses what this unit provides

| Port | Kind | Used by | As need | Their contract |
|---|---|---|---|---|
| app-ui | ui | outside the project, as port `app-ui` of the root | | |
