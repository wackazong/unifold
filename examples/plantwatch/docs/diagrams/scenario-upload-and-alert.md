<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: upload-and-alert

**plantwatch** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**The phone uploads readings, the server opens an alert and the owner is notified once**
Source: requirements of plantwatch, the public API, consistency
Expect: within 1 minute after the upload response the alert is open on the server and its notification is handed to the push service; the phone shows one notification, a tap opens "Monstera", and the plant is first in the list with "needs water"

A unit is named by its path from `plantwatch`; a capability or need of `plantwatch` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it.

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
  participant ppush_dservice as push-service<br/>«http»<br/>Registers phones for an owner<br/>and delivers a notification to<br/>them, for example APNs or FCM
  participant pmobile__ui as mobile/ui<br/>«adapter»<br/>Screens of the phone app
  participant papp_dui as app-ui<br/>«ui»<br/>Shows the state of each plant<br/>and tells the user when to water<br/>it
  pmobile__sync->>pcloud__services__gateway: 1 · upload-batch
  activate pcloud__services__gateway
  deactivate pcloud__services__gateway
  pcloud__services__alerts__notifier->>ppush_dservice: 2 · send
  activate ppush_dservice
  ppush_dservice-)pmobile__ui: 3 · deliver
  activate pmobile__ui
  deactivate pmobile__ui
  deactivate ppush_dservice
  papp_dui->>pmobile__ui: 4 · notification-tap
  activate pmobile__ui
  pmobile__ui->>pmobile__sync: 5 · plant
  activate pmobile__sync
  pmobile__sync->>pcloud__services__gateway: 6 · list-alerts
  activate pcloud__services__gateway
  pcloud__services__gateway-->>pmobile__sync: ↩ 6
  deactivate pcloud__services__gateway
  pmobile__sync-->>pmobile__ui: ↩ 5
  deactivate pmobile__sync
  deactivate pmobile__ui
  papp_dui->>pmobile__ui: 7 · plants
  activate pmobile__ui
  pmobile__ui-->>papp_dui: ↩ 7
  deactivate pmobile__ui
  Note over pmobile__sync,papp_dui: wrap: Expect: within 1 minute after the upload response the alert is open on the server and its notification is handed to the push service#59; the phone shows one notification, a tap opens #quot;Monstera#quot;, and the plant is first in the list with #quot;needs water#quot;
```

| # | Caller | Target | Part | Kind | Contract |
|---|---|---|---|---|---|
| 1 | `mobile/sync` | `cloud/services/gateway` | `upload-batch` | command | [index](../references/public-api/index.md) |
| 2 | `cloud/services/alerts/notifier` | `push-service` | `send` | command | [push-service](../references/push-service.md) |
| 3 | `mobile/ui` | `push-service` | `deliver` | event | [push-service](../references/push-service.md) |
| 4 | `app-ui` | `mobile/ui` | `notification-tap` | command | [app-ui](../references/app-ui.md) |
| 5 | `mobile/ui` | `mobile/sync` | `plant` | query | [index](../../mobile/docs/references/plant-data/index.md) |
| 6 | `mobile/sync` | `cloud/services/gateway` | `list-alerts` | query | [index](../references/public-api/index.md) |
| 7 | `app-ui` | `mobile/ui` | `plants` | query | [app-ui](../references/app-ui.md) |
