# device

`device` is the firmware of the sensor stick. It measures soil moisture, light and temperature at a fixed interval, keeps the readings on the sensor stick until a central has confirmed them, and serves them over Bluetooth Low Energy. It is built to run for a year on one coin cell.

## Why

A sensor stick runs one program, and this unit is that program: it turns two sensors and a coin cell into readings a central can fetch. It changes when what a sensor stick has to do changes, or the energy it may spend. A change of the board, of measuring, of the memory or of the profile lands in one part and leaves the others alone; that is how the parts are cut.

One number shapes the firmware: an average current below 20 µA, so that a coin cell lasts a year. The firmware therefore sleeps almost always and has no main loop: its parts are libraries that react to an alarm or to the radio, do a short piece of work and return. Only one part touches the hardware, so the others are tested on a development machine.

A reading moves in one direction: it is made, numbered and stamped once, then kept, then served. The sequence number is therefore computed where the reading is made; the price is numbers that jump at every start.

What must stay true: a reading is in durable memory before the board sleeps again; it leaves that memory only through a confirm or an overflow; and no change exceeds the energy budget.

## Read next

1. [docs/explanation/reasoning.md](docs/explanation/reasoning.md): why the firmware is cut this way
2. [docs/explanation/invariants.md](docs/explanation/invariants.md): what holds at every moment
3. [docs/explanation/runtime.md](docs/explanation/runtime.md): the start order and the sleep and wake cycle
4. [docs/references/energy-budget.md](docs/references/energy-budget.md): where the 20 µA go
5. [docs/references/glossary.md](docs/references/glossary.md): the terms only the firmware uses
6. [docs/explanation/context.md](docs/explanation/context.md): what it inherits from above
7. [Component diagram](docs/diagrams/component.md)
8. [Decisions](docs/decisions/index.md)
