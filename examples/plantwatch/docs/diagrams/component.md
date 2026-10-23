<!-- unifold:generated - do not edit; run `unifold generate` -->
# Component diagram: plantwatch

**plantwatch** · [README](../../README.md) · [architecture](architecture.md)

The units directly inside `plantwatch` and how they are connected. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_root["plantwatch"]
    u_cloud["cloud"]
    u_device["device"]
    u_emulator["emulator"]
    u_mobile["mobile"]
    u_test_drig["test-rig"]
  end
  n_root___push_dservice{{"push-service"}}
  n_root___container_dhost{{"container-host"}}
  n_root___ambient_dsensor{{"ambient-sensor"}}
  n_root___soil_dprobe{{"soil-probe"}}
  p_root___app_dui(["app-ui"])
  p_root___test_dreport(["test-report"])
  u_mobile -->|"sensor-link → ble-link (real)"| u_device
  u_mobile -.->|"sensor-link → ble-link (simulated)"| u_emulator
  u_mobile -->|"cloud-api → public-api"| u_cloud
  u_mobile -->|"push-service"| n_root___push_dservice
  u_cloud -->|"push-service"| n_root___push_dservice
  u_test_drig -->|"device-under-test → ble-link (real)"| u_device
  u_test_drig -.->|"device-under-test → ble-link (simulated)"| u_emulator
  u_test_drig -->|"scenario-control (optional)"| u_emulator
  u_test_drig -->|"cloud-api → public-api"| u_cloud
  u_cloud -->|"container-host"| n_root___container_dhost
  u_device -->|"ambient-sensor"| n_root___ambient_dsensor
  u_device -->|"soil-probe"| n_root___soil_dprobe
  p_root___app_dui --> u_mobile
  p_root___test_dreport --> u_test_drig
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_cloud,u_device,u_emulator,u_mobile,u_test_drig planned
```

| Unit | Kind | Summary | Status | Diagram |
|---|---|---|---|---|
| [cloud](../../cloud/README.md) | system | Server side that turns uploaded readings into plant history and alerts | **planned** | [component](../../cloud/docs/diagrams/component.md) |
| [device](../../device/README.md) | firmware | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE | **planned** | [component](../../device/docs/diagrams/component.md) |
| [emulator](../../emulator/README.md) | tool | Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware | **planned** | [context](../../emulator/docs/diagrams/context.md) |
| [mobile](../../mobile/README.md) | app | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server | **planned** | [component](../../mobile/docs/diagrams/component.md) |
| [test-rig](../../test-rig/README.md) | test | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware | **planned** | [context](../../test-rig/docs/diagrams/context.md) |

### Connections

| Need | Provider | Note |
|---|---|---|
| capability `app-ui` of `plantwatch` | `mobile.app-ui` | implemented by |
| capability `test-report` of `plantwatch` | `test-rig.test-report` | implemented by |
| `mobile.sensor-link` | `device.ble-link` (real) or `emulator.ble-link` (simulated) |  |
| `mobile.cloud-api` | `cloud.public-api` |  |
| `mobile.push-service` | need `push-service` of `plantwatch` |  |
| `cloud.push-service` | need `push-service` of `plantwatch` |  |
| `test-rig.device-under-test` | `device.ble-link` (real) or `emulator.ble-link` (simulated) |  |
| `test-rig.scenario-control` | `emulator.scenario-control` | optional |
| `test-rig.cloud-api` | `cloud.public-api` |  |
| `cloud.container-host` | need `container-host` of `plantwatch` |  |
| `device.ambient-sensor` | need `ambient-sensor` of `plantwatch` |  |
| `device.soil-probe` | need `soil-probe` of `plantwatch` |  |
