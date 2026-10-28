<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: link

[plantwatch](../../../../docs/diagrams/component.md) / [device](../../../docs/diagrams/component.md) / **link** · [README](../../README.md)

`link` inside `device`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_device["device"]
    u_device__hal["hal (adapter)"]
    u_device__link["link (library)"]
    u_device__sampling["sampling (library)"]
    u_device__store["store (library)"]
  end
  p_device___ble_dlink(["ble-link"])
  u_device__link -->|"radio"| u_device__hal
  u_device__link -->|"reading-log"| u_device__store
  u_device__link -->|"live-readings → readings"| u_device__sampling
  p_device___ble_dlink --> u_device__link
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_device__hal,u_device__link,u_device__sampling,u_device__store planned
  class u_device__link focus
```

| Unit | Kind | Responsibility | Status | Diagram |
|---|---|---|---|---|
| [hal](../../../hal/README.md) | adapter | Hardware abstraction of the sensor stick board | **planned** | [context](../../../hal/docs/diagrams/context.md) |
| [link](../../README.md) | library | Implements the BLE profile on top of the radio | **planned** | [context](context.md) |
| [sampling](../../../sampling/README.md) | library | Takes a calibrated reading at every sampling interval | **planned** | [context](../../../sampling/docs/diagrams/context.md) |
| [store](../../../store/README.md) | library | Keeps readings on the sensor stick until they have been delivered | **planned** | [context](../../../store/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability |
|---|---|---|---|---|
| radio | library | [contract](../../../docs/references/radio.md) | [device/hal](../../../hal/README.md) (planned) | radio |
| reading-log | library | [contract](../../../docs/references/reading-log.md) | [device/store](../../../store/README.md) (planned) | reading-log |
| live-readings | library | [contract](../../../docs/references/readings.md) | [device/sampling](../../../sampling/README.md) (planned) | readings |

### Who uses what this unit provides

| Capability | Kind | Contract | Used by | As need |
|---|---|---|---|---|
| ble-link | protocol | [contract](../../../../docs/references/ble-profile/index.md) | [mobile/ble-client](../../../../mobile/ble-client/README.md) (planned) (real) | sensor-link |
| ble-link | protocol | [contract](../../../../docs/references/ble-profile/index.md) | [test-rig](../../../../test-rig/README.md) (planned) (real) | device-under-test |
