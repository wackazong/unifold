<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Architecture diagram: plantwatch

[plantwatch](../../README.md) · [context](context.md) · [component](component.md)

`plantwatch`, opened up to 3 level(s) down. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    subgraph u_cloud["cloud"]
      u_cloud_platform["platform"]
      subgraph u_cloud_services_alerts["alerts"]
        u_cloud_services_alerts_notifier["notifier"]
        u_cloud_services_alerts_rules["rules"]
        u_cloud_services_alerts_server["server"]
      end
      u_cloud_services_gateway["gateway"]
      u_cloud_services_ingest["ingest"]
      u_cloud_services_plants["plants"]
    end
    subgraph u_device["device"]
      u_device_hal["hal"]
      u_device_link["link"]
      u_device_sampling["sampling"]
      u_device_store["store"]
    end
    u_emulator["emulator"]
    subgraph u_mobile["mobile"]
      u_mobile_ble_client["ble-client"]
      u_mobile_sync["sync"]
      u_mobile_ui["ui"]
    end
    u_protocol["protocol"]
    u_test_rig["test-rig"]
  end
  p_root_app_ui(["app-ui"])
  p_root_test_report(["test-report"])
  n_root_soil_probe{{"soil-probe"}}
  n_root_ambient_sensor{{"ambient-sensor"}}
  n_root_push_service{{"push-service"}}
  n_root_container_host{{"container-host"}}
  p_root_app_ui --> u_mobile_ui
  p_root_test_report --> u_test_rig
  u_device_hal -->|"soil-probe"| n_root_soil_probe
  u_device_hal -->|"ambient-sensor"| n_root_ambient_sensor
  u_device_link -->|"link-profile → ble-profile"| u_protocol
  u_emulator -->|"link-profile → ble-profile"| u_protocol
  u_mobile_ble_client -->|"link-profile → ble-profile"| u_protocol
  u_mobile_sync -->|"reading-format → reading-schema"| u_protocol
  u_mobile_ble_client -.->|"sensor-link → ble-link"| u_device_link
  u_mobile_ble_client -.->|"sensor-link → ble-link"| u_emulator
  u_mobile_sync -->|"cloud-api → public-api"| u_cloud_services_gateway
  u_mobile_ui -->|"push-service"| n_root_push_service
  u_cloud_services_ingest -->|"reading-format → reading-schema"| u_protocol
  u_cloud_services_alerts_notifier -->|"push-service"| n_root_push_service
  u_cloud_platform -->|"container-host"| n_root_container_host
  u_test_rig -.->|"device-under-test → ble-link"| u_device_link
  u_test_rig -.->|"device-under-test → ble-link"| u_emulator
  u_test_rig -->|"scenario-control"| u_emulator
  u_test_rig -->|"cloud-api → public-api"| u_cloud_services_gateway
  u_test_rig -->|"link-profile → ble-profile"| u_protocol
  u_test_rig -->|"reading-format → reading-schema"| u_protocol
  u_cloud_services_gateway -->|"ingest-api"| u_cloud_services_ingest
  u_cloud_services_gateway -->|"plants-api"| u_cloud_services_plants
  u_cloud_services_gateway -->|"alerts-api"| u_cloud_services_alerts_server
  u_cloud_services_ingest -->|"event-bus"| u_cloud_platform
  u_cloud_services_plants -->|"reading-events"| u_cloud_services_ingest
  u_cloud_services_plants -->|"sql-db"| u_cloud_platform
  u_cloud_services_plants -->|"event-bus"| u_cloud_platform
  u_cloud_services_alerts_server -->|"reading-events"| u_cloud_services_ingest
  u_cloud_services_alerts_rules -->|"plants-api"| u_cloud_services_plants
  u_cloud_services_alerts_server -->|"sql-db"| u_cloud_platform
  u_cloud_services_alerts_server -->|"event-bus"| u_cloud_platform
  u_cloud_services_alerts_server -->|"evaluation"| u_cloud_services_alerts_rules
  u_cloud_services_alerts_server -->|"notification"| u_cloud_services_alerts_notifier
  u_device_sampling -->|"sensor-io"| u_device_hal
  u_device_sampling -->|"timer"| u_device_hal
  u_device_store -->|"flash"| u_device_hal
  u_device_store -->|"readings"| u_device_sampling
  u_device_link -->|"radio"| u_device_hal
  u_device_link -->|"reading-log"| u_device_store
  u_device_link -->|"live-readings → readings"| u_device_sampling
  u_mobile_sync -->|"sensor-readings"| u_mobile_ble_client
  u_mobile_ui -->|"plant-data"| u_mobile_sync
  u_mobile_ui -->|"pairing"| u_mobile_ble_client
  click u_cloud_platform href "../../cloud/platform/README.md"
  click u_cloud_services_alerts_notifier href "../../cloud/services/alerts/notifier/README.md"
  click u_cloud_services_alerts_rules href "../../cloud/services/alerts/rules/README.md"
  click u_cloud_services_alerts_server href "../../cloud/services/alerts/server/README.md"
  click u_cloud_services_gateway href "../../cloud/services/gateway/README.md"
  click u_cloud_services_ingest href "../../cloud/services/ingest/README.md"
  click u_cloud_services_plants href "../../cloud/services/plants/README.md"
  click u_device_hal href "../../device/hal/README.md"
  click u_device_link href "../../device/link/README.md"
  click u_device_sampling href "../../device/sampling/README.md"
  click u_device_store href "../../device/store/README.md"
  click u_emulator href "../../emulator/README.md"
  click u_mobile_ble_client href "../../mobile/ble-client/README.md"
  click u_mobile_sync href "../../mobile/sync/README.md"
  click u_mobile_ui href "../../mobile/ui/README.md"
  click u_protocol href "../../protocol/README.md"
  click u_test_rig href "../../test-rig/README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_root,u_cloud,u_cloud_platform,u_cloud_services_alerts,u_cloud_services_alerts_notifier,u_cloud_services_alerts_rules,u_cloud_services_alerts_server,u_cloud_services_gateway,u_cloud_services_ingest,u_cloud_services_plants,u_device,u_device_hal,u_device_link,u_device_sampling,u_device_store,u_emulator,u_mobile,u_mobile_ble_client,u_mobile_sync,u_mobile_ui,u_protocol,u_test_rig planned
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [plantwatch](../../README.md) | Tells people when their house plants need water, using a sensor in the pot, a phone app and cloud services | planned | [component](component.md) |
| [cloud](../../cloud/README.md) | Server side that stores readings, keeps the plant registry and raises alerts | planned | [component](../../cloud/doc/diagrams/component.md) |
| [platform](../../cloud/platform/README.md) | Shared infrastructure of the services - message bus and database | planned | [context](../../cloud/platform/doc/diagrams/context.md) |
| [alerts](../../cloud/services/alerts/README.md) | Decides when a plant needs attention and notifies its owner once | planned | [component](../../cloud/services/alerts/doc/diagrams/component.md) |
| [notifier](../../cloud/services/alerts/notifier/README.md) | Turns an opened alert into one notification to the owner | planned | [context](../../cloud/services/alerts/notifier/doc/diagrams/context.md) |
| [rules](../../cloud/services/alerts/rules/README.md) | Evaluates readings against the thresholds of a plant | planned | [context](../../cloud/services/alerts/rules/doc/diagrams/context.md) |
| [server](../../cloud/services/alerts/server/README.md) | Process of the alerts service - consumes readings, stores alerts and answers queries | planned | [context](../../cloud/services/alerts/server/doc/diagrams/context.md) |
| [gateway](../../cloud/services/gateway/README.md) | Single entry point of the server side that authenticates callers and routes requests | planned | [context](../../cloud/services/gateway/doc/diagrams/context.md) |
| [ingest](../../cloud/services/ingest/README.md) | Accepts uploaded readings, validates them and publishes each one once | planned | [context](../../cloud/services/ingest/doc/diagrams/context.md) |
| [plants](../../cloud/services/plants/README.md) | Registry of plants with their sensors, thresholds and reading history | planned | [context](../../cloud/services/plants/doc/diagrams/context.md) |
| [device](../../device/README.md) | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | planned | [component](../../device/doc/diagrams/component.md) |
| [hal](../../device/hal/README.md) | Hardware abstraction of the sensor stick board | planned | [context](../../device/hal/doc/diagrams/context.md) |
| [link](../../device/link/README.md) | Implements the BLE profile on top of the radio | planned | [context](../../device/link/doc/diagrams/context.md) |
| [sampling](../../device/sampling/README.md) | Takes a calibrated reading at every sampling interval | planned | [context](../../device/sampling/doc/diagrams/context.md) |
| [store](../../device/store/README.md) | Keeps readings on the device until they have been delivered | planned | [context](../../device/store/doc/diagrams/context.md) |
| [emulator](../../emulator/README.md) | Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware | planned | [context](../../emulator/doc/diagrams/context.md) |
| [mobile](../../mobile/README.md) | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | planned | [component](../../mobile/doc/diagrams/component.md) |
| [ble-client](../../mobile/ble-client/README.md) | Finds sensor sticks and fetches their readings over BLE | planned | [context](../../mobile/ble-client/doc/diagrams/context.md) |
| [sync](../../mobile/sync/README.md) | Keeps plants, history and alerts on the phone and in step with the server | planned | [context](../../mobile/sync/doc/diagrams/context.md) |
| [ui](../../mobile/ui/README.md) | Screens of the phone app | planned | [context](../../mobile/ui/doc/diagrams/context.md) |
| [protocol](../../protocol/README.md) | Defines the BLE profile of the sensor stick and the format of a reading | planned | [context](../../protocol/doc/diagrams/context.md) |
| [test-rig](../../test-rig/README.md) | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware | planned | [context](../../test-rig/doc/diagrams/context.md) |
