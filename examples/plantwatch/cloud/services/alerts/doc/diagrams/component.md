<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Component diagram: alerts

[plantwatch](../../../../../doc/diagrams/component.md) / [cloud](../../../../doc/diagrams/component.md) / **alerts** · [README](../../README.md) · [context](context.md) · [architecture](architecture.md)

The units directly inside `alerts` and how they are wired. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

```mermaid
flowchart LR
  subgraph u_cloud__services__alerts["alerts"]
    u_cloud__services__alerts__notifier["notifier"]
    u_cloud__services__alerts__plant_dlookup["plant-lookup"]
    u_cloud__services__alerts__rules["rules"]
    u_cloud__services__alerts__server["server"]
  end
  p_cloud__services__alerts___alerts_dapi(["alerts-api"])
  n_cloud__services__alerts___reading_devents{{"reading-events"}}
  n_cloud__services__alerts___plants_dapi{{"plants-api"}}
  n_cloud__services__alerts___push{{"push"}}
  n_cloud__services__alerts___sql_ddb{{"sql-db"}}
  n_cloud__services__alerts___event_dbus{{"event-bus"}}
  p_cloud__services__alerts___alerts_dapi --> u_cloud__services__alerts__server
  u_cloud__services__alerts__server -->|"reading-events"| n_cloud__services__alerts___reading_devents
  u_cloud__services__alerts__server -->|"evaluation"| u_cloud__services__alerts__rules
  u_cloud__services__alerts__server -->|"notification"| u_cloud__services__alerts__notifier
  u_cloud__services__alerts__server -->|"sql-db"| n_cloud__services__alerts___sql_ddb
  u_cloud__services__alerts__server -->|"event-bus"| n_cloud__services__alerts___event_dbus
  u_cloud__services__alerts__rules -->|"thresholds"| u_cloud__services__alerts__plant_dlookup
  u_cloud__services__alerts__plant_dlookup -->|"plants-api"| n_cloud__services__alerts___plants_dapi
  u_cloud__services__alerts__notifier -->|"push"| n_cloud__services__alerts___push
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_cloud__services__alerts,u_cloud__services__alerts__notifier,u_cloud__services__alerts__plant_dlookup,u_cloud__services__alerts__rules,u_cloud__services__alerts__server planned
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [alerts](../../README.md) | service | Decides when a plant needs attention and notifies its owner once | planned | [component](component.md) |
| [notifier](../../notifier/README.md) | adapter | Turns an opened alert into one notification to the owner | planned | [context](../../notifier/doc/diagrams/context.md) |
| [plant-lookup](../../plant-lookup/README.md) | adapter | Looks up the plant a sensor stick is attached to, with owner and thresholds, in the registry of plants | planned | [context](../../plant-lookup/doc/diagrams/context.md) |
| [rules](../../rules/README.md) | library | Evaluates readings against the thresholds of a plant | planned | [context](../../rules/doc/diagrams/context.md) |
| [server](../../server/README.md) | app | Process that consumes readings, stores the alerts they lead to and answers queries about them | planned | [context](../../server/doc/diagrams/context.md) |
