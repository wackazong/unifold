<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Architecture diagram: plantwatch

**plantwatch** · [README](../../README.md) · [context](context.md) · [component](component.md)

`plantwatch`, opened up 3 level(s) down. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    subgraph u_cloud["cloud"]
      u_cloud__platform["platform"]
      subgraph u_cloud__services__alerts["alerts"]
        u_cloud__services__alerts__notifier["notifier"]
        u_cloud__services__alerts__plant_dlookup["plant-lookup"]
        u_cloud__services__alerts__rules["rules"]
        u_cloud__services__alerts__server["server"]
      end
      u_cloud__services__gateway["gateway"]
      u_cloud__services__ingest["ingest"]
      u_cloud__services__plants["plants"]
    end
    subgraph u_device["device"]
      u_device__hal["hal"]
      u_device__link["link"]
      u_device__sampling["sampling"]
      u_device__store["store"]
    end
    u_emulator["emulator"]
    subgraph u_mobile["mobile"]
      u_mobile__ble_dclient["ble-client"]
      u_mobile__sync["sync"]
      u_mobile__ui["ui"]
    end
    u_protocol["protocol"]
    u_test_drig["test-rig"]
  end
  p_root___app_dui(["app-ui"])
  p_root___test_dreport(["test-report"])
  n_root___soil_dprobe{{"soil-probe"}}
  n_root___ambient_dsensor{{"ambient-sensor"}}
  n_root___push_dservice{{"push-service"}}
  n_root___container_dhost{{"container-host"}}
  p_root___app_dui --> u_mobile__ui
  p_root___test_dreport --> u_test_drig
  u_device__hal -->|"soil-probe"| n_root___soil_dprobe
  u_device__hal -->|"ambient-sensor"| n_root___ambient_dsensor
  u_mobile__ble_dclient -->|"sensor-link → ble-link (real)"| u_device__link
  u_mobile__ble_dclient -.->|"sensor-link → ble-link (simulated)"| u_emulator
  u_mobile__sync -->|"cloud-api → public-api"| u_cloud__services__gateway
  u_mobile__ui -->|"push-service"| n_root___push_dservice
  u_cloud__services__alerts__notifier -->|"push-service"| n_root___push_dservice
  u_cloud__platform -->|"container-host"| n_root___container_dhost
  u_test_drig -->|"device-under-test → ble-link (real)"| u_device__link
  u_test_drig -.->|"device-under-test → ble-link (simulated)"| u_emulator
  u_test_drig -->|"scenario-control"| u_emulator
  u_test_drig -->|"cloud-api → public-api"| u_cloud__services__gateway
  u_device__link -->|"link-profile → ble-profile"| u_protocol
  u_emulator -->|"link-profile → ble-profile"| u_protocol
  u_mobile__ble_dclient -->|"link-profile → ble-profile"| u_protocol
  u_test_drig -->|"link-profile → ble-profile, reading-format → reading-schema"| u_protocol
  u_cloud__services__ingest -->|"reading-format → reading-schema"| u_protocol
  u_mobile__sync -->|"reading-format → reading-schema"| u_protocol
  u_cloud__services__gateway -->|"ingest-api"| u_cloud__services__ingest
  u_cloud__services__gateway -->|"plants-api"| u_cloud__services__plants
  u_cloud__services__gateway -->|"alerts-api"| u_cloud__services__alerts__server
  u_cloud__services__plants -->|"reading-events"| u_cloud__services__ingest
  u_cloud__services__alerts__server -->|"reading-events"| u_cloud__services__ingest
  u_cloud__services__alerts__plant_dlookup -->|"plants-api"| u_cloud__services__plants
  u_cloud__services__alerts__server -->|"event-bus, sql-db"| u_cloud__platform
  u_cloud__services__ingest -->|"event-bus"| u_cloud__platform
  u_cloud__services__plants -->|"event-bus, sql-db"| u_cloud__platform
  u_cloud__services__alerts__server -->|"evaluation"| u_cloud__services__alerts__rules
  u_cloud__services__alerts__server -->|"notification"| u_cloud__services__alerts__notifier
  u_cloud__services__alerts__rules -->|"thresholds"| u_cloud__services__alerts__plant_dlookup
  u_device__sampling -->|"sensor-io, timer"| u_device__hal
  u_device__store -->|"flash"| u_device__hal
  u_device__store -->|"readings"| u_device__sampling
  u_device__link -->|"radio"| u_device__hal
  u_device__link -->|"reading-log"| u_device__store
  u_device__link -->|"live-readings → readings"| u_device__sampling
  u_mobile__sync -->|"sensor-readings"| u_mobile__ble_dclient
  u_mobile__ui -->|"plant-data"| u_mobile__sync
  u_mobile__ui -->|"pairing"| u_mobile__ble_dclient
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_root,u_cloud,u_cloud__platform,u_cloud__services__alerts,u_cloud__services__alerts__notifier,u_cloud__services__alerts__plant_dlookup,u_cloud__services__alerts__rules,u_cloud__services__alerts__server,u_cloud__services__gateway,u_cloud__services__ingest,u_cloud__services__plants,u_device,u_device__hal,u_device__link,u_device__sampling,u_device__store,u_emulator,u_mobile,u_mobile__ble_dclient,u_mobile__sync,u_mobile__ui,u_protocol,u_test_drig planned
```

| Unit | Kind | Diagram |
|---|---|---|
| [plantwatch](../../README.md) | system | [component](component.md) |
| [cloud](../../cloud/README.md) | system | [component](../../cloud/doc/diagrams/component.md) |
| [platform](../../cloud/platform/README.md) | infrastructure | [context](../../cloud/platform/doc/diagrams/context.md) |
| [alerts](../../cloud/services/alerts/README.md) | service | [component](../../cloud/services/alerts/doc/diagrams/component.md) |
| [notifier](../../cloud/services/alerts/notifier/README.md) | adapter | [context](../../cloud/services/alerts/notifier/doc/diagrams/context.md) |
| [plant-lookup](../../cloud/services/alerts/plant-lookup/README.md) | adapter | [context](../../cloud/services/alerts/plant-lookup/doc/diagrams/context.md) |
| [rules](../../cloud/services/alerts/rules/README.md) | library | [context](../../cloud/services/alerts/rules/doc/diagrams/context.md) |
| [server](../../cloud/services/alerts/server/README.md) | app | [context](../../cloud/services/alerts/server/doc/diagrams/context.md) |
| [gateway](../../cloud/services/gateway/README.md) | service | [context](../../cloud/services/gateway/doc/diagrams/context.md) |
| [ingest](../../cloud/services/ingest/README.md) | service | [context](../../cloud/services/ingest/doc/diagrams/context.md) |
| [plants](../../cloud/services/plants/README.md) | service | [context](../../cloud/services/plants/doc/diagrams/context.md) |
| [device](../../device/README.md) | firmware | [component](../../device/doc/diagrams/component.md) |
| [hal](../../device/hal/README.md) | library | [context](../../device/hal/doc/diagrams/context.md) |
| [link](../../device/link/README.md) | library | [context](../../device/link/doc/diagrams/context.md) |
| [sampling](../../device/sampling/README.md) | library | [context](../../device/sampling/doc/diagrams/context.md) |
| [store](../../device/store/README.md) | library | [context](../../device/store/doc/diagrams/context.md) |
| [emulator](../../emulator/README.md) | tool | [context](../../emulator/doc/diagrams/context.md) |
| [mobile](../../mobile/README.md) | app | [component](../../mobile/doc/diagrams/component.md) |
| [ble-client](../../mobile/ble-client/README.md) | library | [context](../../mobile/ble-client/doc/diagrams/context.md) |
| [sync](../../mobile/sync/README.md) | library | [context](../../mobile/sync/doc/diagrams/context.md) |
| [ui](../../mobile/ui/README.md) | library | [context](../../mobile/ui/doc/diagrams/context.md) |
| [protocol](../../protocol/README.md) | specification | [context](../../protocol/doc/diagrams/context.md) |
| [test-rig](../../test-rig/README.md) | test | [context](../../test-rig/doc/diagrams/context.md) |
