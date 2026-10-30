<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: fetch-readings

**plantwatch** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**A paired sensor stick comes into range and the phone fetches, stores and confirms its readings**
Source: BLE profile, fetch stored readings and confirm
Expect: the 96 readings 4711 to 4806 are stored on the phone with a UTC time each and are marked delivered on the sensor stick; the phone disconnects and the readings wait for the next upload

A unit is named by its path from `plantwatch`; a capability or need of `plantwatch` is named bare. Every hop is a call along one connection of the map.

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
  pdevice__link->>pdevice__hal: 2 · answer
  pmobile__ble_dclient->>pdevice__link: 3 · status
  pmobile__ble_dclient->>pdevice__link: 4 · fetch
  pdevice__link->>pdevice__store: 5 · read
  pdevice__link->>pdevice__hal: 6 · send
  pmobile__sync->>pmobile__ble_dclient: 7 · batch
  pmobile__sync->>pmobile__ble_dclient: 8 · acknowledge
  pmobile__ble_dclient->>pdevice__link: 9 · confirm
  pdevice__link->>pdevice__store: 10 · mark-delivered
  Note over pmobile__ble_dclient,pmobile__sync: wrap: Expect: the 96 readings 4711 to 4806 are stored on the phone with a UTC time each and are marked delivered on the sensor stick#59; the phone disconnects and the readings wait for the next upload
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `mobile/ble-client` | `device/link` | `open-session` | [index](../references/ble-profile/index.md) |
| 2 | `device/link` | `device/hal` | `answer` | [radio](../../device/docs/references/radio.md) |
| 3 | `mobile/ble-client` | `device/link` | `status` | [index](../references/ble-profile/index.md) |
| 4 | `mobile/ble-client` | `device/link` | `fetch` | [index](../references/ble-profile/index.md) |
| 5 | `device/link` | `device/store` | `read` | [reading-log](../../device/docs/references/reading-log.md) |
| 6 | `device/link` | `device/hal` | `send` | [radio](../../device/docs/references/radio.md) |
| 7 | `mobile/sync` | `mobile/ble-client` | `batch` | [sensor-readings](../../mobile/docs/references/sensor-readings.md) |
| 8 | `mobile/sync` | `mobile/ble-client` | `acknowledge` | [sensor-readings](../../mobile/docs/references/sensor-readings.md) |
| 9 | `mobile/ble-client` | `device/link` | `confirm` | [index](../references/ble-profile/index.md) |
| 10 | `device/link` | `device/store` | `mark-delivered` | [reading-log](../../device/docs/references/reading-log.md) |
