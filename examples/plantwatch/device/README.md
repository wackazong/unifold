# device

`device` is the firmware of the sensor stick. It measures soil moisture,
light and temperature at a fixed interval, keeps the readings on the
sensor stick until a central has confirmed them, and serves them over
Bluetooth Low Energy. It is built to run for a year on one coin cell.

## Provides

### `ble-link`

The sensor stick as a central sees it over the air. The firmware does
everything the definition behind `link-profile` requires of a sensor stick
in version 1.0: advertising, the service with all its characteristics,
every procedure, every result code and the behaviour on failures. Where
that definition leaves a choice or sets only a bound, a central observes
this:

| Matter | Behaviour |
|---|---|
| Sampling interval | 900 s, or the value between 300 s and 3600 s the firmware was built with. It does not change while the firmware runs. |
| Readings | The first within 10 s after a start, then one per interval. A connection delays a reading by at most 1 s. |
| A sensor that fails | Its quantity is absent from the reading. The reading is still taken. |
| Sequence numbers | Rise strictly over the whole life of a sensor stick: consecutive between two starts, with a jump at every start |
| Tick count | The boot counter rises at every start and never repeats. The seconds are wrong by at most 50 ppm, about 2 minutes in 30 days. |
| Unconfirmed readings | At least 2 880 are kept, through power loss and a change of the cell |
| Full memory | The firmware discards the oldest readings, up to 204 at once, and reports the overflow |
| Advertising | Every 1285 ms while no central is connected |
| Connections | One central at a time. Closed after 30 s without a request, and after 10 minutes in any case. |
| Bonding | Open for 5 minutes after every start. At least 4 bonds survive power loss. |
| Cell life | At least 12 months on one CR2032 cell at the default interval with 4 connections of 3 s a day. The [energy budget](doc/references/energy-budget.md) says what other use costs. |

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
proportional to the supply voltage. The firmware supplies the probe with
2.0 V to 3.3 V and only while it measures; the probe draws at most 5 mA,
and its output is stable within 100 ms. The firmware is calibrated for one
type of probe, not for the single probe.

### `ambient-sensor`

One sensor for light and temperature on an I2C bus at 100 kHz, in a place
that sees the light the plant sees. It covers at least 0 to 100 000 lux
and −20 °C to 60 °C, runs on 2.0 V to 3.3 V, answers within 150 ms and
draws at most 1 µA when idle.

### `link-profile`

The definition of what a sensor stick advertises, of its service and
characteristics, of the record that carries a reading, of the procedures
and of the behaviour on failures, for major version 1. The firmware takes
this definition as it is and adds nothing to it.

## Out of scope

- Wall-clock time. The firmware counts ticks and never knows the date.
- Judging a reading. The firmware knows no plant and no threshold.
- Any radio other than BLE, and the role of a central.
- Updating itself.

## More

- [AGENTS.md](AGENTS.md): why the firmware is cut this way
- [doc/context.md](doc/context.md): what it inherits from above
- [doc/architecture.md](doc/architecture.md): invariants and the cycle of sleeping and waking
- [Context diagram](doc/diagrams/context.md),
  [component diagram](doc/diagrams/component.md),
  [architecture diagram](doc/diagrams/architecture.md)
- [Decisions](doc/decisions/index.md)
- [Energy budget](doc/references/energy-budget.md)
