<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: first-plant

**plantwatch** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**An owner starts the app, adds a plant, pairs a sensor stick and binds it to the plant**
Source: tutorial first-plant of mobile
Expect: the sensor stick is bonded and listed as paired, "Monstera" exists on the phone and on the server with the sensor stick attached, and the phone is registered for the notifications of the new owner

A unit is named by its path from `plantwatch`; a capability or need of `plantwatch` is named bare. Every hop is a call along one connection of the map.

```mermaid
---
config:
  sequence:
    height: 108
---
sequenceDiagram
  participant papp_dui as app-ui<br/>«ui»<br/>Shows the state of each plant<br/>and tells the user when to water<br/>it
  participant pmobile__ui as mobile/ui<br/>«adapter»<br/>Screens of the phone app
  participant pmobile__sync as mobile/sync<br/>«library»<br/>Keeps plants, history and alerts<br/>on the phone and in step with<br/>the server
  participant pmobile__ble_dclient as mobile/ble-client<br/>«library»<br/>Finds sensor sticks and fetches<br/>their readings over BLE
  participant pdevice__link as device/link<br/>«library»<br/>Implements the BLE profile on<br/>top of the radio
  participant pdevice__hal as device/hal<br/>«adapter»<br/>Hardware abstraction of the<br/>sensor stick board
  participant pcloud__services__gateway as cloud/services/gateway<br/>«service»<br/>Single entry point of the server<br/>side that authenticates callers<br/>and routes requests
  participant ppush_dservice as push-service<br/>«http»<br/>Registers phones for an owner<br/>and delivers a notification to<br/>them, for example APNs or FCM
  papp_dui->>pmobile__ui: 1 · owner
  pmobile__ui->>pmobile__sync: 2 · start
  papp_dui->>pmobile__ui: 3 · edit-plant
  pmobile__ui->>pmobile__sync: 4 · create-plant
  papp_dui->>pmobile__ui: 5 · pair
  pmobile__ui->>pmobile__ble_dclient: 6 · search
  pmobile__ble_dclient->>pdevice__link: 7 · advertising
  pmobile__ui->>pmobile__ble_dclient: 8 · pair
  pmobile__ble_dclient->>pdevice__link: 9 · open-session
  pdevice__link->>pdevice__hal: 10 · radio-event
  pmobile__ui->>pmobile__sync: 11 · change-plant
  pmobile__sync->>pcloud__services__gateway: 12 · create-owner
  pmobile__sync->>pcloud__services__gateway: 13 · put-plant
  pmobile__ui->>ppush_dservice: 14 · register
  Note over papp_dui,ppush_dservice: wrap: Expect: the sensor stick is bonded and listed as paired, #quot;Monstera#quot; exists on the phone and on the server with the sensor stick attached, and the phone is registered for the notifications of the new owner
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `app-ui` | `mobile/ui` | `owner` | [app-ui](../references/app-ui.md) |
| 2 | `mobile/ui` | `mobile/sync` | `start` | [index](../../mobile/docs/references/plant-data/index.md) |
| 3 | `app-ui` | `mobile/ui` | `edit-plant` | [app-ui](../references/app-ui.md) |
| 4 | `mobile/ui` | `mobile/sync` | `create-plant` | [index](../../mobile/docs/references/plant-data/index.md) |
| 5 | `app-ui` | `mobile/ui` | `pair` | [app-ui](../references/app-ui.md) |
| 6 | `mobile/ui` | `mobile/ble-client` | `search` | [pairing](../../mobile/docs/references/pairing.md) |
| 7 | `mobile/ble-client` | `device/link` | `advertising` | [index](../references/ble-profile/index.md) |
| 8 | `mobile/ui` | `mobile/ble-client` | `pair` | [pairing](../../mobile/docs/references/pairing.md) |
| 9 | `mobile/ble-client` | `device/link` | `open-session` | [index](../references/ble-profile/index.md) |
| 10 | `device/link` | `device/hal` | `radio-event` | [radio](../../device/docs/references/radio.md) |
| 11 | `mobile/ui` | `mobile/sync` | `change-plant` | [index](../../mobile/docs/references/plant-data/index.md) |
| 12 | `mobile/sync` | `cloud/services/gateway` | `create-owner` | [index](../references/public-api/index.md) |
| 13 | `mobile/sync` | `cloud/services/gateway` | `put-plant` | [index](../references/public-api/index.md) |
| 14 | `mobile/ui` | `push-service` | `register` | [push-service](../references/push-service.md) |
