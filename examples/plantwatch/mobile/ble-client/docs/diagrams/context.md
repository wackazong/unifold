<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: ble-client

[plantwatch](../../../../docs/diagrams/component.md) / [mobile](../../../docs/diagrams/component.md) / **ble-client** · [README](../../README.md)

`ble-client` inside `mobile`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_mobile["mobile"]
    u_mobile__ble_dclient["ble-client (library)"]
    u_mobile__sync["sync (library)"]
    u_mobile__ui["ui (adapter)"]
  end
  n_mobile___sensor_dlink{{"sensor-link"}}
  u_mobile__sync -->|"sensor-readings"| u_mobile__ble_dclient
  u_mobile__ui -->|"pairing"| u_mobile__ble_dclient
  u_mobile__ble_dclient -->|"sensor-link"| n_mobile___sensor_dlink
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_mobile__ble_dclient,u_mobile__sync,u_mobile__ui planned
  class u_mobile__ble_dclient focus
```

| Unit | Kind | Responsibility | Status | Diagram |
|---|---|---|---|---|
| [ble-client](../../README.md) | library | Finds sensor sticks and fetches their readings over BLE | **planned** | [context](context.md) |
| [sync](../../../sync/README.md) | library | Keeps plants, history and alerts on the phone and in step with the server | **planned** | [context](../../../sync/docs/diagrams/context.md) |
| [ui](../../../ui/README.md) | adapter | Screens of the phone app | **planned** | [context](../../../ui/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability |
|---|---|---|---|---|
| sensor-link | protocol | [contract](../../../../docs/references/ble-profile/index.md) | [device/link](../../../../device/link/README.md) (planned) (real) | ble-link |
| sensor-link | protocol | [contract](../../../../docs/references/ble-profile/index.md) | [emulator](../../../../emulator/README.md) (planned) (simulated) | ble-link |

### Who uses what this unit provides

| Capability | Kind | Contract | Used by | As need |
|---|---|---|---|---|
| sensor-readings | library | [contract](../../../docs/references/sensor-readings.md) | [mobile/sync](../../../sync/README.md) (planned) | sensor-readings |
| pairing | library | [contract](../../../docs/references/pairing.md) | [mobile/ui](../../../ui/README.md) (planned) | pairing |
