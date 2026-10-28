<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: platform

[plantwatch](../../../../docs/diagrams/component.md) / [cloud](../../../docs/diagrams/component.md) / **platform** · [README](../../README.md)

`platform` inside `cloud`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_cloud["cloud"]
    u_cloud__platform["platform (adapter)"]
    u_cloud__services__alerts["alerts (service)"]
    u_cloud__services__ingest["ingest (service)"]
    u_cloud__services__plants["plants (service)"]
  end
  n_cloud___container_dhost{{"container-host"}}
  u_cloud__services__ingest -->|"event-bus"| u_cloud__platform
  u_cloud__services__plants -->|"event-bus, sql-db"| u_cloud__platform
  u_cloud__services__alerts -->|"event-bus, sql-db"| u_cloud__platform
  u_cloud__platform -->|"container-host"| n_cloud___container_dhost
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud__platform,u_cloud__services__alerts,u_cloud__services__ingest,u_cloud__services__plants planned
  class u_cloud__platform focus
```

| Unit | Kind | Responsibility | Status | Diagram |
|---|---|---|---|---|
| [platform](../../README.md) | adapter | Shared infrastructure of the services - message bus and database | **planned** | [context](context.md) |
| [alerts](../../../services/alerts/README.md) | service | Decides when a plant needs attention and notifies its owner once | **planned** | [component](../../../services/alerts/docs/diagrams/component.md) |
| [ingest](../../../services/ingest/README.md) | service | Accepts uploaded readings and announces each accepted one as an event | **planned** | [context](../../../services/ingest/docs/diagrams/context.md) |
| [plants](../../../services/plants/README.md) | service | Registry of plants with their sensors, thresholds and reading history | **planned** | [context](../../../services/plants/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability |
|---|---|---|---|---|
| container-host | infrastructure | [contract](../../../../docs/references/container-host.md) | outside the project, as need `container-host` of the root | |

### Who uses what this unit provides

| Capability | Kind | Contract | Used by | As need |
|---|---|---|---|---|
| event-bus | queue | [contract](../../../docs/references/event-bus.md) | [cloud/services/ingest](../../../services/ingest/README.md) (planned) | event-bus |
| event-bus | queue | [contract](../../../docs/references/event-bus.md) | [cloud/services/plants](../../../services/plants/README.md) (planned) | event-bus |
| event-bus | queue | [contract](../../../docs/references/event-bus.md) | [cloud/services/alerts/server](../../../services/alerts/server/README.md) (planned) | event-bus |
| sql-db | db | [contract](../../../docs/references/sql-db.md) | [cloud/services/plants](../../../services/plants/README.md) (planned) | sql-db |
| sql-db | db | [contract](../../../docs/references/sql-db.md) | [cloud/services/alerts/server](../../../services/alerts/server/README.md) (planned) | sql-db |
