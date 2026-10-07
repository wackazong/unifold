<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Component diagram: cloud

[cloud](../../README.md) · [context](context.md) · [architecture](architecture.md)

The units directly inside `cloud` and how they are wired. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_cloud["cloud"]
    u_cloud_platform["platform"]
    u_cloud_services_alerts["alerts"]
    u_cloud_services_gateway["gateway"]
    u_cloud_services_ingest["ingest"]
    u_cloud_services_plants["plants"]
  end
  p_cloud_public_api(["public-api"])
  n_cloud_push_service{{"push-service"}}
  n_cloud_reading_format{{"reading-format"}}
  n_cloud_container_host{{"container-host"}}
  p_cloud_public_api --> u_cloud_services_gateway
  u_cloud_services_gateway -->|"ingest-api"| u_cloud_services_ingest
  u_cloud_services_gateway -->|"plants-api"| u_cloud_services_plants
  u_cloud_services_gateway -->|"alerts-api"| u_cloud_services_alerts
  u_cloud_services_ingest -->|"event-bus"| u_cloud_platform
  u_cloud_services_ingest -->|"reading-format"| n_cloud_reading_format
  u_cloud_services_plants -->|"reading-events"| u_cloud_services_ingest
  u_cloud_services_plants -->|"sql-db"| u_cloud_platform
  u_cloud_services_plants -->|"event-bus"| u_cloud_platform
  u_cloud_services_alerts -->|"reading-events"| u_cloud_services_ingest
  u_cloud_services_alerts -->|"plants-api"| u_cloud_services_plants
  u_cloud_services_alerts -->|"push → push-service"| n_cloud_push_service
  u_cloud_services_alerts -->|"sql-db"| u_cloud_platform
  u_cloud_services_alerts -->|"event-bus"| u_cloud_platform
  u_cloud_platform -->|"container-host"| n_cloud_container_host
  click u_cloud_platform href "../../platform/README.md"
  click u_cloud_services_alerts href "../../services/alerts/README.md"
  click u_cloud_services_gateway href "../../services/gateway/README.md"
  click u_cloud_services_ingest href "../../services/ingest/README.md"
  click u_cloud_services_plants href "../../services/plants/README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_cloud,u_cloud_platform,u_cloud_services_alerts,u_cloud_services_gateway,u_cloud_services_ingest,u_cloud_services_plants planned
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [cloud](../../README.md) | Server side that stores readings, keeps the plant registry and raises alerts | planned | [component](component.md) |
| [platform](../../platform/README.md) | Shared infrastructure of the services - message bus and database | planned | [context](../../platform/doc/diagrams/context.md) |
| [alerts](../../services/alerts/README.md) | Decides when a plant needs attention and notifies its owner once | planned | [component](../../services/alerts/doc/diagrams/component.md) |
| [gateway](../../services/gateway/README.md) | Single entry point of the server side that authenticates callers and routes requests | planned | [context](../../services/gateway/doc/diagrams/context.md) |
| [ingest](../../services/ingest/README.md) | Accepts uploaded readings, validates them and publishes each one once | planned | [context](../../services/ingest/doc/diagrams/context.md) |
| [plants](../../services/plants/README.md) | Registry of plants with their sensors, thresholds and reading history | planned | [context](../../services/plants/doc/diagrams/context.md) |
