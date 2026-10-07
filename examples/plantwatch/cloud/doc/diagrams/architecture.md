<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Architecture diagram: cloud

[plantwatch](../../../doc/diagrams/component.md) / **cloud** · [README](../../README.md) · [context](context.md) · [component](component.md)

`cloud` next to its siblings in `plantwatch`, opened up 3 level(s) down. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
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
    u_device["device"]
    u_emulator["emulator"]
    u_mobile["mobile"]
    u_protocol["protocol"]
    u_test_drig["test-rig"]
  end
  n_root___push_dservice{{"push-service"}}
  n_root___container_dhost{{"container-host"}}
  u_mobile -->|"cloud-api → public-api"| u_cloud__services__gateway
  u_cloud__services__alerts__notifier -->|"push-service"| n_root___push_dservice
  u_cloud__platform -->|"container-host"| n_root___container_dhost
  u_test_drig -->|"cloud-api → public-api"| u_cloud__services__gateway
  u_cloud__services__ingest -->|"reading-format → reading-schema"| u_protocol
  u_cloud__services__gateway -->|"ingest-api"| u_cloud__services__ingest
  u_cloud__services__gateway -->|"plants-api"| u_cloud__services__plants
  u_cloud__services__gateway -->|"alerts-api"| u_cloud__services__alerts__server
  u_cloud__services__plants -->|"reading-events"| u_cloud__services__ingest
  u_cloud__services__alerts__server -->|"reading-events"| u_cloud__services__ingest
  u_cloud__services__alerts__plant_dlookup -->|"plants-api"| u_cloud__services__plants
  u_cloud__services__alerts__server -->|"event-bus, sql-db"| u_cloud__platform
  u_cloud__services__ingest -->|"event-bus"| u_cloud__platform
  u_cloud__services__plants -->|"event-bus, sql-db"| u_cloud__platform
  u_cloud__services__alerts__server -->|"evaluation"| u_cloud__services__alerts__rules
  u_cloud__services__alerts__server -->|"notification"| u_cloud__services__alerts__notifier
  u_cloud__services__alerts__rules -->|"thresholds"| u_cloud__services__alerts__plant_dlookup
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_root,u_cloud,u_cloud__platform,u_cloud__services__alerts,u_cloud__services__alerts__notifier,u_cloud__services__alerts__plant_dlookup,u_cloud__services__alerts__rules,u_cloud__services__alerts__server,u_cloud__services__gateway,u_cloud__services__ingest,u_cloud__services__plants,u_device,u_emulator,u_mobile,u_protocol,u_test_drig planned
  class u_cloud focus
```

| Unit | Kind | Diagram |
|---|---|---|
| [plantwatch](../../../README.md) | system | [component](../../../doc/diagrams/component.md) |
| [cloud](../../README.md) | system | [component](component.md) |
| [platform](../../platform/README.md) | infrastructure | [context](../../platform/doc/diagrams/context.md) |
| [alerts](../../services/alerts/README.md) | service | [component](../../services/alerts/doc/diagrams/component.md) |
| [notifier](../../services/alerts/notifier/README.md) | adapter | [context](../../services/alerts/notifier/doc/diagrams/context.md) |
| [plant-lookup](../../services/alerts/plant-lookup/README.md) | adapter | [context](../../services/alerts/plant-lookup/doc/diagrams/context.md) |
| [rules](../../services/alerts/rules/README.md) | library | [context](../../services/alerts/rules/doc/diagrams/context.md) |
| [server](../../services/alerts/server/README.md) | app | [context](../../services/alerts/server/doc/diagrams/context.md) |
| [gateway](../../services/gateway/README.md) | service | [context](../../services/gateway/doc/diagrams/context.md) |
| [ingest](../../services/ingest/README.md) | service | [context](../../services/ingest/doc/diagrams/context.md) |
| [plants](../../services/plants/README.md) | service | [context](../../services/plants/doc/diagrams/context.md) |
| [device](../../../device/README.md) | firmware | [component](../../../device/doc/diagrams/component.md) |
| [emulator](../../../emulator/README.md) | tool | [context](../../../emulator/doc/diagrams/context.md) |
| [mobile](../../../mobile/README.md) | app | [component](../../../mobile/doc/diagrams/component.md) |
| [protocol](../../../protocol/README.md) | specification | [context](../../../protocol/doc/diagrams/context.md) |
| [test-rig](../../../test-rig/README.md) | test | [context](../../../test-rig/doc/diagrams/context.md) |
