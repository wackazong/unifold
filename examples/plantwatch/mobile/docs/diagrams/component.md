<!-- unifold:generated - do not edit; run `unifold generate` -->
# Component diagram: mobile

[plantwatch](../../../docs/diagrams/component.md) / **mobile** · [README](../../README.md) · [context](context.md)

The units directly inside `mobile` and how they are connected. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_mobile["mobile"]
    u_mobile__ble_dclient["ble-client"]
    u_mobile__sync["sync"]
    u_mobile__ui["ui"]
  end
  n_mobile___sensor_dlink{{"sensor-link"}}
  n_mobile___cloud_dapi{{"cloud-api"}}
  n_mobile___push_dservice{{"push-service"}}
  p_mobile___app_dui(["app-ui"])
  u_mobile__sync -->|"sensor-readings"| u_mobile__ble_dclient
  u_mobile__ui -->|"plant-data"| u_mobile__sync
  u_mobile__ui -->|"pairing"| u_mobile__ble_dclient
  u_mobile__ble_dclient -->|"sensor-link"| n_mobile___sensor_dlink
  u_mobile__sync -->|"cloud-api"| n_mobile___cloud_dapi
  u_mobile__ui -->|"push-service"| n_mobile___push_dservice
  p_mobile___app_dui --> u_mobile__ui
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_mobile__ble_dclient,u_mobile__sync,u_mobile__ui planned
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [ble-client](../../ble-client/README.md) | library | Finds sensor sticks and fetches their readings over BLE | **planned** | [context](../../ble-client/docs/diagrams/context.md) |
| [sync](../../sync/README.md) | library | Keeps plants, history and alerts on the phone and in step with the server | **planned** | [context](../../sync/docs/diagrams/context.md) |
| [ui](../../ui/README.md) | library | Screens of the phone app | **planned** | [context](../../ui/docs/diagrams/context.md) |

### Connections

| Need | Provider | Note |
|---|---|---|
| capability `app-ui` of `mobile` | `ui.app-ui` | implemented by |
| `sync.sensor-readings` | `ble-client.sensor-readings` |  |
| `ui.plant-data` | `sync.plant-data` |  |
| `ui.pairing` | `ble-client.pairing` |  |
| `ble-client.sensor-link` | need `sensor-link` of `mobile` |  |
| `sync.cloud-api` | need `cloud-api` of `mobile` |  |
| `ui.push-service` | need `push-service` of `mobile` |  |
