<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: plants

[plantwatch](../../../../../docs/diagrams/component.md) / [cloud](../../../../docs/diagrams/component.md) / **plants** · [README](../../README.md)

`plants` inside `cloud`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_cloud["cloud"]
    u_cloud__platform["platform (adapter)"]
    u_cloud__services__alerts["alerts (service)"]
    u_cloud__services__gateway["gateway (service)"]
    u_cloud__services__ingest["ingest (service)"]
    u_cloud__services__plants["plants (service)"]
  end
  u_cloud__services__plants -->|"event-bus, sql-db"| u_cloud__platform
  u_cloud__services__gateway -->|"plants-api"| u_cloud__services__plants
  u_cloud__services__plants -->|"reading-events"| u_cloud__services__ingest
  u_cloud__services__alerts -->|"plants-api"| u_cloud__services__plants
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud__platform,u_cloud__services__alerts,u_cloud__services__gateway,u_cloud__services__ingest,u_cloud__services__plants planned
  class u_cloud__services__plants focus
```

| Unit | Kind | Responsibility | Status | Diagram |
|---|---|---|---|---|
| [platform](../../../../platform/README.md) | adapter | Shared infrastructure of the services - message bus and database | **planned** | [context](../../../../platform/docs/diagrams/context.md) |
| [alerts](../../../alerts/README.md) | service | Decides when a plant needs attention and notifies its owner once | **planned** | [component](../../../alerts/docs/diagrams/component.md) |
| [gateway](../../../gateway/README.md) | service | Single entry point of the server side that authenticates callers and routes requests | **planned** | [context](../../../gateway/docs/diagrams/context.md) |
| [ingest](../../../ingest/README.md) | service | Accepts uploaded readings and announces each accepted one as an event | **planned** | [context](../../../ingest/docs/diagrams/context.md) |
| [plants](../../README.md) | service | Registry of plants with their sensors, thresholds and reading history | **planned** | [context](context.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability |
|---|---|---|---|---|
| reading-events | events | [contract](../../../../docs/references/reading-events.md) | [cloud/services/ingest](../../../ingest/README.md) (planned) | reading-events |
| sql-db | db | [contract](../../../../docs/references/sql-db.md) | [cloud/platform](../../../../platform/README.md) (planned) | sql-db |
| event-bus | queue | [contract](../../../../docs/references/event-bus.md) | [cloud/platform](../../../../platform/README.md) (planned) | event-bus |

### Who uses what this unit provides

| Capability | Kind | Contract | Used by | As need |
|---|---|---|---|---|
| plants-api | http | [contract](../../../../docs/references/plants-api.md) | [cloud/services/gateway](../../../gateway/README.md) (planned) | plants-api |
| plants-api | http | [contract](../../../../docs/references/plants-api.md) | [cloud/services/alerts/plant-lookup](../../../alerts/plant-lookup/README.md) (planned) | plants-api |
