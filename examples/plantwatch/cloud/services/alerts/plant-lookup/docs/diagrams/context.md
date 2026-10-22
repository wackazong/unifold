<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: plant-lookup

[plantwatch](../../../../../../docs/diagrams/component.md) / [cloud](../../../../../docs/diagrams/component.md) / [alerts](../../../docs/diagrams/component.md) / **plant-lookup** · [README](../../README.md)

`plant-lookup` inside `alerts`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_cloud__services__alerts["alerts"]
    u_cloud__services__alerts__plant_dlookup["plant-lookup"]
    u_cloud__services__alerts__rules["rules"]
  end
  n_cloud__services__alerts___plants_dapi{{"plants-api"}}
  u_cloud__services__alerts__rules -->|"thresholds"| u_cloud__services__alerts__plant_dlookup
  u_cloud__services__alerts__plant_dlookup -->|"plants-api"| n_cloud__services__alerts___plants_dapi
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud__services__alerts__plant_dlookup,u_cloud__services__alerts__rules planned
  class u_cloud__services__alerts__plant_dlookup focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [plant-lookup](../../README.md) | adapter | Looks up the plant a sensor stick is attached to, with owner and thresholds, in the registry of plants | **planned** | [context](context.md) |
| [rules](../../../rules/README.md) | library | Evaluates readings against the thresholds of a plant | **planned** | [context](../../../rules/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Capability | Their contract | Verified by |
|---|---|---|---|---|---|---|
| plants-api | http |  | [cloud/services/plants](../../../../plants/README.md) (planned) (passed up by name) | plants-api | [contract](../../../../plants/docs/references/plants-api.md) |  |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need | Their contract |
|---|---|---|---|---|---|---|
| thresholds | library | [contract](../references/thresholds.md) |  | [cloud/services/alerts/rules](../../../rules/README.md) (planned) | thresholds | [contract](../../../rules/docs/references/thresholds.md) |
