<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: emulator

[plantwatch](../../../docs/diagrams/component.md) / **emulator** · [README](../../README.md)

`emulator` inside `plantwatch`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    u_emulator["emulator"]
    u_mobile["mobile"]
    u_protocol["protocol"]
    u_test_drig["test-rig"]
  end
  u_emulator -->|"link-profile → ble-profile"| u_protocol
  u_mobile -.->|"sensor-link → ble-link (simulated)"| u_emulator
  u_test_drig -.->|"device-under-test → ble-link (simulated)"| u_emulator
  u_test_drig -->|"scenario-control (optional)"| u_emulator
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_emulator,u_mobile,u_protocol,u_test_drig planned
  class u_emulator focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [emulator](../../README.md) | tool | Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware | **planned** | [context](context.md) |
| [mobile](../../../mobile/README.md) | app | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | **planned** | [component](../../../mobile/docs/diagrams/component.md) |
| [protocol](../../../protocol/README.md) | specification | Defines the BLE profile of the sensor stick and the format of a reading | **planned** | [context](../../../protocol/docs/diagrams/context.md) |
| [test-rig](../../../test-rig/README.md) | test | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware | **planned** | [context](../../../test-rig/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Capability | Their contract | Verified by |
|---|---|---|---|---|---|---|
| link-profile | specification |  | [protocol](../../../protocol/README.md) (planned) | ble-profile | [contract](../../../protocol/docs/references/ble-profile/index.md) |  |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need | Their contract |
|---|---|---|---|---|---|---|
| ble-link | protocol |  |  | [mobile/ble-client](../../../mobile/ble-client/README.md) (planned) (simulated) | sensor-link |  |
| ble-link | protocol |  |  | [test-rig](../../../test-rig/README.md) (planned) (simulated) | device-under-test |  |
| scenario-control | http | [contract](../references/scenario-control-api.md) |  | [test-rig](../../../test-rig/README.md) (planned) | scenario-control |  |
