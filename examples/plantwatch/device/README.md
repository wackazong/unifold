# device

`device` is the firmware of the sensor stick. It measures soil moisture, light and temperature at a fixed interval, keeps the readings on the sensor stick until a central has confirmed them, and serves them over Bluetooth Low Energy. It is built to run for a year on one coin cell.

## Why

A sensor stick runs one program, and this unit is that program: it turns two sensors and a coin cell into readings a central can fetch. It changes when what a sensor stick has to do changes, or the energy it may spend. A change of the board, of measuring, of the memory or of the profile lands in one part and leaves the others alone; that is how the parts are cut.

One number shapes the firmware: an average current below 20 µA, so that a coin cell lasts a year. The firmware therefore sleeps almost always and has no main loop: its parts are libraries that react to an alarm or to the radio, do a short piece of work and return. Only one part touches the hardware, so the others are tested on a development machine.

A reading moves in one direction: it is made, numbered and stamped once, then kept, then served. The sequence number is therefore computed where the reading is made; the price is numbers that jump at every start.

What must stay true: a reading is in durable memory before the board sleeps again; it leaves that memory only through a confirm or an overflow; and no change exceeds the energy budget.

## Capabilities

### `ble-link`

Where the BLE profile leaves a choice or sets only a bound, a central observes this:

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
| Connections | Closed after 30 s without a request, and after 10 minutes in any case |
| Cell life | At least 12 months on one CR2032 cell at the default interval with 4 connections of 3 s a day. The [energy budget](docs/references/energy-budget.md) says what other use costs. |

Limit: a sensor stick gives readings for 16 383 starts.

## Read next

1. [docs/explanation/reasoning.md](docs/explanation/reasoning.md): why the firmware is cut this way
2. [docs/explanation/invariants.md](docs/explanation/invariants.md): what holds at every moment
3. [docs/explanation/runtime.md](docs/explanation/runtime.md): the start order and the sleep and wake cycle
4. [docs/references/energy-budget.md](docs/references/energy-budget.md): where the 20 µA go
5. [docs/references/glossary.md](docs/references/glossary.md): the terms only the firmware uses
6. [docs/explanation/context.md](docs/explanation/context.md): what it inherits from above
7. [Context diagram](docs/diagrams/context.md), [component diagram](docs/diagrams/component.md)
8. [Decisions](docs/decisions/index.md)
