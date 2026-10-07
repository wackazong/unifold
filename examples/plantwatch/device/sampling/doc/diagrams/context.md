<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: sampling

[sampling](../../README.md)

`sampling` among its siblings inside `device`. Only connections that touch `sampling` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_device["device"]
    u_device_hal["hal"]
    u_device_link["link"]
    u_device_sampling["sampling"]
    u_device_store["store"]
  end
  u_device_sampling -->|"sensor-io"| u_device_hal
  u_device_sampling -->|"timer"| u_device_hal
  u_device_store -->|"readings"| u_device_sampling
  u_device_link -->|"live-readings → readings"| u_device_sampling
  click u_device_hal href "../../../hal/README.md"
  click u_device_link href "../../../link/README.md"
  click u_device_sampling href "../../README.md"
  click u_device_store href "../../../store/README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_device,u_device_hal,u_device_link,u_device_sampling,u_device_store planned
  class u_device_sampling focus
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [device](../../../README.md) | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | planned | [component](../../../doc/diagrams/component.md) |
| [hal](../../../hal/README.md) | Hardware abstraction of the sensor stick board | planned | [context](../../../hal/doc/diagrams/context.md) |
| [link](../../../link/README.md) | Implements the BLE profile on top of the radio | planned | [context](../../../link/doc/diagrams/context.md) |
| [sampling](../../README.md) | Takes a calibrated reading at every sampling interval | planned | [context](context.md) |
| [store](../../../store/README.md) | Keeps readings on the device until they have been delivered | planned | [context](../../../store/doc/diagrams/context.md) |
