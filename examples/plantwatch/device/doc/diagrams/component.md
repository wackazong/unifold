<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Component diagram: device

[plantwatch](../../../doc/diagrams/component.md) / **device** · [README](../../README.md) · [context](context.md) · [architecture](architecture.md)

The units directly inside `device` and how they are wired. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

```mermaid
flowchart LR
  subgraph u_device["device"]
    u_device__hal["hal"]
    u_device__link["link"]
    u_device__sampling["sampling"]
    u_device__store["store"]
  end
  p_device___ble_dlink(["ble-link"])
  n_device___soil_dprobe{{"soil-probe"}}
  n_device___ambient_dsensor{{"ambient-sensor"}}
  n_device___link_dprofile{{"link-profile"}}
  p_device___ble_dlink --> u_device__link
  u_device__hal -->|"soil-probe"| n_device___soil_dprobe
  u_device__hal -->|"ambient-sensor"| n_device___ambient_dsensor
  u_device__sampling -->|"sensor-io, timer"| u_device__hal
  u_device__store -->|"flash"| u_device__hal
  u_device__store -->|"readings"| u_device__sampling
  u_device__link -->|"radio"| u_device__hal
  u_device__link -->|"reading-log"| u_device__store
  u_device__link -->|"live-readings → readings"| u_device__sampling
  u_device__link -->|"link-profile"| n_device___link_dprofile
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_device,u_device__hal,u_device__link,u_device__sampling,u_device__store planned
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [device](../../README.md) | firmware | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | planned | [component](component.md) |
| [hal](../../hal/README.md) | library | Hardware abstraction of the sensor stick board | planned | [context](../../hal/doc/diagrams/context.md) |
| [link](../../link/README.md) | library | Implements the BLE profile on top of the radio | planned | [context](../../link/doc/diagrams/context.md) |
| [sampling](../../sampling/README.md) | library | Takes a calibrated reading at every sampling interval | planned | [context](../../sampling/doc/diagrams/context.md) |
| [store](../../store/README.md) | library | Keeps readings on the sensor stick until they have been delivered | planned | [context](../../store/doc/diagrams/context.md) |
