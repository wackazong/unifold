<!-- unifold:generated - do not edit; run `unifold check --fix` -->
# Context diagram: alerts

[plantwatch](../../../../../docs/diagrams/component.md) / [cloud](../../../../docs/diagrams/component.md) / **alerts** · [README](../../README.md) · [component](component.md)

`alerts` inside `cloud`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_cloud["cloud"]
    u_cloud__platform["platform (adapter)"]
    u_cloud__services__alerts["alerts (service)"]
    u_cloud__services__gateway["gateway (service)"]
    u_cloud__services__ingest["ingest (service)"]
    u_cloud__services__plants["plants (service)"]
  end
  n_cloud___push_dservice{{"push-service"}}
  u_cloud__services__alerts -->|"event-bus, sql-db"| u_cloud__platform
  u_cloud__services__gateway -->|"alerts-api"| u_cloud__services__alerts
  u_cloud__services__alerts -->|"reading-events"| u_cloud__services__ingest
  u_cloud__services__alerts -->|"plants-api"| u_cloud__services__plants
  u_cloud__services__alerts -->|"push → push-service"| n_cloud___push_dservice
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud__platform,u_cloud__services__alerts,u_cloud__services__gateway,u_cloud__services__ingest,u_cloud__services__plants planned
  class u_cloud__services__alerts focus
```

| Unit | Kind | Responsibility | Status | Diagram |
|---|---|---|---|---|
| [platform](../../../../platform/README.md) | adapter | Shared infrastructure of the services - message bus and database | **planned** |  |
| [alerts](../../README.md) | service | Decides when a plant needs attention and notifies its owner once | **planned** | [component](component.md) |
| [gateway](../../../gateway/README.md) | service | Single entry point of the server side that authenticates callers and routes requests | **planned** |  |
| [ingest](../../../ingest/README.md) | service | Accepts uploaded readings and announces each accepted one as an event | **planned** |  |
| [plants](../../../plants/README.md) | service | Registry of plants with their sensors, thresholds and reading history | **planned** |  |

### Who provides what this unit needs

| Need | Contract | Provided by | Capability |
|---|---|---|---|
| reading-events | [contract](../../../../docs/references/reading-events.md) | [cloud/services/ingest](../../../ingest/README.md) (planned) | reading-events |
| plants-api | [contract](../../../../docs/references/plants-api.md) | [cloud/services/plants](../../../plants/README.md) (planned) | plants-api |
| push | [contract](../../../../../docs/references/push-service.md) | outside the project, as need `push-service` of the root | |
| sql-db | [contract](../../../../docs/references/sql-db.md) | [cloud/platform](../../../../platform/README.md) (planned) | sql-db |
| event-bus | [contract](../../../../docs/references/event-bus.md) | [cloud/platform](../../../../platform/README.md) (planned) | event-bus |

### Who uses what this unit provides

| Capability | Contract | Used by | As need |
|---|---|---|---|
| alerts-api | [contract](../../../../docs/references/alerts-api.md) | [cloud/services/gateway](../../../gateway/README.md) (planned) | alerts-api |
