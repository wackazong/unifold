# AGENTS.md: device

This folder is a [youmedoc](https://youmedoc.example) unit.

## Why

One number shapes this firmware: an average current below 20 µA, so that a
coin cell lasts a year. The firmware therefore sleeps almost always. It
has no main loop and no scheduler; its parts are libraries that react to
a timer or to the radio, do a short piece of work and return.

The firmware is cut where the reasons for change differ: the board, the
measuring, the memory and the BLE profile each change on their own
occasion. Only one part touches the hardware, so the others can be built
and tested on a development machine.

A reading moves in one direction: it is made, numbered and stamped once,
then kept, then served. No part hands a reading back or alters it. To
make that possible without shared storage, the sequence number is computed
where the reading is made; the price is numbers that jump at every start.

What must stay true: a reading is in durable memory before the board
sleeps again; it leaves that memory only through a confirm or an overflow;
and no change exceeds the energy budget.

## Read next

1. [README.md](README.md): what the firmware provides and needs
2. [doc/context.md](doc/context.md): what it inherits from the project
3. [doc/architecture.md](doc/architecture.md): reasoning, invariants, the sleep and wake cycle
4. [doc/diagrams/component.md](doc/diagrams/component.md): the parts and their wiring
5. [doc/decisions/index.md](doc/decisions/index.md): sleep and advertising, hardware access, sequence numbers
6. [doc/references/energy-budget.md](doc/references/energy-budget.md): where the 20 µA go

## Skills

| Skill | Use it when |
|---|---|
| [device-add-a-sensor-driver](doc/skills/device-add-a-sensor-driver/SKILL.md) | A sensor part is added or replaced on the board |
| [device-check-the-energy-budget](doc/skills/device-check-the-energy-budget/SKILL.md) | A change makes the board wake more often, stay awake longer or use the radio more |

## Rules for work here

- Nothing waits in a loop. Code that needs to wait sets an alarm or
  reacts to a radio event, and returns.
- The start-up code in this folder only creates the parts in the order
  given in [doc/architecture.md](doc/architecture.md) and returns. It
  holds no logic. Logic belongs into a part.
- A part does not include a file of another part other than its public
  interface. If two parts need the same type, the part that provides the
  port defines it.
- Every number in the [energy budget](doc/references/energy-budget.md)
  is a planned value until it is measured. Replace it when a measurement
  exists.
- A feature that needs a setting to survive a start has no place to keep
  it today. That is a change of the decomposition, not a detail: propose
  it as a decision first.
