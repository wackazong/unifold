<!-- unifold:generated - do not edit; run `unifold generate` -->
# Component diagram: device

[plantwatch](../../../docs/diagrams/component.md) / **device** · [README](../../README.md) · [context](context.md)

The units directly inside `device` and how they are connected. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_device["device"]
    u_device__hal["hal"]
    u_device__link["link"]
    u_device__sampling["sampling"]
    u_device__store["store"]
  end
  n_device___ambient_dsensor{{"ambient-sensor"}}
  n_device___soil_dprobe{{"soil-probe"}}
  p_device___ble_dlink(["ble-link"])
  u_device__sampling -->|"sensor-io, timer"| u_device__hal
  u_device__store -->|"flash"| u_device__hal
  u_device__store -->|"readings"| u_device__sampling
  u_device__link -->|"radio"| u_device__hal
  u_device__link -->|"reading-log"| u_device__store
  u_device__link -->|"live-readings → readings"| u_device__sampling
  u_device__hal -->|"ambient-sensor"| n_device___ambient_dsensor
  u_device__hal -->|"soil-probe"| n_device___soil_dprobe
  p_device___ble_dlink --> u_device__link
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_device__hal,u_device__link,u_device__sampling,u_device__store planned
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [hal](../../hal/README.md) | library | Hardware abstraction of the sensor stick board | **planned** | [context](../../hal/docs/diagrams/context.md) |
| [link](../../link/README.md) | library | Implements the BLE profile on top of the radio | **planned** | [context](../../link/docs/diagrams/context.md) |
| [sampling](../../sampling/README.md) | library | Takes a calibrated reading at every sampling interval | **planned** | [context](../../sampling/docs/diagrams/context.md) |
| [store](../../store/README.md) | library | Keeps readings on the sensor stick until they have been delivered | **planned** | [context](../../store/docs/diagrams/context.md) |

### Connections

| Need | Provider | Note |
|---|---|---|
| capability `ble-link` of `device` | `link.ble-link` | implemented by |
| `sampling.sensor-io` | `hal.sensor-io` |  |
| `sampling.timer` | `hal.timer` |  |
| `store.flash` | `hal.flash` |  |
| `store.readings` | `sampling.readings` |  |
| `link.radio` | `hal.radio` |  |
| `link.reading-log` | `store.reading-log` |  |
| `link.live-readings` | `sampling.readings` |  |
| `hal.ambient-sensor` | need `ambient-sensor` of `device` |  |
| `hal.soil-probe` | need `soil-probe` of `device` |  |
