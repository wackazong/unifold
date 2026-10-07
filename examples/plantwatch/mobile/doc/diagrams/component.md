<!-- unifold:generated - do not edit; run `unifold generate` -->
# Component diagram: mobile

[plantwatch](../../../doc/diagrams/component.md) / **mobile** · [README](../../README.md) · [context](context.md) · [architecture](architecture.md)

The units directly inside `mobile` and how they are wired. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

```mermaid
flowchart LR
  subgraph u_mobile["mobile"]
    u_mobile__ble_dclient["ble-client"]
    u_mobile__sync["sync"]
    u_mobile__ui["ui"]
  end
  p_mobile___app_dui(["app-ui"])
  n_mobile___sensor_dlink{{"sensor-link"}}
  n_mobile___cloud_dapi{{"cloud-api"}}
  n_mobile___link_dprofile{{"link-profile"}}
  n_mobile___reading_dformat{{"reading-format"}}
  n_mobile___push_dservice{{"push-service"}}
  p_mobile___app_dui --> u_mobile__ui
  u_mobile__ble_dclient -->|"sensor-link"| n_mobile___sensor_dlink
  u_mobile__ble_dclient -->|"link-profile"| n_mobile___link_dprofile
  u_mobile__sync -->|"sensor-readings"| u_mobile__ble_dclient
  u_mobile__sync -->|"cloud-api"| n_mobile___cloud_dapi
  u_mobile__sync -->|"reading-format"| n_mobile___reading_dformat
  u_mobile__ui -->|"plant-data"| u_mobile__sync
  u_mobile__ui -->|"pairing"| u_mobile__ble_dclient
  u_mobile__ui -->|"push-service"| n_mobile___push_dservice
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_mobile,u_mobile__ble_dclient,u_mobile__sync,u_mobile__ui planned
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [mobile](../../README.md) | app | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | planned | [component](component.md) |
| [ble-client](../../ble-client/README.md) | library | Finds sensor sticks and fetches their readings over BLE | planned | [context](../../ble-client/doc/diagrams/context.md) |
| [sync](../../sync/README.md) | library | Keeps plants, history and alerts on the phone and in step with the server | planned | [context](../../sync/doc/diagrams/context.md) |
| [ui](../../ui/README.md) | library | Screens of the phone app | planned | [context](../../ui/doc/diagrams/context.md) |
