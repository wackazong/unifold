<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: change-a-threshold-offline

[plantwatch](../../../docs/diagrams/component.md) / **mobile** · [README](../../README.md) · [context](context.md) · [component](component.md)

**The owner changes a threshold without a network connection, and the change reaches the server later**
Source: decision 0001 of mobile
Expect: the screen shows the new value within 1 second, marked "not yet sent"; until the server has the new threshold, alerts follow the old one; after the next exchange the plant is `in step` and the mark is gone

A unit is named by its path from `mobile`; a capability or need of `mobile` is named bare. Every hop is a call along one connection of the map.

```mermaid
sequenceDiagram
  participant papp_dui as app-ui
  participant pui as ui
  participant psync as sync
  participant pcloud_dapi as cloud-api
  papp_dui->>pui: 1 · edit-plant
  pui->>psync: 2 · change-plant
  pui->>psync: 3 · plant
  psync->>pcloud_dapi: 4 · put-plant
  Note over papp_dui,pcloud_dapi: Expect: the screen shows the new value within 1 second, marked #quot;not yet sent#quot;; until the server has the new threshold, alerts follow the old one; after the next exchange the plant is `in step` and the mark is gone
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `app-ui` | `ui` | `edit-plant` | [app-ui](../../../docs/references/app-ui.md) |
| 2 | `ui` | `sync` | `change-plant` | [index](../references/plant-data/index.md) |
| 3 | `ui` | `sync` | `plant` | [index](../references/plant-data/index.md) |
| 4 | `sync` | `cloud-api` | `put-plant` | [index](../../../docs/references/public-api/index.md) |
