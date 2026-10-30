<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: fetch-readings

**plantwatch** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**A paired sensor stick comes into range and the phone fetches, stores and confirms its readings**
Source: BLE profile, fetch stored readings and confirm
Expect: the 96 readings 4711 to 4806 are stored on the phone with a UTC time each and are marked delivered on the sensor stick; the phone disconnects and the readings wait for the next upload

A unit is named by its path from `plantwatch`; a capability or need of `plantwatch` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it.

```mermaid
---
config:
  sequence:
    height: 108
---
sequenceDiagram
  participant pmobile__ble_dclient as mobile/ble-client<br/>«library»<br/>Finds sensor sticks and fetches<br/>their readings over BLE
  participant pdevice__link as device/link<br/>«library»<br/>Implements the BLE profile on<br/>top of the radio
  participant pdevice__hal as device/hal<br/>«adapter»<br/>Hardware abstraction of the<br/>sensor stick board
  participant pdevice__store as device/store<br/>«library»<br/>Keeps readings on the sensor<br/>stick until they have been<br/>delivered
  participant pmobile__sync as mobile/sync<br/>«library»<br/>Keeps plants, history and alerts<br/>on the phone and in step with<br/>the server
  pmobile__ble_dclient->>pdevice__link: 1 · open-session
  activate pdevice__link
  pdevice__link->>pdevice__hal: 2 · answer
  activate pdevice__hal
  deactivate pdevice__hal
  deactivate pdevice__link
  pmobile__ble_dclient->>pdevice__link: 3 · status
  activate pdevice__link
  pdevice__link-->>pmobile__ble_dclient: ↩ 3
  deactivate pdevice__link
  pmobile__ble_dclient->>pdevice__link: 4 · fetch
  activate pdevice__link
  pdevice__link->>pdevice__store: 5 · read
  activate pdevice__store
  pdevice__store-->>pdevice__link: ↩ 5
  deactivate pdevice__store
  pdevice__link->>pdevice__hal: 6 · send
  activate pdevice__hal
  deactivate pdevice__hal
  deactivate pdevice__link
  pmobile__ble_dclient-)pmobile__sync: 7 · batch
  activate pmobile__sync
  pmobile__sync->>pmobile__ble_dclient: 8 · acknowledge
  activate pmobile__ble_dclient
  pmobile__ble_dclient->>pdevice__link: 9 · confirm
  activate pdevice__link
  pdevice__link->>pdevice__store: 10 · mark-delivered
  activate pdevice__store
  deactivate pdevice__store
  deactivate pdevice__link
  deactivate pmobile__ble_dclient
  deactivate pmobile__sync
  Note over pmobile__ble_dclient,pmobile__sync: wrap: Expect: the 96 readings 4711 to 4806 are stored on the phone with a UTC time each and are marked delivered on the sensor stick#59; the phone disconnects and the readings wait for the next upload
```

| # | Caller | Target | Part | Kind | Contract |
|---|---|---|---|---|---|
| 1 | `mobile/ble-client` | `device/link` | `open-session` | command | [index](../references/ble-profile/index.md) |
| 2 | `device/link` | `device/hal` | `answer` | command | [radio](../../device/docs/references/radio.md) |
| 3 | `mobile/ble-client` | `device/link` | `status` | query | [index](../references/ble-profile/index.md) |
| 4 | `mobile/ble-client` | `device/link` | `fetch` | command | [index](../references/ble-profile/index.md) |
| 5 | `device/link` | `device/store` | `read` | query | [reading-log](../../device/docs/references/reading-log.md) |
| 6 | `device/link` | `device/hal` | `send` | command | [radio](../../device/docs/references/radio.md) |
| 7 | `mobile/sync` | `mobile/ble-client` | `batch` | event | [sensor-readings](../../mobile/docs/references/sensor-readings.md) |
| 8 | `mobile/sync` | `mobile/ble-client` | `acknowledge` | command | [sensor-readings](../../mobile/docs/references/sensor-readings.md) |
| 9 | `mobile/ble-client` | `device/link` | `confirm` | command | [index](../references/ble-profile/index.md) |
| 10 | `device/link` | `device/store` | `mark-delivered` | command | [reading-log](../../device/docs/references/reading-log.md) |
