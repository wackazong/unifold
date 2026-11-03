<!-- unifold:generated - do not edit; run `unifold check --fix` -->
# Scenario: upload-and-alert

**plantwatch** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**The phone uploads readings, the server opens an alert and the owner is notified once**
Source: requirements of plantwatch, the public API, consistency
Given: `mobile/sync.plant-data` is active
Expect: within 1 minute after the upload response the alert is open on the server and its notification is handed to the push service; the phone shows one notification, a tap opens "Monstera", and the plant is first in the list with "needs water"

A unit is named by its path from `plantwatch`; a capability or need of `plantwatch` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it. An event from an idle lifeline lands on the bar of a busy receiver, or starts one. A step shows its result; a note on a provider's lifeline shows the state of a connection whose contract has states.

```mermaid
---
config:
  sequence:
    height: 108
---
sequenceDiagram
  participant pmobile__sync as mobile/sync<br/>«library»<br/>Keeps plants, history and alerts<br/>on the phone and in step with<br/>the server
  participant pcloud__services__gateway as cloud/services/gateway<br/>«service»<br/>Single entry point of the server<br/>side that authenticates callers<br/>and routes requests
  participant pcloud__services__alerts__notifier as cloud/services/alerts/notifier<br/>«adapter»<br/>Turns an opened alert into one<br/>notification to the owner
  participant ppush_dservice as push-service<br/>Registers phones for an owner<br/>and delivers a notification to<br/>them, for example APNs or FCM
  participant pmobile__ui as mobile/ui<br/>«adapter»<br/>Screens of the phone app
  participant papp_dui as app-ui<br/>Shows the state of each plant<br/>and tells the user when to water<br/>it
  pmobile__sync->>pcloud__services__gateway: 1 · upload-batch(00a1b2c3d4e5f607, readings 4711 to 4806) → 200, 4711 to 4806 are new
  pcloud__services__alerts__notifier->>ppush_dservice: 2 · send(the notification of the alert) → taken
  activate ppush_dservice
  ppush_dservice-)pmobile__ui: 3 · deliver(the notification of the alert) → ok
  deactivate ppush_dservice
  papp_dui->>pmobile__ui: 4 · notification-tap(the notification about Monstera) → the app opens the screen of #quot;Monstera#quot;
  activate pmobile__ui
  Note over pmobile__sync: active
  pmobile__ui->>pmobile__sync: 5 · plant(Monstera)
  activate pmobile__sync
  pmobile__sync->>pcloud__services__gateway: 6 · list-alerts()
  activate pcloud__services__gateway
  pcloud__services__gateway-->>pmobile__sync: ↩ 6 · 200 with the open alert of Monstera
  deactivate pcloud__services__gateway
  pmobile__sync-->>pmobile__ui: ↩ 5 · Monstera with its open alert
  deactivate pmobile__sync
  deactivate pmobile__ui
  papp_dui->>pmobile__ui: 7 · plants()
  activate pmobile__ui
  pmobile__ui-->>papp_dui: ↩ 7 · the plant is first in the list with #quot;needs water#quot;
  deactivate pmobile__ui
  Note over pmobile__sync,papp_dui: wrap: Expect: within 1 minute after the upload response the alert is open on the server and its notification is handed to the push service#59; the phone shows one notification, a tap opens #quot;Monstera#quot;, and the plant is first in the list with #quot;needs water#quot;
```

| # | Caller | Target | Call | Kind | Result | State | Contract |
|---|---|---|---|---|---|---|---|
| 1 | `mobile/sync` | `cloud/services/gateway` | `upload-batch(00a1b2c3d4e5f607, readings 4711 to 4806)` | command | 200, 4711 to 4806 are new |  | [public-api](../references/public-api/index.md) |
| 2 | `cloud/services/alerts/notifier` | `push-service` | `send(the notification of the alert)` | command | taken |  | [push-service](../references/push-service.md) |
| 3 | `mobile/ui` | `push-service` | `deliver(the notification of the alert)` | event | ok |  | [push-service](../references/push-service.md) |
| 4 | `app-ui` | `mobile/ui` | `notification-tap(the notification about Monstera)` | command | the app opens the screen of "Monstera" |  | [app-ui](../references/app-ui.md) |
| 5 | `mobile/ui` | `mobile/sync` | `plant(Monstera)` | query | Monstera with its open alert | active | [plant-data](../../mobile/docs/references/plant-data/index.md) |
| 6 | `mobile/sync` | `cloud/services/gateway` | `list-alerts()` | query | 200 with the open alert of Monstera |  | [public-api](../references/public-api/index.md) |
| 7 | `app-ui` | `mobile/ui` | `plants()` | query | the plant is first in the list with "needs water" |  | [app-ui](../references/app-ui.md) |
