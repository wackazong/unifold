<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Architecture diagram: alerts

[plantwatch](../../../../../doc/diagrams/component.md) / [cloud](../../../../doc/diagrams/component.md) / **alerts** · [README](../../README.md) · [context](context.md) · [component](component.md)

`alerts` next to its siblings in `cloud`, opened up 3 level(s) down. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

```mermaid
flowchart LR
  subgraph u_cloud["cloud"]
    u_cloud__platform["platform"]
    subgraph u_cloud__services__alerts["alerts"]
      u_cloud__services__alerts__notifier["notifier"]
      u_cloud__services__alerts__plant_dlookup["plant-lookup"]
      u_cloud__services__alerts__rules["rules"]
      u_cloud__services__alerts__server["server"]
    end
    u_cloud__services__gateway["gateway"]
    u_cloud__services__ingest["ingest"]
    u_cloud__services__plants["plants"]
  end
  n_cloud___push_dservice{{"push-service"}}
  u_cloud__services__gateway -->|"alerts-api"| u_cloud__services__alerts__server
  u_cloud__services__alerts__server -->|"reading-events"| u_cloud__services__ingest
  u_cloud__services__alerts__plant_dlookup -->|"plants-api"| u_cloud__services__plants
  u_cloud__services__alerts__notifier -->|"push → push-service"| n_cloud___push_dservice
  u_cloud__services__alerts__server -->|"event-bus, sql-db"| u_cloud__platform
  u_cloud__services__alerts__server -->|"evaluation"| u_cloud__services__alerts__rules
  u_cloud__services__alerts__server -->|"notification"| u_cloud__services__alerts__notifier
  u_cloud__services__alerts__rules -->|"thresholds"| u_cloud__services__alerts__plant_dlookup
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_cloud,u_cloud__platform,u_cloud__services__alerts,u_cloud__services__alerts__notifier,u_cloud__services__alerts__plant_dlookup,u_cloud__services__alerts__rules,u_cloud__services__alerts__server,u_cloud__services__gateway,u_cloud__services__ingest,u_cloud__services__plants planned
  class u_cloud__services__alerts focus
```

| Unit | Kind | Diagram |
|---|---|---|
| [cloud](../../../../README.md) | system | [component](../../../../doc/diagrams/component.md) |
| [platform](../../../../platform/README.md) | infrastructure | [context](../../../../platform/doc/diagrams/context.md) |
| [alerts](../../README.md) | service | [component](component.md) |
| [notifier](../../notifier/README.md) | adapter | [context](../../notifier/doc/diagrams/context.md) |
| [plant-lookup](../../plant-lookup/README.md) | adapter | [context](../../plant-lookup/doc/diagrams/context.md) |
| [rules](../../rules/README.md) | library | [context](../../rules/doc/diagrams/context.md) |
| [server](../../server/README.md) | app | [context](../../server/doc/diagrams/context.md) |
| [gateway](../../../gateway/README.md) | service | [context](../../../gateway/doc/diagrams/context.md) |
| [ingest](../../../ingest/README.md) | service | [context](../../../ingest/doc/diagrams/context.md) |
| [plants](../../../plants/README.md) | service | [context](../../../plants/doc/diagrams/context.md) |
