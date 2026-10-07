<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: ingest

[ingest](../../README.md)

`ingest` among its siblings inside `cloud`. Only connections that touch `ingest` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_cloud["cloud"]
    u_cloud_platform["platform"]
    u_cloud_services_alerts["alerts"]
    u_cloud_services_gateway["gateway"]
    u_cloud_services_ingest["ingest"]
    u_cloud_services_plants["plants"]
  end
  n_cloud_reading_format{{"reading-format"}}
  u_cloud_services_gateway -->|"ingest-api"| u_cloud_services_ingest
  u_cloud_services_ingest -->|"event-bus"| u_cloud_platform
  u_cloud_services_ingest -->|"reading-format"| n_cloud_reading_format
  u_cloud_services_plants -->|"reading-events"| u_cloud_services_ingest
  u_cloud_services_alerts -->|"reading-events"| u_cloud_services_ingest
  click u_cloud_platform href "../../../../platform/README.md"
  click u_cloud_services_alerts href "../../../alerts/README.md"
  click u_cloud_services_gateway href "../../../gateway/README.md"
  click u_cloud_services_ingest href "../../README.md"
  click u_cloud_services_plants href "../../../plants/README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_cloud,u_cloud_platform,u_cloud_services_alerts,u_cloud_services_gateway,u_cloud_services_ingest,u_cloud_services_plants planned
  class u_cloud_services_ingest focus
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [cloud](../../../../README.md) | Server side that stores readings, keeps the plant registry and raises alerts | planned | [component](../../../../doc/diagrams/component.md) |
| [platform](../../../../platform/README.md) | Shared infrastructure of the services - message bus and database | planned | [context](../../../../platform/doc/diagrams/context.md) |
| [alerts](../../../alerts/README.md) | Decides when a plant needs attention and notifies its owner once | planned | [component](../../../alerts/doc/diagrams/component.md) |
| [gateway](../../../gateway/README.md) | Single entry point of the server side that authenticates callers and routes requests | planned | [context](../../../gateway/doc/diagrams/context.md) |
| [ingest](../../README.md) | Accepts uploaded readings, validates them and publishes each one once | planned | [context](context.md) |
| [plants](../../../plants/README.md) | Registry of plants with their sensors, thresholds and reading history | planned | [context](../../../plants/doc/diagrams/context.md) |
