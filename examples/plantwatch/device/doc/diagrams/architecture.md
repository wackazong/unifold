<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Architecture diagram: device

[device](../../README.md) · [context](context.md) · [component](component.md)

`device` next to its siblings in `plantwatch`, opened up to 3 level(s) down. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    u_cloud["cloud"]
    subgraph u_device["device"]
      u_device_hal["hal"]
      u_device_link["link"]
      u_device_sampling["sampling"]
      u_device_store["store"]
    end
    u_emulator["emulator"]
    u_mobile["mobile"]
    u_protocol["protocol"]
    u_test_rig["test-rig"]
  end
  n_root_soil_probe{{"soil-probe"}}
  n_root_ambient_sensor{{"ambient-sensor"}}
  u_device_hal -->|"soil-probe"| n_root_soil_probe
  u_device_hal -->|"ambient-sensor"| n_root_ambient_sensor
  u_device_link -->|"link-profile → ble-profile"| u_protocol
  u_mobile -.->|"sensor-link → ble-link"| u_device_link
  u_test_rig -.->|"device-under-test → ble-link"| u_device_link
  u_device_sampling -->|"sensor-io"| u_device_hal
  u_device_sampling -->|"timer"| u_device_hal
  u_device_store -->|"flash"| u_device_hal
  u_device_store -->|"readings"| u_device_sampling
  u_device_link -->|"radio"| u_device_hal
  u_device_link -->|"reading-log"| u_device_store
  u_device_link -->|"live-readings → readings"| u_device_sampling
  click u_cloud href "../../../cloud/README.md"
  click u_device_hal href "../../hal/README.md"
  click u_device_link href "../../link/README.md"
  click u_device_sampling href "../../sampling/README.md"
  click u_device_store href "../../store/README.md"
  click u_emulator href "../../../emulator/README.md"
  click u_mobile href "../../../mobile/README.md"
  click u_protocol href "../../../protocol/README.md"
  click u_test_rig href "../../../test-rig/README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_root,u_cloud,u_device,u_device_hal,u_device_link,u_device_sampling,u_device_store,u_emulator,u_mobile,u_protocol,u_test_rig planned
  class u_device focus
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [plantwatch](../../../README.md) | Tells people when their house plants need water, using a sensor in the pot, a phone app and cloud services | planned | [component](../../../doc/diagrams/component.md) |
| [cloud](../../../cloud/README.md) | Server side that stores readings, keeps the plant registry and raises alerts | planned | [component](../../../cloud/doc/diagrams/component.md) |
| [device](../../README.md) | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | planned | [component](component.md) |
| [hal](../../hal/README.md) | Hardware abstraction of the sensor stick board | planned | [context](../../hal/doc/diagrams/context.md) |
| [link](../../link/README.md) | Implements the BLE profile on top of the radio | planned | [context](../../link/doc/diagrams/context.md) |
| [sampling](../../sampling/README.md) | Takes a calibrated reading at every sampling interval | planned | [context](../../sampling/doc/diagrams/context.md) |
| [store](../../store/README.md) | Keeps readings on the device until they have been delivered | planned | [context](../../store/doc/diagrams/context.md) |
| [emulator](../../../emulator/README.md) | Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware | planned | [context](../../../emulator/doc/diagrams/context.md) |
| [mobile](../../../mobile/README.md) | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | planned | [component](../../../mobile/doc/diagrams/component.md) |
| [protocol](../../../protocol/README.md) | Defines the BLE profile of the sensor stick and the format of a reading | planned | [context](../../../protocol/doc/diagrams/context.md) |
| [test-rig](../../../test-rig/README.md) | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware | planned | [context](../../../test-rig/doc/diagrams/context.md) |
