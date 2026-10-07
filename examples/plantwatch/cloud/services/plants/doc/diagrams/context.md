<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: plants

[plants](../../README.md)

`plants` among its siblings inside `cloud`. Only connections that touch `plants` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_cloud["cloud"]
    u_cloud_platform["platform"]
    u_cloud_services_alerts["alerts"]
    u_cloud_services_gateway["gateway"]
    u_cloud_services_ingest["ingest"]
    u_cloud_services_plants["plants"]
  end
  u_cloud_services_gateway -->|"plants-api"| u_cloud_services_plants
  u_cloud_services_plants -->|"reading-events"| u_cloud_services_ingest
  u_cloud_services_plants -->|"sql-db"| u_cloud_platform
  u_cloud_services_plants -->|"event-bus"| u_cloud_platform
  u_cloud_services_alerts -->|"plants-api"| u_cloud_services_plants
  click u_cloud_platform href "../../../../platform/README.md"
  click u_cloud_services_alerts href "../../../alerts/README.md"
  click u_cloud_services_gateway href "../../../gateway/README.md"
  click u_cloud_services_ingest href "../../../ingest/README.md"
  click u_cloud_services_plants href "../../README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_cloud,u_cloud_platform,u_cloud_services_alerts,u_cloud_services_gateway,u_cloud_services_ingest,u_cloud_services_plants planned
  class u_cloud_services_plants focus
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [cloud](../../../../README.md) | Server side that stores readings, keeps the plant registry and raises alerts | planned | [component](../../../../doc/diagrams/component.md) |
| [platform](../../../../platform/README.md) | Shared infrastructure of the services - message bus and database | planned | [context](../../../../platform/doc/diagrams/context.md) |
| [alerts](../../../alerts/README.md) | Decides when a plant needs attention and notifies its owner once | planned | [component](../../../alerts/doc/diagrams/component.md) |
| [gateway](../../../gateway/README.md) | Single entry point of the server side that authenticates callers and routes requests | planned | [context](../../../gateway/doc/diagrams/context.md) |
| [ingest](../../../ingest/README.md) | Accepts uploaded readings, validates them and publishes each one once | planned | [context](../../../ingest/doc/diagrams/context.md) |
| [plants](../../README.md) | Registry of plants with their sensors, thresholds and reading history | planned | [context](context.md) |
