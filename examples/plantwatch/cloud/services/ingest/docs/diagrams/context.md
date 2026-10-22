<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: ingest

[plantwatch](../../../../../docs/diagrams/component.md) / [cloud](../../../../docs/diagrams/component.md) / **ingest** · [README](../../README.md)

`ingest` inside `cloud`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_cloud["cloud"]
    u_cloud__platform["platform"]
    u_cloud__services__alerts["alerts"]
    u_cloud__services__gateway["gateway"]
    u_cloud__services__ingest["ingest"]
    u_cloud__services__plants["plants"]
  end
  u_cloud__services__ingest -->|"event-bus"| u_cloud__platform
  u_cloud__services__gateway -->|"ingest-api"| u_cloud__services__ingest
  u_cloud__services__plants -->|"reading-events"| u_cloud__services__ingest
  u_cloud__services__alerts -->|"reading-events"| u_cloud__services__ingest
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud__platform,u_cloud__services__alerts,u_cloud__services__gateway,u_cloud__services__ingest,u_cloud__services__plants planned
  class u_cloud__services__ingest focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [platform](../../../../platform/README.md) | infrastructure | Shared infrastructure of the services - message bus and database | **planned** | [context](../../../../platform/docs/diagrams/context.md) |
| [alerts](../../../alerts/README.md) | service | Decides when a plant needs attention and notifies its owner once | **planned** | [component](../../../alerts/docs/diagrams/component.md) |
| [gateway](../../../gateway/README.md) | service | Single entry point of the server side that authenticates callers and routes requests | **planned** | [context](../../../gateway/docs/diagrams/context.md) |
| [ingest](../../README.md) | service | Accepts uploaded readings and announces each accepted one as an event | **planned** | [context](context.md) |
| [plants](../../../plants/README.md) | service | Registry of plants with their sensors, thresholds and reading history | **planned** | [context](../../../plants/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability | Verified by |
|---|---|---|---|---|---|
| event-bus | queue | [contract](../../../../docs/references/event-bus.md) | [cloud/platform](../../../../platform/README.md) (planned) | event-bus |  |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need |
|---|---|---|---|---|---|
| ingest-api | http | [contract](../../../../docs/references/ingest-api.md) |  | [cloud/services/gateway](../../../gateway/README.md) (planned) | ingest-api |
| reading-events | events | [contract](../../../../docs/references/reading-events.md) |  | [cloud/services/plants](../../../plants/README.md) (planned) | reading-events |
| reading-events | events | [contract](../../../../docs/references/reading-events.md) |  | [cloud/services/alerts/server](../../../alerts/server/README.md) (planned) | reading-events |
