<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: ble-client

[ble-client](../../README.md)

`ble-client` among its siblings inside `mobile`. Only connections that touch `ble-client` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_mobile["mobile"]
    u_mobile_ble_client["ble-client"]
    u_mobile_sync["sync"]
    u_mobile_ui["ui"]
  end
  n_mobile_sensor_link{{"sensor-link"}}
  n_mobile_link_profile{{"link-profile"}}
  u_mobile_ble_client -->|"sensor-link"| n_mobile_sensor_link
  u_mobile_ble_client -->|"link-profile"| n_mobile_link_profile
  u_mobile_sync -->|"sensor-readings"| u_mobile_ble_client
  u_mobile_ui -->|"pairing"| u_mobile_ble_client
  click u_mobile_ble_client href "../../README.md"
  click u_mobile_sync href "../../../sync/README.md"
  click u_mobile_ui href "../../../ui/README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_mobile,u_mobile_ble_client,u_mobile_sync,u_mobile_ui planned
  class u_mobile_ble_client focus
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [mobile](../../../README.md) | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | planned | [component](../../../doc/diagrams/component.md) |
| [ble-client](../../README.md) | Finds sensor sticks and fetches their readings over BLE | planned | [context](context.md) |
| [sync](../../../sync/README.md) | Keeps plants, history and alerts on the phone and in step with the server | planned | [context](../../../sync/doc/diagrams/context.md) |
| [ui](../../../ui/README.md) | Screens of the phone app | planned | [context](../../../ui/doc/diagrams/context.md) |
