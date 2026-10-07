<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: cloud

[cloud](../../README.md) · [component](component.md) · [architecture](architecture.md)

`cloud` among its siblings inside `plantwatch`. Only connections that touch `cloud` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    u_cloud["cloud"]
    u_device["device"]
    u_emulator["emulator"]
    u_mobile["mobile"]
    u_protocol["protocol"]
    u_test_rig["test-rig"]
  end
  n_root_push_service{{"push-service"}}
  n_root_container_host{{"container-host"}}
  u_mobile -->|"cloud-api → public-api"| u_cloud
  u_cloud -->|"reading-format → reading-schema"| u_protocol
  u_cloud -->|"push-service"| n_root_push_service
  u_cloud -->|"container-host"| n_root_container_host
  u_test_rig -->|"cloud-api → public-api"| u_cloud
  click u_cloud href "../../README.md"
  click u_device href "../../../device/README.md"
  click u_emulator href "../../../emulator/README.md"
  click u_mobile href "../../../mobile/README.md"
  click u_protocol href "../../../protocol/README.md"
  click u_test_rig href "../../../test-rig/README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_root,u_cloud,u_device,u_emulator,u_mobile,u_protocol,u_test_rig planned
  class u_cloud focus
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [plantwatch](../../../README.md) | Tells people when their house plants need water, using a sensor in the pot, a phone app and cloud services | planned | [component](../../../doc/diagrams/component.md) |
| [cloud](../../README.md) | Server side that stores readings, keeps the plant registry and raises alerts | planned | [component](component.md) |
| [device](../../../device/README.md) | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | planned | [component](../../../device/doc/diagrams/component.md) |
| [emulator](../../../emulator/README.md) | Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware | planned | [context](../../../emulator/doc/diagrams/context.md) |
| [mobile](../../../mobile/README.md) | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | planned | [component](../../../mobile/doc/diagrams/component.md) |
| [protocol](../../../protocol/README.md) | Defines the BLE profile of the sensor stick and the format of a reading | planned | [context](../../../protocol/doc/diagrams/context.md) |
| [test-rig](../../../test-rig/README.md) | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware | planned | [context](../../../test-rig/doc/diagrams/context.md) |
