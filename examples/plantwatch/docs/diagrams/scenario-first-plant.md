<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: first-plant

**plantwatch** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**An owner starts the app, adds a plant, pairs a sensor stick and binds it to the plant**
Source: tutorial first-plant of mobile
Expect: the sensor stick is bonded and listed as paired, "Monstera" exists on the phone and on the server with the sensor stick attached, and the phone is registered for the notifications of the new owner

A unit is named by its path from `plantwatch`; a capability or need of `plantwatch` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it. An event from an idle lifeline lands on the bar of a busy receiver, or starts one.

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
  participant pcloud__services__gateway as cloud/services/gateway<br/>«service»<br/>Single entry point of the server<br/>side that authenticates callers<br/>and routes requests
  participant pmobile__ble_dclient as mobile/ble-client<br/>«library»<br/>Finds sensor sticks and fetches<br/>their readings over BLE
  participant pdevice__link as device/link<br/>«library»<br/>Implements the BLE profile on<br/>top of the radio
  participant pdevice__hal as device/hal<br/>«adapter»<br/>Hardware abstraction of the<br/>sensor stick board
  participant ppush_dservice as push-service<br/>«http»<br/>Registers phones for an owner<br/>and delivers a notification to<br/>them, for example APNs or FCM
  papp_dui->>pmobile__ui: 1 · owner
  activate pmobile__ui
  pmobile__ui->>pmobile__sync: 2 · start
  deactivate pmobile__ui
  papp_dui->>pmobile__ui: 3 · edit-plant
  activate pmobile__ui
  pmobile__ui->>pmobile__sync: 4 · create-plant
  deactivate pmobile__ui
  papp_dui->>pmobile__ui: 5 · pair
  activate pmobile__ui
  pmobile__ui->>pmobile__ble_dclient: 6 · search
  activate pmobile__ble_dclient
  pdevice__link-)pmobile__ble_dclient: 7 · advertising
  pmobile__ble_dclient-->>pmobile__ui: ↩ 6
  deactivate pmobile__ble_dclient
  pmobile__ui->>pmobile__ble_dclient: 8 · pair
  activate pmobile__ble_dclient
  pmobile__ble_dclient->>pdevice__link: 9 · open-session
  activate pdevice__link
  pdevice__hal-)pdevice__link: 10 · radio-event
  deactivate pdevice__link
  deactivate pmobile__ble_dclient
  pmobile__ui->>pmobile__sync: 11 · change-plant
  activate pmobile__sync
  pmobile__sync->>pcloud__services__gateway: 12 · create-owner
  pmobile__sync->>pcloud__services__gateway: 13 · put-plant
  deactivate pmobile__sync
  pmobile__ui->>ppush_dservice: 14 · register
  deactivate pmobile__ui
  Note over papp_dui,ppush_dservice: wrap: Expect: the sensor stick is bonded and listed as paired, #quot;Monstera#quot; exists on the phone and on the server with the sensor stick attached, and the phone is registered for the notifications of the new owner
```

| # | Caller | Target | Part | Kind | Contract |
|---|---|---|---|---|---|
| 1 | `app-ui` | `mobile/ui` | `owner` | command | [app-ui](../references/app-ui.md) |
| 2 | `mobile/ui` | `mobile/sync` | `start` | command | [index](../../mobile/docs/references/plant-data/index.md) |
| 3 | `app-ui` | `mobile/ui` | `edit-plant` | command | [app-ui](../references/app-ui.md) |
| 4 | `mobile/ui` | `mobile/sync` | `create-plant` | command | [index](../../mobile/docs/references/plant-data/index.md) |
| 5 | `app-ui` | `mobile/ui` | `pair` | command | [app-ui](../references/app-ui.md) |
| 6 | `mobile/ui` | `mobile/ble-client` | `search` | query | [pairing](../../mobile/docs/references/pairing.md) |
| 7 | `mobile/ble-client` | `device/link` | `advertising` | event | [index](../references/ble-profile/index.md) |
| 8 | `mobile/ui` | `mobile/ble-client` | `pair` | command | [pairing](../../mobile/docs/references/pairing.md) |
| 9 | `mobile/ble-client` | `device/link` | `open-session` | command | [index](../references/ble-profile/index.md) |
| 10 | `device/link` | `device/hal` | `radio-event` | event | [radio](../../device/docs/references/radio.md) |
| 11 | `mobile/ui` | `mobile/sync` | `change-plant` | command | [index](../../mobile/docs/references/plant-data/index.md) |
| 12 | `mobile/sync` | `cloud/services/gateway` | `create-owner` | command | [index](../references/public-api/index.md) |
| 13 | `mobile/sync` | `cloud/services/gateway` | `put-plant` | command | [index](../references/public-api/index.md) |
| 14 | `mobile/ui` | `push-service` | `register` | command | [push-service](../references/push-service.md) |
