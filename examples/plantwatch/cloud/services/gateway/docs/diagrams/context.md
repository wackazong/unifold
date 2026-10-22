<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: gateway

[plantwatch](../../../../../docs/diagrams/component.md) / [cloud](../../../../docs/diagrams/component.md) / **gateway** · [README](../../README.md)

`gateway` inside `cloud`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_cloud["cloud"]
    u_cloud__services__alerts["alerts"]
    u_cloud__services__gateway["gateway"]
    u_cloud__services__ingest["ingest"]
    u_cloud__services__plants["plants"]
  end
  p_cloud___public_dapi(["public-api"])
  u_cloud__services__gateway -->|"ingest-api"| u_cloud__services__ingest
  u_cloud__services__gateway -->|"plants-api"| u_cloud__services__plants
  u_cloud__services__gateway -->|"alerts-api"| u_cloud__services__alerts
  p_cloud___public_dapi --> u_cloud__services__gateway
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud__services__alerts,u_cloud__services__gateway,u_cloud__services__ingest,u_cloud__services__plants planned
  class u_cloud__services__gateway focus
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [alerts](../../../alerts/README.md) | service | Decides when a plant needs attention and notifies its owner once | **planned** | [component](../../../alerts/docs/diagrams/component.md) |
| [gateway](../../README.md) | service | Single entry point of the server side that authenticates callers and routes requests | **planned** | [context](context.md) |
| [ingest](../../../ingest/README.md) | service | Accepts uploaded readings and announces each accepted one as an event | **planned** | [context](../../../ingest/docs/diagrams/context.md) |
| [plants](../../../plants/README.md) | service | Registry of plants with their sensors, thresholds and reading history | **planned** | [context](../../../plants/docs/diagrams/context.md) |

### Who provides what this unit needs

| Need | Kind | Own contract | Provided by | Capability | Their contract | Verified by |
|---|---|---|---|---|---|---|
| ingest-api | http |  | [cloud/services/ingest](../../../ingest/README.md) (planned) | ingest-api | [contract](../../../ingest/docs/references/ingest-api.md) |  |
| plants-api | http |  | [cloud/services/plants](../../../plants/README.md) (planned) | plants-api | [contract](../../../plants/docs/references/plants-api.md) |  |
| alerts-api | http |  | [cloud/services/alerts/server](../../../alerts/server/README.md) (planned) | alerts-api |  |  |

### Who uses what this unit provides

| Capability | Kind | Contract | Verified by | Used by | As need | Their contract |
|---|---|---|---|---|---|---|
| public-api | http | [contract](../references/public-api.md) |  | [mobile/sync](../../../../../mobile/sync/README.md) (planned) | cloud-api |  |
| public-api | http | [contract](../references/public-api.md) |  | [test-rig](../../../../../test-rig/README.md) (planned) | cloud-api |  |
