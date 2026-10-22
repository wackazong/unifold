<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: ble-client

[plantwatch](../../../../docs/diagrams/component.md) / [mobile](../../../docs/diagrams/component.md) / **ble-client** · [README](../../README.md)

`ble-client` inside `mobile`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_mobile["mobile"]
    u_mobile__ble_dclient["ble-client"]
    u_mobile__sync["sync"]
    u_mobile__ui["ui"]
  end
  n_mobile___sensor_dlink{{"sensor-link"}}
  n_mobile___link_dprofile{{"link-profile"}}
  u_mobile__sync -->|"sensor-readings"| u_mobile__ble_dclient
  u_mobile__ui -->|"pairing"| u_mobile__ble_dclient
  u_mobile__ble_dclient -->|"sensor-link"| n_mobile___sensor_dlink
  u_mobile__ble_dclient -->|"link-profile"| n_mobile___link_dprofile
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_mobile__ble_dclient,u_mobile__sync,u_mobile__ui planned
  class u_mobile__ble_dclient focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [ble-client](../../README.md) | library | Finds sensor sticks and fetches their readings over BLE | **planned** | [context](context.md) |
| [sync](../../../sync/README.md) | library | Keeps plants, history and alerts on the phone and in step with the server | **planned** | [context](../../../sync/docs/diagrams/context.md) |
| [ui](../../../ui/README.md) | library | Screens of the phone app | **planned** | [context](../../../ui/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Capability | Their contract | Verified by |
|---|---|---|---|---|---|---|
| sensor-link | protocol |  | [device/link](../../../../device/link/README.md) (planned) (real; passed up by name) | ble-link |  |  |
| sensor-link | protocol |  | [emulator](../../../../emulator/README.md) (planned) (simulated; passed up by name) | ble-link |  |  |
| link-profile | specification |  | [protocol](../../../../protocol/README.md) (planned) (passed up by name) | ble-profile | [contract](../../../../protocol/docs/references/ble-profile/index.md) |  |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need | Their contract |
|---|---|---|---|---|---|---|
| sensor-readings | library | [contract](../references/sensor-readings.md) |  | [mobile/sync](../../../sync/README.md) (planned) | sensor-readings |  |
| pairing | library | [contract](../references/pairing.md) |  | [mobile/ui](../../../ui/README.md) (planned) | pairing |  |
