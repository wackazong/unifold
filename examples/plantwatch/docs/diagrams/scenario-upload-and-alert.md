<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: upload-and-alert

**plantwatch** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**The phone uploads readings, the server opens an alert and the owner is notified once**
Source: requirements of plantwatch, the public API, consistency
Expect: within 1 minute after the upload response the alert is open on the server and its notification is handed to the push service; the phone shows one notification, a tap opens "Monstera", and the plant is first in the list with "needs water"

A unit is named by its path from `plantwatch`; a capability or need of `plantwatch` is named bare. Every hop is a call along one connection of the map.

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
  pcloud__services__alerts__notifier->>ppush_dservice: 2 · send
  pmobile__ui->>ppush_dservice: 3 · deliver
  papp_dui->>pmobile__ui: 4 · notification-tap
  pmobile__ui->>pmobile__sync: 5 · plant
  pmobile__sync->>pcloud__services__gateway: 6 · list-alerts
  papp_dui->>pmobile__ui: 7 · plants
  Note over pmobile__sync,papp_dui: wrap: Expect: within 1 minute after the upload response the alert is open on the server and its notification is handed to the push service#59; the phone shows one notification, a tap opens #quot;Monstera#quot;, and the plant is first in the list with #quot;needs water#quot;
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `mobile/sync` | `cloud/services/gateway` | `upload-batch` | [index](../references/public-api/index.md) |
| 2 | `cloud/services/alerts/notifier` | `push-service` | `send` | [push-service](../references/push-service.md) |
| 3 | `mobile/ui` | `push-service` | `deliver` | [push-service](../references/push-service.md) |
| 4 | `app-ui` | `mobile/ui` | `notification-tap` | [app-ui](../references/app-ui.md) |
| 5 | `mobile/ui` | `mobile/sync` | `plant` | [index](../../mobile/docs/references/plant-data/index.md) |
| 6 | `mobile/sync` | `cloud/services/gateway` | `list-alerts` | [index](../references/public-api/index.md) |
| 7 | `app-ui` | `mobile/ui` | `plants` | [app-ui](../references/app-ui.md) |
