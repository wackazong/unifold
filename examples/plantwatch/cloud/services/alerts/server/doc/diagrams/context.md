<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: server

[plantwatch](../../../../../../doc/diagrams/component.md) / [cloud](../../../../../doc/diagrams/component.md) / [alerts](../../../doc/diagrams/component.md) / **server** · [README](../../README.md)

`server` among its siblings inside `alerts`. Only connections that touch `server` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

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
  n_cloud__services__alerts___sql_ddb{{"sql-db"}}
  n_cloud__services__alerts___event_dbus{{"event-bus"}}
  p_cloud__services__alerts___alerts_dapi --> u_cloud__services__alerts__server
  u_cloud__services__alerts__server -->|"reading-events"| n_cloud__services__alerts___reading_devents
  u_cloud__services__alerts__server -->|"evaluation"| u_cloud__services__alerts__rules
  u_cloud__services__alerts__server -->|"notification"| u_cloud__services__alerts__notifier
  u_cloud__services__alerts__server -->|"sql-db"| n_cloud__services__alerts___sql_ddb
  u_cloud__services__alerts__server -->|"event-bus"| n_cloud__services__alerts___event_dbus
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_cloud__services__alerts,u_cloud__services__alerts__notifier,u_cloud__services__alerts__plant_dlookup,u_cloud__services__alerts__rules,u_cloud__services__alerts__server planned
  class u_cloud__services__alerts__server focus
```

| Unit | Kind | Diagram |
|---|---|---|
| [alerts](../../../README.md) | service | [component](../../../doc/diagrams/component.md) |
| [notifier](../../../notifier/README.md) | adapter | [context](../../../notifier/doc/diagrams/context.md) |
| [plant-lookup](../../../plant-lookup/README.md) | adapter | [context](../../../plant-lookup/doc/diagrams/context.md) |
| [rules](../../../rules/README.md) | library | [context](../../../rules/doc/diagrams/context.md) |
| [server](../../README.md) | app | [context](context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Port | Their contract |
|---|---|---|---|---|---|
| reading-events | events | [contract](../references/reading-events.md) | [cloud/services/ingest](../../../../ingest/README.md) | reading-events | [contract](../../../../ingest/doc/references/reading-events.md) |
| evaluation | library | [contract](../references/evaluation.md) | [cloud/services/alerts/rules](../../../rules/README.md) | evaluation | [contract](../../../rules/doc/references/evaluation.md) |
| notification | library | [contract](../references/notification.md) | [cloud/services/alerts/notifier](../../../notifier/README.md) | notification | [contract](../../../notifier/doc/references/notification.md) |
| sql-db | db |  | [cloud/platform](../../../../../platform/README.md) | sql-db | [contract](../../../../../platform/doc/references/sql-db.md) |
| event-bus | queue |  | [cloud/platform](../../../../../platform/README.md) | event-bus | [contract](../../../../../platform/doc/references/event-bus.md) |

### Who uses what this unit provides

| Port | Kind | Used by | As need | Their contract |
|---|---|---|---|---|
| alerts-api | http | [cloud/services/gateway](../../../../gateway/README.md) | alerts-api |  |
