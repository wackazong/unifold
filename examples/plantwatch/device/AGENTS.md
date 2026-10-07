# AGENTS.md: device

This folder is a [unifold](https://unifold.md) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `unifold`. From
there, `python3 doc/skills/check-docs/scripts/unifold.py show device`
prints this unit with its neighbours.

## Why

A sensor stick runs one program, and this unit is that program: it turns
two sensors and a coin cell into readings a central can fetch. It changes
when what a sensor stick has to do changes, or the energy it may spend. A
change of the board, of measuring, of the memory or of the profile lands
in one part and leaves the others alone; that is how the parts are cut.

One number shapes the firmware: an average current below 20 µA, so that a
coin cell lasts a year. The firmware therefore sleeps almost always and
has no main loop: its parts are libraries that react to an alarm or to
the radio, do a short piece of work and return. Only one part touches the
hardware, so the others are tested on a development machine.

A reading moves in one direction: it is made, numbered and stamped once,
then kept, then served. The sequence number is therefore computed where
the reading is made; the price is numbers that jump at every start.

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
7. [doc/references/glossary.md](doc/references/glossary.md): the terms only the firmware uses

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
- A part writes down what it expects of another as a need, with a
  contract where numbers matter. Whoever changes a wiring line in
  [README.md](README.md) reads both ends and makes them agree.
- Every number in the [energy budget](doc/references/energy-budget.md)
  is a planned value until it is measured. Replace it when a measurement
  exists.
- A feature that needs a setting to survive a start has no place to keep
  it today. That is a change of the decomposition, not a detail: propose
  it as a decision first.
