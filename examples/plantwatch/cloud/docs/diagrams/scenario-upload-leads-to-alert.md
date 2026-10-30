<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: upload-leads-to-alert

[plantwatch](../../../docs/diagrams/component.md) / **cloud** · [README](../../README.md) · [context](context.md) · [component](component.md) · [architecture](architecture.md)

**An upload is accepted, enters the history, is judged and opens an alert**
Source: decisions 0001 and 0003 of cloud
Expect: the upload is answered with `new` before history and evaluation have seen the reading; within 10 seconds the reading is in the history of its plant; within 1 minute the alert is open and its notification is handed to the push service; the two branches run independently and in any order

A unit is named by its path from `cloud`; a capability or need of `cloud` is named bare. Every hop is a call along one connection of the map.

```mermaid
---
config:
  sequence:
    height: 124
---
sequenceDiagram
  participant ppublic_dapi as public-api<br/>«http»<br/>Upload readings and query<br/>plants, history and alerts
  participant pgateway as gateway<br/>«service»<br/>Single entry point of the server<br/>side that authenticates callers<br/>and routes requests
  participant pingest as ingest<br/>«service»<br/>Accepts uploaded readings and<br/>announces each accepted one as<br/>an event
  participant pplatform as platform<br/>«adapter»<br/>Shared infrastructure of the<br/>services - message bus and<br/>database
  participant pplants as plants<br/>«service»<br/>Registry of plants with their<br/>sensors, thresholds and reading<br/>history
  participant pservices__alerts__server as services/alerts/server<br/>«app»<br/>Process that consumes readings,<br/>stores the alerts they lead to<br/>and answers queries about them
  participant pservices__alerts__plant_dlookup as services/alerts/plant-lookup<br/>«adapter»<br/>Looks up the plant a sensor<br/>stick is attached to, with owner<br/>and thresholds, in the registry<br/>of plants
  participant pservices__alerts__notifier as services/alerts/notifier<br/>«adapter»<br/>Turns an opened alert into one<br/>notification to the owner
  participant ppush_dservice as push-service<br/>«http»<br/>Takes a notification for an<br/>owner and delivers it to the<br/>phones registered for that owner
  ppublic_dapi->>pgateway: 1 · upload-batch
  pgateway->>pingest: 2 · upload-batch
  pingest->>pplatform: 3 · publish
  pplants->>pingest: 4 · reading-accepted
  pplants->>pplatform: 5 · deliver
  pplants->>pplatform: 6 · transaction
  pplants->>pplatform: 7 · commit
  pservices__alerts__server->>pingest: 8 · reading-accepted
  pservices__alerts__server->>pplatform: 9 · deliver
  pservices__alerts__plant_dlookup->>pplants: 10 · lookup-by-sensor
  pservices__alerts__server->>pplatform: 11 · transaction
  pservices__alerts__server->>pplatform: 12 · commit
  pservices__alerts__notifier->>ppush_dservice: 13 · send
  ppublic_dapi->>pgateway: 14 · list-alerts
  pgateway->>pservices__alerts__server: 15 · list-alerts
  ppublic_dapi->>pgateway: 16 · get-history
  pgateway->>pplants: 17 · get-history
  Note over ppublic_dapi,ppush_dservice: wrap: Expect: the upload is answered with `new` before history and evaluation have seen the reading#59; within 10 seconds the reading is in the history of its plant#59; within 1 minute the alert is open and its notification is handed to the push service#59; the two branches run independently and in any order
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `public-api` | `gateway` | `upload-batch` | [index](../../../docs/references/public-api/index.md) |
| 2 | `gateway` | `ingest` | `upload-batch` | [ingest-api](../references/ingest-api.md) |
| 3 | `ingest` | `platform` | `publish` | [event-bus](../references/event-bus.md) |
| 4 | `plants` | `ingest` | `reading-accepted` | [reading-events](../references/reading-events.md) |
| 5 | `plants` | `platform` | `deliver` | [event-bus](../references/event-bus.md) |
| 6 | `plants` | `platform` | `transaction` | [sql-db](../references/sql-db.md) |
| 7 | `plants` | `platform` | `commit` | [event-bus](../references/event-bus.md) |
| 8 | `services/alerts/server` | `ingest` | `reading-accepted` | [reading-events](../references/reading-events.md) |
| 9 | `services/alerts/server` | `platform` | `deliver` | [event-bus](../references/event-bus.md) |
| 10 | `services/alerts/plant-lookup` | `plants` | `lookup-by-sensor` | [plants-api](../references/plants-api.md) |
| 11 | `services/alerts/server` | `platform` | `transaction` | [sql-db](../references/sql-db.md) |
| 12 | `services/alerts/server` | `platform` | `commit` | [event-bus](../references/event-bus.md) |
| 13 | `services/alerts/notifier` | `push-service` | `send` | [push-service](../../../docs/references/push-service.md) |
| 14 | `public-api` | `gateway` | `list-alerts` | [index](../../../docs/references/public-api/index.md) |
| 15 | `gateway` | `services/alerts/server` | `list-alerts` | [alerts-api](../references/alerts-api.md) |
| 16 | `public-api` | `gateway` | `get-history` | [index](../../../docs/references/public-api/index.md) |
| 17 | `gateway` | `plants` | `get-history` | [plants-api](../references/plants-api.md) |
