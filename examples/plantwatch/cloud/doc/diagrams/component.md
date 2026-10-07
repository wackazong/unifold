<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Component diagram: cloud

[plantwatch](../../../doc/diagrams/component.md) / **cloud** · [README](../../README.md) · [context](context.md) · [architecture](architecture.md)

The units directly inside `cloud` and how they are wired. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

```mermaid
flowchart LR
  subgraph u_cloud["cloud"]
    u_cloud__platform["platform"]
    u_cloud__services__alerts["alerts"]
    u_cloud__services__gateway["gateway"]
    u_cloud__services__ingest["ingest"]
    u_cloud__services__plants["plants"]
  end
  p_cloud___public_dapi(["public-api"])
  n_cloud___push_dservice{{"push-service"}}
  n_cloud___reading_dformat{{"reading-format"}}
  n_cloud___container_dhost{{"container-host"}}
  p_cloud___public_dapi --> u_cloud__services__gateway
  u_cloud__services__gateway -->|"ingest-api"| u_cloud__services__ingest
  u_cloud__services__gateway -->|"plants-api"| u_cloud__services__plants
  u_cloud__services__gateway -->|"alerts-api"| u_cloud__services__alerts
  u_cloud__services__ingest -->|"reading-format"| n_cloud___reading_dformat
  u_cloud__services__plants -->|"reading-events"| u_cloud__services__ingest
  u_cloud__services__alerts -->|"reading-events"| u_cloud__services__ingest
  u_cloud__services__alerts -->|"plants-api"| u_cloud__services__plants
  u_cloud__services__alerts -->|"push → push-service"| n_cloud___push_dservice
  u_cloud__platform -->|"container-host"| n_cloud___container_dhost
  u_cloud__services__alerts -->|"event-bus, sql-db"| u_cloud__platform
  u_cloud__services__ingest -->|"event-bus"| u_cloud__platform
  u_cloud__services__plants -->|"event-bus, sql-db"| u_cloud__platform
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_cloud,u_cloud__platform,u_cloud__services__alerts,u_cloud__services__gateway,u_cloud__services__ingest,u_cloud__services__plants planned
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [cloud](../../README.md) | system | Server side that turns uploaded readings into plant history and alerts | planned | [component](component.md) |
| [platform](../../platform/README.md) | infrastructure | Shared infrastructure of the services - message bus and database | planned | [context](../../platform/doc/diagrams/context.md) |
| [alerts](../../services/alerts/README.md) | service | Decides when a plant needs attention and notifies its owner once | planned | [component](../../services/alerts/doc/diagrams/component.md) |
| [gateway](../../services/gateway/README.md) | service | Single entry point of the server side that authenticates callers and routes requests | planned | [context](../../services/gateway/doc/diagrams/context.md) |
| [ingest](../../services/ingest/README.md) | service | Accepts uploaded readings and announces each accepted one as an event | planned | [context](../../services/ingest/doc/diagrams/context.md) |
| [plants](../../services/plants/README.md) | service | Registry of plants with their sensors, thresholds and reading history | planned | [context](../../services/plants/doc/diagrams/context.md) |
