# AGENTS.md: emulator

This folder is a [youmedoc](https://youmedoc.example) unit.

## Why

A sensor stick is slow to work with: one reading in 15 minutes, a full
memory after a month, and a board on the desk. The emulator removes the
board and the waiting. It keeps everything else, so that what is developed
against it also works with a sensor stick.

That gives the program two faces. The radio face must be indistinguishable
from a sensor stick, so it speaks real BLE and has nothing of its own. The
control face is what a sensor stick does not have: a way to dictate values
and time. It is kept off the radio, on a local HTTP port.

The program is built from the profile definition alone. A second,
independent reading of that text is half of the program's value: where it
behaves differently from a sensor stick, either the text has a gap or one
of the two is wrong.

The price: the host needs a Bluetooth controller, and the program says
nothing about energy, memory wear or radio timing. What must stay true: the
radio face follows the definition and nothing else, and a run is
reproducible.

## Read next

1. [README.md](README.md): what the two ports guarantee
2. [doc/context.md](doc/context.md): what the program inherits from the project
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): real BLE, and how time moves
5. [doc/references/scenario-format.md](doc/references/scenario-format.md): the scenario document
6. [doc/references/scenario-control-api.md](doc/references/scenario-control-api.md): the HTTP API

## Skills

| Skill | Use it when |
|---|---|
| [emulator-write-a-scenario](doc/skills/emulator-write-a-scenario/SKILL.md) | A situation of a plant or of a sensor stick shall be reproduced |

## Rules for work here

- Build the radio face from the definition behind `link-profile` and from
  nothing else. Do not read, port or imitate another implementation.
- If the definition does not say what to do, do not guess. The gap is a
  finding: report it, and build only after the definition is corrected.
- Add nothing to the radio face that the definition does not have: no
  extra characteristic, no marker in the advertising data.
- No randomness and no wall clock in anything that ends up in a reading.
- A control request names a target state. Never add a request that means
  "one more step".
- Radio timing stays real time. Do not scale it with simulated time.
