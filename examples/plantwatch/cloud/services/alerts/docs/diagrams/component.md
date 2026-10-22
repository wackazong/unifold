<!-- unifold:generated - do not edit; run `unifold generate` -->
# Component diagram: alerts

[plantwatch](../../../../../docs/diagrams/component.md) / [cloud](../../../../docs/diagrams/component.md) / **alerts** · [README](../../README.md) · [context](context.md)

The units directly inside `alerts` and how they are connected. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_cloud__services__alerts["alerts"]
    u_cloud__services__alerts__notifier["notifier"]
    u_cloud__services__alerts__plant_dlookup["plant-lookup"]
    u_cloud__services__alerts__rules["rules"]
    u_cloud__services__alerts__server["server"]
  end
  n_cloud__services__alerts___push{{"push"}}
  n_cloud__services__alerts___plants_dapi{{"plants-api"}}
  n_cloud__services__alerts___reading_devents{{"reading-events"}}
  n_cloud__services__alerts___sql_ddb{{"sql-db"}}
  n_cloud__services__alerts___event_dbus{{"event-bus"}}
  p_cloud__services__alerts___alerts_dapi(["alerts-api"])
  u_cloud__services__alerts__server -->|"evaluation"| u_cloud__services__alerts__rules
  u_cloud__services__alerts__server -->|"notification"| u_cloud__services__alerts__notifier
  u_cloud__services__alerts__rules -->|"thresholds"| u_cloud__services__alerts__plant_dlookup
  u_cloud__services__alerts__notifier -->|"push"| n_cloud__services__alerts___push
  u_cloud__services__alerts__plant_dlookup -->|"plants-api"| n_cloud__services__alerts___plants_dapi
  u_cloud__services__alerts__server -->|"reading-events"| n_cloud__services__alerts___reading_devents
  u_cloud__services__alerts__server -->|"sql-db"| n_cloud__services__alerts___sql_ddb
  u_cloud__services__alerts__server -->|"event-bus"| n_cloud__services__alerts___event_dbus
  p_cloud__services__alerts___alerts_dapi --> u_cloud__services__alerts__server
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud__services__alerts__notifier,u_cloud__services__alerts__plant_dlookup,u_cloud__services__alerts__rules,u_cloud__services__alerts__server planned
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [notifier](../../notifier/README.md) | adapter | Turns an opened alert into one notification to the owner | **planned** | [context](../../notifier/docs/diagrams/context.md) |
| [plant-lookup](../../plant-lookup/README.md) | adapter | Looks up the plant a sensor stick is attached to, with owner and thresholds, in the registry of plants | **planned** | [context](../../plant-lookup/docs/diagrams/context.md) |
| [rules](../../rules/README.md) | library | Evaluates readings against the thresholds of a plant | **planned** | [context](../../rules/docs/diagrams/context.md) |
| [server](../../server/README.md) | app | Process that consumes readings, stores the alerts they lead to and answers queries about them | **planned** | [context](../../server/docs/diagrams/context.md) |

### Connections

| Need | Provider | Note |
|---|---|---|
| capability `alerts-api` of `alerts` | `server.alerts-api` | implemented by |
| `server.evaluation` | `rules.evaluation` |  |
| `server.notification` | `notifier.notification` |  |
| `rules.thresholds` | `plant-lookup.thresholds` |  |
| `notifier.push` | need `push` of `alerts` | passed up by name |
| `plant-lookup.plants-api` | need `plants-api` of `alerts` | passed up by name |
| `server.reading-events` | need `reading-events` of `alerts` | passed up by name |
| `server.sql-db` | need `sql-db` of `alerts` | passed up by name |
| `server.event-bus` | need `event-bus` of `alerts` | passed up by name |
