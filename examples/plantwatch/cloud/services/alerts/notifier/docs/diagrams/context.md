<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: notifier

[plantwatch](../../../../../../docs/diagrams/component.md) / [cloud](../../../../../docs/diagrams/component.md) / [alerts](../../../docs/diagrams/component.md) / **notifier** · [README](../../README.md)

`notifier` inside `alerts`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_cloud__services__alerts["alerts"]
    u_cloud__services__alerts__notifier["notifier"]
    u_cloud__services__alerts__server["server"]
  end
  n_cloud__services__alerts___push{{"push"}}
  u_cloud__services__alerts__server -->|"notification"| u_cloud__services__alerts__notifier
  u_cloud__services__alerts__notifier -->|"push"| n_cloud__services__alerts___push
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud__services__alerts__notifier,u_cloud__services__alerts__server planned
  class u_cloud__services__alerts__notifier focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [notifier](../../README.md) | adapter | Turns an opened alert into one notification to the owner | **planned** | [context](context.md) |
| [server](../../../server/README.md) | app | Process that consumes readings, stores the alerts they lead to and answers queries about them | **planned** | [context](../../../server/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability | Verified by |
|---|---|---|---|---|---|
| push | http | [contract](../../../../../../docs/references/push-service.md) | outside the project, as need `push-service` of the root | | |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need |
|---|---|---|---|---|---|
| notification | library | [contract](../../../docs/references/notification.md) |  | [cloud/services/alerts/server](../../../server/README.md) (planned) | notification |
