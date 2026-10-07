---
unit: device
summary: Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE
kind: firmware
status: planned
provides:
  ble-link:
    kind: protocol
    summary: Serves live and stored readings to a nearby central over BLE
needs:
  soil-probe:
    kind: hardware
    summary: Capacitive soil moisture probe with an analogue output
  ambient-sensor:
    kind: hardware
    summary: Light and temperature sensor on an I2C bus
  link-profile:
    kind: specification
    summary: The definition of the BLE services this firmware has to implement
wiring:
  ble-link: link.ble-link
  hal.soil-probe: soil-probe
  hal.ambient-sensor: ambient-sensor
  sampling.sensor-io: hal.sensor-io
  sampling.timer: hal.timer
  store.flash: hal.flash
  store.readings: sampling.readings
  link.radio: hal.radio
  link.reading-log: store.reading-log
  link.live-readings: sampling.readings
  link.link-profile: link-profile
---
# device

device is the firmware of the sensor stick. It measures soil moisture,
light and temperature at a fixed interval, keeps the readings on the
sensor stick until a central has confirmed them, and serves them over
Bluetooth Low Energy. It is built to run for a year on one coin cell.

## Provides

### `ble-link`

The sensor stick as a central sees it over the air.

What a central can rely on:

- **Conformance.** The firmware implements the sensor stick's side of the
  definition it gets through `link-profile`, version 1.0, completely.
- **Readings.** The firmware takes one reading per sampling interval, the
  first within 10 s after it starts. The interval is 900 s unless the
  firmware was built with another value between 300 s and 3600 s. A
  quantity that could not be measured is absent from the reading.
- **Sequence numbers** rise strictly over the whole life of a sensor
  stick. They are consecutive between two starts and jump at every start.
- **Keeping.** The firmware holds at least 2 880 readings that no central
  has confirmed. They survive power loss and a change of the cell. When
  the memory is full, the firmware discards the oldest readings, up to
  204 at once, and reports an overflow.
- **Time.** The seconds of the tick count are wrong by at most 50 ppm,
  about 2 minutes in 30 days. The boot counter rises by one at every
  start.
- **Being found.** While no central is connected, the firmware advertises
  every 1285 ms.
- **Connections.** One central at a time. The firmware closes a
  connection that has carried no request for 30 s, and any connection
  after 10 minutes. Sampling goes on during a connection.
- **Cell life.** At least 12 months on one CR2032 cell at the default
  interval, if centrals connect about 4 times a day for a few seconds.
  A central that stays connected, or connects much more often, shortens
  the life of the cell.

Limits:

- The sampling interval cannot be changed over the radio link.
- The firmware reports no battery level.
- A new firmware image is written through the programming header of the
  board, not over the air.
- A sensor stick gives readings for 16 383 starts.

## Needs

### `soil-probe`

A capacitive probe in the soil with an analogue output between 0 V and its
supply voltage. The output falls as the soil gets wetter and is
proportional to the supply voltage. The firmware powers the probe only
while it measures; the probe draws at most 5 mA and settles within 100 ms.
The firmware is calibrated for one type of probe, not for the single
probe.

### `ambient-sensor`

One sensor for light and temperature on an I2C bus, in a place that sees
the light the plant sees. It covers at least 0 to 100 000 lux and −20 °C
to 60 °C, answers within 150 ms and draws at most 1 µA when idle.

### `link-profile`

The definition of what a sensor stick advertises, of its GATT service and
characteristics, of the record that carries a reading, of the procedures
and of the behaviour on failures, for major version 1. The firmware
implements this definition and does not extend it.

## Out of scope

- Wall-clock time. The firmware counts ticks and never knows the date.
- Judging a reading. The firmware knows no plant and no threshold.
- Any radio other than BLE, and the role of a central.
- Updating itself.

## More

- [AGENTS.md](AGENTS.md): why the firmware is cut this way
- [doc/architecture.md](doc/architecture.md): invariants and the cycle of sleeping and waking
- [Context diagram](doc/diagrams/context.md),
  [component diagram](doc/diagrams/component.md),
  [architecture diagram](doc/diagrams/architecture.md)
- [Decisions](doc/decisions/index.md)
- [Energy budget](doc/references/energy-budget.md)
