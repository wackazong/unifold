---
unit: plantwatch
youmedoc: "0.1"
summary: Tells people when their house plants need water, using a sensor in the pot, a phone app and cloud services
kind: system
status: planned
provides:
  app-ui:
    kind: ui
    summary: Shows the state of each plant and tells the user when to water it
  test-report:
    kind: file
    summary: Result of the automated end-to-end tests, for developers and CI
needs:
  soil-probe:
    kind: hardware
    summary: Capacitive soil moisture probe with an analogue output
  ambient-sensor:
    kind: hardware
    summary: Light and temperature sensor on an I2C bus
  push-service:
    kind: http
    summary: Delivers a notification to a phone, for example APNs or FCM
  container-host:
    kind: infrastructure
    summary: Runs containers, gives them a private network and persistent volumes
wiring:
  app-ui: mobile.app-ui
  test-report: test-rig.test-report
  device.soil-probe: soil-probe
  device.ambient-sensor: ambient-sensor
  device.link-profile: protocol.ble-profile
  emulator.link-profile: protocol.ble-profile
  mobile.link-profile: protocol.ble-profile
  mobile.reading-format: protocol.reading-schema
  mobile.sensor-link: [device.ble-link, emulator.ble-link]
  mobile.cloud-api: cloud.public-api
  mobile.push-service: push-service
  cloud.reading-format: protocol.reading-schema
  cloud.push-service: push-service
  cloud.container-host: container-host
  test-rig.device-under-test: [device.ble-link, emulator.ble-link]
  test-rig.scenario-control: emulator.scenario-control
  test-rig.cloud-api: cloud.public-api
  test-rig.link-profile: protocol.ble-profile
  test-rig.reading-format: protocol.reading-schema
---
# plantwatch

plantwatch tells people when their house plants need water. A sensor stick in
the pot measures the soil and its surroundings. A phone app collects the
readings when the phone is near, shows the state of each plant, and passes the
readings on to a server. The server keeps the history and raises an alert when
a plant needs attention.

This repository is documented with [youmedoc](https://youmedoc.example).
Start with [AGENTS.md](AGENTS.md).

Every unit in this repository has `status: planned`. The documents are the
design; no product code exists yet.

## Provides

### `app-ui`

The phone app as its user sees it. For each plant it shows the latest reading,
the history, and whether the plant needs water, more light or a warmer place.
It works without a network connection and shows the last known state.
A plant that needs attention produces one notification, not a series.

### `test-report`

The result of the automated end-to-end tests as a JUnit XML file. A run
exercises the path from a sensor value to an alert. It can run against a real
sensor stick or against a simulated one.

## Needs

### `soil-probe`

A capacitive probe that sits in the soil and delivers an analogue voltage that
depends on the moisture. The voltage range and the calibration are described
by the unit that reads it.

### `ambient-sensor`

A combined light and temperature sensor on an I2C bus, close enough to the
plant to stand for its conditions.

### `push-service`

A service at which a phone registers for the notifications of an owner and
which delivers a short notification to every phone registered for that
owner, such as APNs or FCM. Delivery may be delayed and is not guaranteed.

### `container-host`

Something that runs containers, connects them with a private network, and
gives them volumes that survive restarts. The server side makes no further
assumption about the hosting.

## Out of scope

- Automatic watering. plantwatch tells people; it does not act.
- Sensor sticks that reach the server by themselves. See
  [decision 0001](doc/decisions/0001-the-phone-relays-between-sensor-and-server.md).
- Identifying plant species. The user sets the thresholds or picks a preset.

## More

- [AGENTS.md](AGENTS.md): why the system is cut this way
- [doc/architecture.md](doc/architecture.md): the path of a reading, and where things run
- [Context diagram](doc/diagrams/context.md), [component diagram](doc/diagrams/component.md),
  [architecture diagram](doc/diagrams/architecture.md)
- [Decisions](doc/decisions/index.md)
- [Glossary](doc/references/glossary.md) and [conventions](doc/references/conventions.md)
