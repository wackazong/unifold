<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: hal

[plantwatch](../../../../docs/diagrams/component.md) / [device](../../../docs/diagrams/component.md) / **hal** · [README](../../README.md)

`hal` inside `device`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_device["device"]
    u_device__hal["hal"]
    u_device__link["link"]
    u_device__sampling["sampling"]
    u_device__store["store"]
  end
  n_device___soil_dprobe{{"soil-probe"}}
  n_device___ambient_dsensor{{"ambient-sensor"}}
  u_device__sampling -->|"sensor-io, timer"| u_device__hal
  u_device__store -->|"flash"| u_device__hal
  u_device__link -->|"radio"| u_device__hal
  u_device__hal -->|"soil-probe"| n_device___soil_dprobe
  u_device__hal -->|"ambient-sensor"| n_device___ambient_dsensor
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_device__hal,u_device__link,u_device__sampling,u_device__store planned
  class u_device__hal focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [hal](../../README.md) | library | Hardware abstraction of the sensor stick board | **planned** | [context](context.md) |
| [link](../../../link/README.md) | library | Implements the BLE profile on top of the radio | **planned** | [context](../../../link/docs/diagrams/context.md) |
| [sampling](../../../sampling/README.md) | library | Takes a calibrated reading at every sampling interval | **planned** | [context](../../../sampling/docs/diagrams/context.md) |
| [store](../../../store/README.md) | library | Keeps readings on the sensor stick until they have been delivered | **planned** | [context](../../../store/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability | Verified by |
|---|---|---|---|---|---|
| soil-probe | hardware | [contract](../../../../docs/references/soil-probe.md) | outside the project, as need `soil-probe` of the root (passed up by name) | | |
| ambient-sensor | hardware | [contract](../../../../docs/references/ambient-sensor.md) | outside the project, as need `ambient-sensor` of the root (passed up by name) | | |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need |
|---|---|---|---|---|---|
| sensor-io | library | [contract](../../../docs/references/sensor-io.md) |  | [device/sampling](../../../sampling/README.md) (planned) | sensor-io |
| radio | library | [contract](../../../docs/references/radio.md) |  | [device/link](../../../link/README.md) (planned) | radio |
| flash | library | [contract](../../../docs/references/flash.md) |  | [device/store](../../../store/README.md) (planned) | flash |
| timer | library | [contract](../../../docs/references/timer.md) |  | [device/sampling](../../../sampling/README.md) (planned) | timer |
