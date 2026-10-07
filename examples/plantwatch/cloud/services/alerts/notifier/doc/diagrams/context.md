<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: notifier

[plantwatch](../../../../../../doc/diagrams/component.md) / [cloud](../../../../../doc/diagrams/component.md) / [alerts](../../../doc/diagrams/component.md) / **notifier** · [README](../../README.md)

`notifier` among its siblings inside `alerts`. Only connections that touch `notifier` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

```mermaid
flowchart LR
  subgraph u_cloud__services__alerts["alerts"]
    u_cloud__services__alerts__notifier["notifier"]
    u_cloud__services__alerts__plant_dlookup["plant-lookup"]
    u_cloud__services__alerts__rules["rules"]
    u_cloud__services__alerts__server["server"]
  end
  n_cloud__services__alerts___push{{"push"}}
  u_cloud__services__alerts__server -->|"notification"| u_cloud__services__alerts__notifier
  u_cloud__services__alerts__notifier -->|"push"| n_cloud__services__alerts___push
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_cloud__services__alerts,u_cloud__services__alerts__notifier,u_cloud__services__alerts__plant_dlookup,u_cloud__services__alerts__rules,u_cloud__services__alerts__server planned
  class u_cloud__services__alerts__notifier focus
```

| Unit | Kind | Diagram |
|---|---|---|
| [alerts](../../../README.md) | service | [component](../../../doc/diagrams/component.md) |
| [notifier](../../README.md) | adapter | [context](context.md) |
| [plant-lookup](../../../plant-lookup/README.md) | adapter | [context](../../../plant-lookup/doc/diagrams/context.md) |
| [rules](../../../rules/README.md) | library | [context](../../../rules/doc/diagrams/context.md) |
| [server](../../../server/README.md) | app | [context](../../../server/doc/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Port | Their contract |
|---|---|---|---|---|---|
| push | http |  | outside the project, as need `push-service` of the root | | |

### Who uses what this unit provides

| Port | Kind | Used by | As need | Their contract |
|---|---|---|---|---|
| notification | library | [cloud/services/alerts/server](../../../server/README.md) | notification | [contract](../../../server/doc/references/notification.md) |
