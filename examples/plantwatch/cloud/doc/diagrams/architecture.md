<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Architecture diagram: cloud

[cloud](../../README.md) · [context](context.md) · [component](component.md)

`cloud` next to its siblings in `plantwatch`, opened up to 3 level(s) down. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    subgraph u_cloud["cloud"]
      u_cloud_platform["platform"]
      subgraph u_cloud_services_alerts["alerts"]
        u_cloud_services_alerts_notifier["notifier"]
        u_cloud_services_alerts_rules["rules"]
        u_cloud_services_alerts_server["server"]
      end
      u_cloud_services_gateway["gateway"]
      u_cloud_services_ingest["ingest"]
      u_cloud_services_plants["plants"]
    end
    u_device["device"]
    u_emulator["emulator"]
    u_mobile["mobile"]
    u_protocol["protocol"]
    u_test_rig["test-rig"]
  end
  n_root_push_service{{"push-service"}}
  n_root_container_host{{"container-host"}}
  u_mobile -->|"cloud-api → public-api"| u_cloud_services_gateway
  u_cloud_services_ingest -->|"reading-format → reading-schema"| u_protocol
  u_cloud_services_alerts_notifier -->|"push-service"| n_root_push_service
  u_cloud_platform -->|"container-host"| n_root_container_host
  u_test_rig -->|"cloud-api → public-api"| u_cloud_services_gateway
  u_cloud_services_gateway -->|"ingest-api"| u_cloud_services_ingest
  u_cloud_services_gateway -->|"plants-api"| u_cloud_services_plants
  u_cloud_services_gateway -->|"alerts-api"| u_cloud_services_alerts_server
  u_cloud_services_ingest -->|"event-bus"| u_cloud_platform
  u_cloud_services_plants -->|"reading-events"| u_cloud_services_ingest
  u_cloud_services_plants -->|"sql-db"| u_cloud_platform
  u_cloud_services_plants -->|"event-bus"| u_cloud_platform
  u_cloud_services_alerts_server -->|"reading-events"| u_cloud_services_ingest
  u_cloud_services_alerts_rules -->|"plants-api"| u_cloud_services_plants
  u_cloud_services_alerts_server -->|"sql-db"| u_cloud_platform
  u_cloud_services_alerts_server -->|"event-bus"| u_cloud_platform
  u_cloud_services_alerts_server -->|"evaluation"| u_cloud_services_alerts_rules
  u_cloud_services_alerts_server -->|"notification"| u_cloud_services_alerts_notifier
  click u_cloud_platform href "../../platform/README.md"
  click u_cloud_services_alerts_notifier href "../../services/alerts/notifier/README.md"
  click u_cloud_services_alerts_rules href "../../services/alerts/rules/README.md"
  click u_cloud_services_alerts_server href "../../services/alerts/server/README.md"
  click u_cloud_services_gateway href "../../services/gateway/README.md"
  click u_cloud_services_ingest href "../../services/ingest/README.md"
  click u_cloud_services_plants href "../../services/plants/README.md"
  click u_device href "../../../device/README.md"
  click u_emulator href "../../../emulator/README.md"
  click u_mobile href "../../../mobile/README.md"
  click u_protocol href "../../../protocol/README.md"
  click u_test_rig href "../../../test-rig/README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_root,u_cloud,u_cloud_platform,u_cloud_services_alerts,u_cloud_services_alerts_notifier,u_cloud_services_alerts_rules,u_cloud_services_alerts_server,u_cloud_services_gateway,u_cloud_services_ingest,u_cloud_services_plants,u_device,u_emulator,u_mobile,u_protocol,u_test_rig planned
  class u_cloud focus
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [plantwatch](../../../README.md) | Tells people when their house plants need water, using a sensor in the pot, a phone app and cloud services | planned | [component](../../../doc/diagrams/component.md) |
| [cloud](../../README.md) | Server side that stores readings, keeps the plant registry and raises alerts | planned | [component](component.md) |
| [platform](../../platform/README.md) | Shared infrastructure of the services - message bus and database | planned | [context](../../platform/doc/diagrams/context.md) |
| [alerts](../../services/alerts/README.md) | Decides when a plant needs attention and notifies its owner once | planned | [component](../../services/alerts/doc/diagrams/component.md) |
| [notifier](../../services/alerts/notifier/README.md) | Turns an opened alert into one notification to the owner | planned | [context](../../services/alerts/notifier/doc/diagrams/context.md) |
| [rules](../../services/alerts/rules/README.md) | Evaluates readings against the thresholds of a plant | planned | [context](../../services/alerts/rules/doc/diagrams/context.md) |
| [server](../../services/alerts/server/README.md) | Process of the alerts service - consumes readings, stores alerts and answers queries | planned | [context](../../services/alerts/server/doc/diagrams/context.md) |
| [gateway](../../services/gateway/README.md) | Single entry point of the server side that authenticates callers and routes requests | planned | [context](../../services/gateway/doc/diagrams/context.md) |
| [ingest](../../services/ingest/README.md) | Accepts uploaded readings, validates them and publishes each one once | planned | [context](../../services/ingest/doc/diagrams/context.md) |
| [plants](../../services/plants/README.md) | Registry of plants with their sensors, thresholds and reading history | planned | [context](../../services/plants/doc/diagrams/context.md) |
| [device](../../../device/README.md) | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | planned | [component](../../../device/doc/diagrams/component.md) |
| [emulator](../../../emulator/README.md) | Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware | planned | [context](../../../emulator/doc/diagrams/context.md) |
| [mobile](../../../mobile/README.md) | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | planned | [component](../../../mobile/doc/diagrams/component.md) |
| [protocol](../../../protocol/README.md) | Defines the BLE profile of the sensor stick and the format of a reading | planned | [context](../../../protocol/doc/diagrams/context.md) |
| [test-rig](../../../test-rig/README.md) | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware | planned | [context](../../../test-rig/doc/diagrams/context.md) |
