<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: link

[plantwatch](../../../../docs/diagrams/component.md) / [device](../../../docs/diagrams/component.md) / **link** · [README](../../README.md)

`link` inside `device`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_device["device"]
    u_device__hal["hal"]
    u_device__link["link"]
    u_device__sampling["sampling"]
    u_device__store["store"]
  end
  n_device___link_dprofile{{"link-profile"}}
  p_device___ble_dlink(["ble-link"])
  u_device__link -->|"radio"| u_device__hal
  u_device__link -->|"reading-log"| u_device__store
  u_device__link -->|"live-readings → readings"| u_device__sampling
  u_device__link -->|"link-profile"| n_device___link_dprofile
  p_device___ble_dlink --> u_device__link
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_device__hal,u_device__link,u_device__sampling,u_device__store planned
  class u_device__link focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [hal](../../../hal/README.md) | library | Hardware abstraction of the sensor stick board | **planned** | [context](../../../hal/docs/diagrams/context.md) |
| [link](../../README.md) | library | Implements the BLE profile on top of the radio | **planned** | [context](context.md) |
| [sampling](../../../sampling/README.md) | library | Takes a calibrated reading at every sampling interval | **planned** | [context](../../../sampling/docs/diagrams/context.md) |
| [store](../../../store/README.md) | library | Keeps readings on the sensor stick until they have been delivered | **planned** | [context](../../../store/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Capability | Their contract | Verified by |
|---|---|---|---|---|---|---|
| radio | library | [contract](../references/radio.md) | [device/hal](../../../hal/README.md) (planned) | radio | [contract](../../../hal/docs/references/radio.md) |  |
| reading-log | library |  | [device/store](../../../store/README.md) (planned) | reading-log |  |  |
| live-readings | library |  | [device/sampling](../../../sampling/README.md) (planned) | readings |  |  |
| link-profile | specification |  | [protocol](../../../../protocol/README.md) (planned) (passed up by name) | ble-profile | [contract](../../../../protocol/docs/references/ble-profile/index.md) |  |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need | Their contract |
|---|---|---|---|---|---|---|
| ble-link | protocol |  |  | [mobile/ble-client](../../../../mobile/ble-client/README.md) (planned) (real) | sensor-link |  |
| ble-link | protocol |  |  | [test-rig](../../../../test-rig/README.md) (planned) (real) | device-under-test |  |
