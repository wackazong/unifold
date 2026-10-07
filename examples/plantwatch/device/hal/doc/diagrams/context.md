<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: hal

[plantwatch](../../../../doc/diagrams/component.md) / [device](../../../doc/diagrams/component.md) / **hal** · [README](../../README.md)

`hal` among its siblings inside `device`. Only connections that touch `hal` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

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
  u_device__hal -->|"soil-probe"| n_device___soil_dprobe
  u_device__hal -->|"ambient-sensor"| n_device___ambient_dsensor
  u_device__sampling -->|"sensor-io, timer"| u_device__hal
  u_device__store -->|"flash"| u_device__hal
  u_device__link -->|"radio"| u_device__hal
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_device,u_device__hal,u_device__link,u_device__sampling,u_device__store planned
  class u_device__hal focus
```

| Unit | Kind | Diagram |
|---|---|---|
| [device](../../../README.md) | firmware | [component](../../../doc/diagrams/component.md) |
| [hal](../../README.md) | library | [context](context.md) |
| [link](../../../link/README.md) | library | [context](../../../link/doc/diagrams/context.md) |
| [sampling](../../../sampling/README.md) | library | [context](../../../sampling/doc/diagrams/context.md) |
| [store](../../../store/README.md) | library | [context](../../../store/doc/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Port | Their contract |
|---|---|---|---|---|---|
| soil-probe | hardware |  | outside the project, as need `soil-probe` of the root | | |
| ambient-sensor | hardware |  | outside the project, as need `ambient-sensor` of the root | | |

### Who uses what this unit provides

| Port | Kind | Used by | As need | Their contract |
|---|---|---|---|---|
| sensor-io | library | [device/sampling](../../../sampling/README.md) | sensor-io | [contract](../../../sampling/doc/references/sensor-io.md) |
| radio | library | [device/link](../../../link/README.md) | radio | [contract](../../../link/doc/references/radio.md) |
| flash | library | [device/store](../../../store/README.md) | flash | [contract](../../../store/doc/references/flash.md) |
| timer | library | [device/sampling](../../../sampling/README.md) | timer | [contract](../../../sampling/doc/references/timer.md) |
