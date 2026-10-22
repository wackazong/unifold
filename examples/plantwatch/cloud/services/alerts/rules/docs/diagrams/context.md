<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: rules

[plantwatch](../../../../../../docs/diagrams/component.md) / [cloud](../../../../../docs/diagrams/component.md) / [alerts](../../../docs/diagrams/component.md) / **rules** · [README](../../README.md)

`rules` inside `alerts`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_cloud__services__alerts["alerts"]
    u_cloud__services__alerts__plant_dlookup["plant-lookup"]
    u_cloud__services__alerts__rules["rules"]
    u_cloud__services__alerts__server["server"]
  end
  u_cloud__services__alerts__server -->|"evaluation"| u_cloud__services__alerts__rules
  u_cloud__services__alerts__rules -->|"thresholds"| u_cloud__services__alerts__plant_dlookup
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud__services__alerts__plant_dlookup,u_cloud__services__alerts__rules,u_cloud__services__alerts__server planned
  class u_cloud__services__alerts__rules focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [plant-lookup](../../../plant-lookup/README.md) | adapter | Looks up the plant a sensor stick is attached to, with owner and thresholds, in the registry of plants | **planned** | [context](../../../plant-lookup/docs/diagrams/context.md) |
| [rules](../../README.md) | library | Evaluates readings against the thresholds of a plant | **planned** | [context](context.md) |
| [server](../../../server/README.md) | app | Process that consumes readings, stores the alerts they lead to and answers queries about them | **planned** | [context](../../../server/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability | Verified by |
|---|---|---|---|---|---|
| thresholds | library | [contract](../../../docs/references/thresholds.md) | [cloud/services/alerts/plant-lookup](../../../plant-lookup/README.md) (planned) | thresholds |  |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need |
|---|---|---|---|---|---|
| evaluation | library | [contract](../../../docs/references/evaluation.md) |  | [cloud/services/alerts/server](../../../server/README.md) (planned) | evaluation |
