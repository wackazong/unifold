<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Component diagram: device

[device](../../README.md) · [context](context.md) · [architecture](architecture.md)

The units directly inside `device` and how they are wired. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_device["device"]
    u_device_hal["hal"]
    u_device_link["link"]
    u_device_sampling["sampling"]
    u_device_store["store"]
  end
  p_device_ble_link(["ble-link"])
  n_device_soil_probe{{"soil-probe"}}
  n_device_ambient_sensor{{"ambient-sensor"}}
  n_device_link_profile{{"link-profile"}}
  p_device_ble_link --> u_device_link
  u_device_hal -->|"soil-probe"| n_device_soil_probe
  u_device_hal -->|"ambient-sensor"| n_device_ambient_sensor
  u_device_sampling -->|"sensor-io"| u_device_hal
  u_device_sampling -->|"timer"| u_device_hal
  u_device_store -->|"flash"| u_device_hal
  u_device_store -->|"readings"| u_device_sampling
  u_device_link -->|"radio"| u_device_hal
  u_device_link -->|"reading-log"| u_device_store
  u_device_link -->|"live-readings → readings"| u_device_sampling
  u_device_link -->|"link-profile"| n_device_link_profile
  click u_device_hal href "../../hal/README.md"
  click u_device_link href "../../link/README.md"
  click u_device_sampling href "../../sampling/README.md"
  click u_device_store href "../../store/README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_device,u_device_hal,u_device_link,u_device_sampling,u_device_store planned
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [device](../../README.md) | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | planned | [component](component.md) |
| [hal](../../hal/README.md) | Hardware abstraction of the sensor stick board | planned | [context](../../hal/doc/diagrams/context.md) |
| [link](../../link/README.md) | Implements the BLE profile on top of the radio | planned | [context](../../link/doc/diagrams/context.md) |
| [sampling](../../sampling/README.md) | Takes a calibrated reading at every sampling interval | planned | [context](../../sampling/doc/diagrams/context.md) |
| [store](../../store/README.md) | Keeps readings on the device until they have been delivered | planned | [context](../../store/doc/diagrams/context.md) |
