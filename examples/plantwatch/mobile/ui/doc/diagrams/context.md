<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: ui

[ui](../../README.md)

`ui` among its siblings inside `mobile`. Only connections that touch `ui` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_mobile["mobile"]
    u_mobile_ble_client["ble-client"]
    u_mobile_sync["sync"]
    u_mobile_ui["ui"]
  end
  p_mobile_app_ui(["app-ui"])
  n_mobile_push_service{{"push-service"}}
  p_mobile_app_ui --> u_mobile_ui
  u_mobile_ui -->|"plant-data"| u_mobile_sync
  u_mobile_ui -->|"pairing"| u_mobile_ble_client
  u_mobile_ui -->|"push-service"| n_mobile_push_service
  click u_mobile_ble_client href "../../../ble-client/README.md"
  click u_mobile_sync href "../../../sync/README.md"
  click u_mobile_ui href "../../README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_mobile,u_mobile_ble_client,u_mobile_sync,u_mobile_ui planned
  class u_mobile_ui focus
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [mobile](../../../README.md) | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | planned | [component](../../../doc/diagrams/component.md) |
| [ble-client](../../../ble-client/README.md) | Finds sensor sticks and fetches their readings over BLE | planned | [context](../../../ble-client/doc/diagrams/context.md) |
| [sync](../../../sync/README.md) | Keeps plants, history and alerts on the phone and in step with the server | planned | [context](../../../sync/doc/diagrams/context.md) |
| [ui](../../README.md) | Screens of the phone app | planned | [context](context.md) |
