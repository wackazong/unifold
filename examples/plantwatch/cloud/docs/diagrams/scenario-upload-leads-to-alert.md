<!-- unifold:generated - do not edit; run `unifold check --fix` -->
# Scenario: upload-leads-to-alert

[plantwatch](../../../docs/diagrams/component.md) / **cloud** · [README](../../README.md) · [context](context.md) · [component](component.md) · [architecture](architecture.md)

**An upload is accepted, enters the history, is judged and opens an alert**
Source: decisions 0001 and 0003 of cloud
Expect: the upload is answered with `new` before history and evaluation have seen the reading; within 10 seconds the reading is in the history of its plant; within 1 minute the alert is open and its notification is handed to the push service; the two branches run independently and in any order

A unit is named by its path from `cloud`; a capability or need of `cloud` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it. An event from an idle lifeline lands on the bar of a busy receiver, or starts one. A step shows its result; a note on a provider's lifeline shows the state of a connection whose contract has states.

```mermaid
---
config:
  sequence:
    height: 124
---
sequenceDiagram
  participant ppublic_dapi as public-api<br/>Upload readings and query<br/>plants, history and alerts
  participant pgateway as gateway<br/>«service»<br/>Single entry point of the server<br/>side that authenticates callers<br/>and routes requests
  participant pingest as ingest<br/>«service»<br/>Accepts uploaded readings and<br/>announces each accepted one as<br/>an event
  participant pplatform as platform<br/>«adapter»<br/>Shared infrastructure of the<br/>services - message bus and<br/>database
  participant pplants as plants<br/>«service»<br/>Registry of plants with their<br/>sensors, thresholds and reading<br/>history
  participant pservices__alerts__plant_dlookup as services/alerts/plant-lookup<br/>«adapter»<br/>Looks up the plant a sensor<br/>stick is attached to, with owner<br/>and thresholds, in the registry<br/>of plants
  participant pservices__alerts__server as services/alerts/server<br/>«app»<br/>Process that consumes readings,<br/>stores the alerts they lead to<br/>and answers queries about them
  participant pservices__alerts__notifier as services/alerts/notifier<br/>«adapter»<br/>Turns an opened alert into one<br/>notification to the owner
  participant ppush_dservice as push-service<br/>Takes a notification for an<br/>owner and delivers it to the<br/>phones registered for that owner
  ppublic_dapi->>pgateway: 1 · upload-batch(00a1b2c3d4e5f607, reading 4711) → 200, 4711 is new
  activate pgateway
  pgateway->>pingest: 2 · upload-batch(00a1b2c3d4e5f607, reading 4711) → 200, 4711 is new
  activate pingest
  pingest->>pplatform: 3 · publish(ingest.readings.v1, the event 00a1b2c3d4e5f607-4711) → acknowledged
  pingest-)pplants: 4 · reading-accepted(00a1b2c3d4e5f607-4711) → ok
  activate pplants
  pplatform-)pplants: 5 · deliver(the event 00a1b2c3d4e5f607-4711) → ok
  pplants->>pplatform: 6 · transaction → ok
  pplants->>pplatform: 7 · commit → ok
  deactivate pplants
  pingest-)pservices__alerts__server: 8 · reading-accepted(00a1b2c3d4e5f607-4711) → ok
  activate pservices__alerts__server
  pplatform-)pservices__alerts__server: 9 · deliver(the event 00a1b2c3d4e5f607-4711) → ok
  deactivate pservices__alerts__server
  deactivate pingest
  deactivate pgateway
  pservices__alerts__plant_dlookup->>pplants: 10 · lookup-by-sensor(00a1b2c3d4e5f607)
  activate pplants
  pplants-->>pservices__alerts__plant_dlookup: ↩ 10 · 200 with plant_id P and owner_id A
  deactivate pplants
  pservices__alerts__server->>pplatform: 11 · transaction → ok
  pservices__alerts__server->>pplatform: 12 · commit → ok
  pservices__alerts__notifier->>ppush_dservice: 13 · send(the notification of the alert) → taken
  ppublic_dapi->>pgateway: 14 · list-alerts()
  activate pgateway
  pgateway->>pservices__alerts__server: 15 · list-alerts()
  activate pservices__alerts__server
  pservices__alerts__server-->>pgateway: ↩ 15 · 200 with the open alert
  deactivate pservices__alerts__server
  pgateway-->>ppublic_dapi: ↩ 14 · 200 with the open alert
  deactivate pgateway
  ppublic_dapi->>pgateway: 16 · get-history(P)
  activate pgateway
  pgateway->>pplants: 17 · get-history(P)
  activate pplants
  pplants-->>pgateway: ↩ 17 · 200 with reading 4711
  deactivate pplants
  pgateway-->>ppublic_dapi: ↩ 16 · 200 with reading 4711
  deactivate pgateway
  Note over ppublic_dapi,ppush_dservice: wrap: Expect: the upload is answered with `new` before history and evaluation have seen the reading#59; within 10 seconds the reading is in the history of its plant#59; within 1 minute the alert is open and its notification is handed to the push service#59; the two branches run independently and in any order
```

| # | Caller | Target | Call | Kind | Result | State | Contract |
|---|---|---|---|---|---|---|---|
| 1 | `public-api` | `gateway` | `upload-batch(00a1b2c3d4e5f607, reading 4711)` | command | 200, 4711 is new |  | [public-api](../../../docs/references/public-api/index.md) |
| 2 | `gateway` | `ingest` | `upload-batch(00a1b2c3d4e5f607, reading 4711)` | command | 200, 4711 is new |  | [ingest-api](../references/ingest-api.md) |
| 3 | `ingest` | `platform` | `publish(ingest.readings.v1, the event 00a1b2c3d4e5f607-4711)` | command | acknowledged |  | [event-bus](../references/event-bus.md) |
| 4 | `plants` | `ingest` | `reading-accepted(00a1b2c3d4e5f607-4711)` | event | ok |  | [reading-events](../references/reading-events.md) |
| 5 | `plants` | `platform` | `deliver(the event 00a1b2c3d4e5f607-4711)` | event | ok |  | [event-bus](../references/event-bus.md) |
| 6 | `plants` | `platform` | `transaction` | command | ok |  | [sql-db](../references/sql-db.md) |
| 7 | `plants` | `platform` | `commit` | command | ok |  | [event-bus](../references/event-bus.md) |
| 8 | `services/alerts/server` | `ingest` | `reading-accepted(00a1b2c3d4e5f607-4711)` | event | ok |  | [reading-events](../references/reading-events.md) |
| 9 | `services/alerts/server` | `platform` | `deliver(the event 00a1b2c3d4e5f607-4711)` | event | ok |  | [event-bus](../references/event-bus.md) |
| 10 | `services/alerts/plant-lookup` | `plants` | `lookup-by-sensor(00a1b2c3d4e5f607)` | query | 200 with plant_id P and owner_id A |  | [plants-api](../references/plants-api.md) |
| 11 | `services/alerts/server` | `platform` | `transaction` | command | ok |  | [sql-db](../references/sql-db.md) |
| 12 | `services/alerts/server` | `platform` | `commit` | command | ok |  | [event-bus](../references/event-bus.md) |
| 13 | `services/alerts/notifier` | `push-service` | `send(the notification of the alert)` | command | taken |  | [push-service](../../../docs/references/push-service.md) |
| 14 | `public-api` | `gateway` | `list-alerts()` | query | 200 with the open alert |  | [public-api](../../../docs/references/public-api/index.md) |
| 15 | `gateway` | `services/alerts/server` | `list-alerts()` | query | 200 with the open alert |  | [alerts-api](../references/alerts-api.md) |
| 16 | `public-api` | `gateway` | `get-history(P)` | query | 200 with reading 4711 |  | [public-api](../../../docs/references/public-api/index.md) |
| 17 | `gateway` | `plants` | `get-history(P)` | query | 200 with reading 4711 |  | [plants-api](../references/plants-api.md) |
