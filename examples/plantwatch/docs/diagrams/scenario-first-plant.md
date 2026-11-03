<!-- unifold:generated - do not edit; run `unifold check --fix` -->
# Scenario: first-plant

**plantwatch** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**An owner starts the app, adds a plant, pairs a sensor stick and binds it to the plant**
Source: tutorial first-plant of mobile
Expect: the sensor stick is bonded and listed as paired, "Monstera" exists on the phone and on the server with the sensor stick attached, and the phone is registered for the notifications of the new owner

A unit is named by its path from `plantwatch`; a capability or need of `plantwatch` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it. An event from an idle lifeline lands on the bar of a busy receiver, or starts one. A step shows its result; a note on a provider's lifeline shows the state of a connection whose contract has states.

```mermaid
---
config:
  sequence:
    height: 108
---
sequenceDiagram
  participant papp_dui as app-ui<br/>Shows the state of each plant<br/>and tells the user when to water<br/>it
  participant pmobile__ui as mobile/ui<br/>«adapter»<br/>Screens of the phone app
  participant pmobile__sync as mobile/sync<br/>«library»<br/>Keeps plants, history and alerts<br/>on the phone and in step with<br/>the server
  participant pcloud__services__gateway as cloud/services/gateway<br/>«service»<br/>Single entry point of the server<br/>side that authenticates callers<br/>and routes requests
  participant pmobile__ble_dclient as mobile/ble-client<br/>«library»<br/>Finds sensor sticks and fetches<br/>their readings over BLE
  participant pdevice__link as device/link<br/>«library»<br/>Implements the BLE profile on<br/>top of the radio
  participant ppush_dservice as push-service<br/>Registers phones for an owner<br/>and delivers a notification to<br/>them, for example APNs or FCM
  papp_dui->>pmobile__ui: 1 · owner() → the app works and asks for no name and no password
  activate pmobile__ui
  Note over pmobile__sync: none
  pmobile__ui->>pmobile__sync: 2 · start() → ok
  activate pmobile__sync
  Note over pmobile__sync: active
  deactivate pmobile__sync
  deactivate pmobile__ui
  papp_dui->>pmobile__ui: 3 · edit-plant(Monstera, a preset) → the plant is added
  activate pmobile__ui
  pmobile__ui->>pmobile__sync: 4 · create-plant(Monstera, the lower limits of the preset, none) → the plant id
  deactivate pmobile__ui
  papp_dui->>pmobile__ui: 5 · pair(Monstera) → the sensor stick is paired and bound to the plant
  activate pmobile__ui
  pmobile__ui->>pmobile__ble_dclient: 6 · search(an observer)
  activate pmobile__ble_dclient
  Note over pdevice__link: disconnected
  pdevice__link-)pmobile__ble_dclient: 7 · advertising(flags 03, has-readings and bonding-open) → ok
  pmobile__ble_dclient-->>pmobile__ui: ↩ 6 · a list with the new sensor stick
  deactivate pmobile__ble_dclient
  pmobile__ui->>pmobile__ble_dclient: 8 · pair(00a1b2c3d4e5f607) → paired
  activate pmobile__ble_dclient
  pmobile__ble_dclient->>pdevice__link: 9 · open-session() → ok
  activate pdevice__link
  Note over pdevice__link: connected
  deactivate pdevice__link
  pmobile__ble_dclient->>pdevice__link: 10 · info()
  activate pdevice__link
  pdevice__link-->>pmobile__ble_dclient: ↩ 10 · 01 00 00 A1 B2 C3 D4 E5 F6 07 07 84 03 40 0B 01 00 00
  deactivate pdevice__link
  deactivate pmobile__ble_dclient
  pmobile__ui->>pmobile__sync: 11 · change-plant(Monstera, sensor id 00a1b2c3d4e5f607) → ok
  activate pmobile__sync
  pmobile__sync->>pcloud__services__gateway: 12 · create-owner() → 201 with owner_id, token and expires_at
  pmobile__sync->>pcloud__services__gateway: 13 · put-plant(Monstera with the sensor stick) → 200 with the plant
  deactivate pmobile__sync
  pmobile__ui->>ppush_dservice: 14 · register(the owner id) → ok
  deactivate pmobile__ui
  Note over papp_dui,ppush_dservice: wrap: Expect: the sensor stick is bonded and listed as paired, #quot;Monstera#quot; exists on the phone and on the server with the sensor stick attached, and the phone is registered for the notifications of the new owner
```

| # | Caller | Target | Call | Kind | Result | State | Contract |
|---|---|---|---|---|---|---|---|
| 1 | `app-ui` | `mobile/ui` | `owner()` | command | the app works and asks for no name and no password |  | [app-ui](../references/app-ui.md) |
| 2 | `mobile/ui` | `mobile/sync` | `start()` | command | ok | active | [plant-data](../../mobile/docs/references/plant-data/index.md) |
| 3 | `app-ui` | `mobile/ui` | `edit-plant(Monstera, a preset)` | command | the plant is added |  | [app-ui](../references/app-ui.md) |
| 4 | `mobile/ui` | `mobile/sync` | `create-plant(Monstera, the lower limits of the preset, none)` | command | the plant id | active | [plant-data](../../mobile/docs/references/plant-data/index.md) |
| 5 | `app-ui` | `mobile/ui` | `pair(Monstera)` | command | the sensor stick is paired and bound to the plant |  | [app-ui](../references/app-ui.md) |
| 6 | `mobile/ui` | `mobile/ble-client` | `search(an observer)` | query | a list with the new sensor stick |  | [pairing](../../mobile/docs/references/pairing.md) |
| 7 | `mobile/ble-client` | `device/link` | `advertising(flags 03, has-readings and bonding-open)` | event | ok | disconnected | [ble-profile](../references/ble-profile/index.md) |
| 8 | `mobile/ui` | `mobile/ble-client` | `pair(00a1b2c3d4e5f607)` | command | paired |  | [pairing](../../mobile/docs/references/pairing.md) |
| 9 | `mobile/ble-client` | `device/link` | `open-session()` | command | ok | connected | [ble-profile](../references/ble-profile/index.md) |
| 10 | `mobile/ble-client` | `device/link` | `info()` | query | 01 00 00 A1 B2 C3 D4 E5 F6 07 07 84 03 40 0B 01 00 00 | connected | [ble-profile](../references/ble-profile/index.md) |
| 11 | `mobile/ui` | `mobile/sync` | `change-plant(Monstera, sensor id 00a1b2c3d4e5f607)` | command | ok | active | [plant-data](../../mobile/docs/references/plant-data/index.md) |
| 12 | `mobile/sync` | `cloud/services/gateway` | `create-owner()` | command | 201 with owner_id, token and expires_at |  | [public-api](../references/public-api/index.md) |
| 13 | `mobile/sync` | `cloud/services/gateway` | `put-plant(Monstera with the sensor stick)` | command | 200 with the plant |  | [public-api](../references/public-api/index.md) |
| 14 | `mobile/ui` | `push-service` | `register(the owner id)` | command | ok |  | [push-service](../references/push-service.md) |
