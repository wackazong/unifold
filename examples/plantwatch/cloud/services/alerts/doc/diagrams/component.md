<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Component diagram: alerts

[alerts](../../README.md) · [context](context.md) · [architecture](architecture.md)

The units directly inside `alerts` and how they are wired. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_cloud_services_alerts["alerts"]
    u_cloud_services_alerts_notifier["notifier"]
    u_cloud_services_alerts_rules["rules"]
    u_cloud_services_alerts_server["server"]
  end
  p_cloud_services_alerts_alerts_api(["alerts-api"])
  n_cloud_services_alerts_reading_events{{"reading-events"}}
  n_cloud_services_alerts_plants_api{{"plants-api"}}
  n_cloud_services_alerts_push{{"push"}}
  n_cloud_services_alerts_sql_db{{"sql-db"}}
  n_cloud_services_alerts_event_bus{{"event-bus"}}
  p_cloud_services_alerts_alerts_api --> u_cloud_services_alerts_server
  u_cloud_services_alerts_server -->|"reading-events"| n_cloud_services_alerts_reading_events
  u_cloud_services_alerts_server -->|"evaluation"| u_cloud_services_alerts_rules
  u_cloud_services_alerts_server -->|"notification"| u_cloud_services_alerts_notifier
  u_cloud_services_alerts_server -->|"sql-db"| n_cloud_services_alerts_sql_db
  u_cloud_services_alerts_server -->|"event-bus"| n_cloud_services_alerts_event_bus
  u_cloud_services_alerts_rules -->|"thresholds → plants-api"| n_cloud_services_alerts_plants_api
  u_cloud_services_alerts_notifier -->|"push"| n_cloud_services_alerts_push
  click u_cloud_services_alerts_notifier href "../../notifier/README.md"
  click u_cloud_services_alerts_rules href "../../rules/README.md"
  click u_cloud_services_alerts_server href "../../server/README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_cloud_services_alerts,u_cloud_services_alerts_notifier,u_cloud_services_alerts_rules,u_cloud_services_alerts_server planned
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [alerts](../../README.md) | Decides when a plant needs attention and notifies its owner once | planned | [component](component.md) |
| [notifier](../../notifier/README.md) | Turns an opened alert into one notification to the owner | planned | [context](../../notifier/doc/diagrams/context.md) |
| [rules](../../rules/README.md) | Evaluates readings against the thresholds of a plant | planned | [context](../../rules/doc/diagrams/context.md) |
| [server](../../server/README.md) | Process of the alerts service - consumes readings, stores alerts and answers queries | planned | [context](../../server/doc/diagrams/context.md) |
