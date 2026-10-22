<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: store

[plantwatch](../../../../docs/diagrams/component.md) / [device](../../../docs/diagrams/component.md) / **store** · [README](../../README.md)

`store` inside `device`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_device["device"]
    u_device__hal["hal"]
    u_device__link["link"]
    u_device__sampling["sampling"]
    u_device__store["store"]
  end
  u_device__store -->|"flash"| u_device__hal
  u_device__store -->|"readings"| u_device__sampling
  u_device__link -->|"reading-log"| u_device__store
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_device__hal,u_device__link,u_device__sampling,u_device__store planned
  class u_device__store focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [hal](../../../hal/README.md) | library | Hardware abstraction of the sensor stick board | **planned** | [context](../../../hal/docs/diagrams/context.md) |
| [link](../../../link/README.md) | library | Implements the BLE profile on top of the radio | **planned** | [context](../../../link/docs/diagrams/context.md) |
| [sampling](../../../sampling/README.md) | library | Takes a calibrated reading at every sampling interval | **planned** | [context](../../../sampling/docs/diagrams/context.md) |
| [store](../../README.md) | library | Keeps readings on the sensor stick until they have been delivered | **planned** | [context](context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Capability | Their contract | Verified by |
|---|---|---|---|---|---|---|
| flash | library | [contract](../references/flash.md) | [device/hal](../../../hal/README.md) (planned) | flash | [contract](../../../hal/docs/references/flash.md) |  |
| readings | library |  | [device/sampling](../../../sampling/README.md) (planned) | readings |  |  |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need | Their contract |
|---|---|---|---|---|---|---|
| reading-log | library |  |  | [device/link](../../../link/README.md) (planned) | reading-log |  |
