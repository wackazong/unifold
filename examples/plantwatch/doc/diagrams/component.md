<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Component diagram: plantwatch

**plantwatch** · [README](../../README.md) · [context](context.md) · [architecture](architecture.md)

The units directly inside `plantwatch` and how they are wired. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a planned unit.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    u_cloud["cloud"]
    u_device["device"]
    u_emulator["emulator"]
    u_mobile["mobile"]
    u_protocol["protocol"]
    u_test_drig["test-rig"]
  end
  p_root___app_dui(["app-ui"])
  p_root___test_dreport(["test-report"])
  n_root___soil_dprobe{{"soil-probe"}}
  n_root___ambient_dsensor{{"ambient-sensor"}}
  n_root___push_dservice{{"push-service"}}
  n_root___container_dhost{{"container-host"}}
  p_root___app_dui --> u_mobile
  p_root___test_dreport --> u_test_drig
  u_device -->|"soil-probe"| n_root___soil_dprobe
  u_device -->|"ambient-sensor"| n_root___ambient_dsensor
  u_mobile -->|"sensor-link → ble-link (real)"| u_device
  u_mobile -.->|"sensor-link → ble-link (simulated)"| u_emulator
  u_mobile -->|"cloud-api → public-api"| u_cloud
  u_mobile -->|"push-service"| n_root___push_dservice
  u_cloud -->|"push-service"| n_root___push_dservice
  u_cloud -->|"container-host"| n_root___container_dhost
  u_test_drig -->|"device-under-test → ble-link (real)"| u_device
  u_test_drig -.->|"device-under-test → ble-link (simulated)"| u_emulator
  u_test_drig -->|"scenario-control"| u_emulator
  u_test_drig -->|"cloud-api → public-api"| u_cloud
  u_device -->|"link-profile → ble-profile"| u_protocol
  u_emulator -->|"link-profile → ble-profile"| u_protocol
  u_mobile -->|"link-profile → ble-profile, reading-format → reading-schema"| u_protocol
  u_test_drig -->|"link-profile → ble-profile, reading-format → reading-schema"| u_protocol
  u_cloud -->|"reading-format → reading-schema"| u_protocol
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef plain stroke-dasharray:2 3
  class u_root,u_cloud,u_device,u_emulator,u_mobile,u_protocol,u_test_drig planned
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [plantwatch](../../README.md) | system | Tells people when their house plants need water, using a sensor in the pot, a phone app and cloud services | planned | [component](component.md) |
| [cloud](../../cloud/README.md) | system | Server side that turns uploaded readings into plant history and alerts | planned | [component](../../cloud/doc/diagrams/component.md) |
| [device](../../device/README.md) | firmware | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | planned | [component](../../device/doc/diagrams/component.md) |
| [emulator](../../emulator/README.md) | tool | Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware | planned | [context](../../emulator/doc/diagrams/context.md) |
| [mobile](../../mobile/README.md) | app | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | planned | [component](../../mobile/doc/diagrams/component.md) |
| [protocol](../../protocol/README.md) | specification | Defines the BLE profile of the sensor stick and the format of a reading | planned | [context](../../protocol/doc/diagrams/context.md) |
| [test-rig](../../test-rig/README.md) | test | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware | planned | [context](../../test-rig/doc/diagrams/context.md) |
