# emulator

`emulator` is a desktop program that behaves like a sensor stick. A central that connects to it over BLE finds the same service, the same procedures and the same kind of readings as on a sensor stick. The measured values come from a scenario instead of sensors, and time is simulated: a month of readings takes seconds. The program exists so that everything that talks to a sensor stick can be developed and tried out without hardware and without waiting.

## Why

What this unit hides is how a scenario is turned into readings and served over a BLE controller of the host ([0001](docs/decisions/0001-speak-real-ble-through-a-controller-of-the-host.md)). A sensor stick is slow to work with: one reading in 15 minutes, a full memory after a month, and a board on the desk. The emulator exists to remove the board and the waiting and to keep everything else, so that what is developed against it also works with a sensor stick. It changes when the definition it implements changes, or when a situation has to be reproduced that no scenario can express.

That gives the program two faces. The radio face must be indistinguishable from a sensor stick, so it speaks real BLE and has nothing of its own. The control face is what a sensor stick does not have: a way to dictate values and time. It is kept off the radio, on a local HTTP port.

The program is built from the profile definition alone. A second, independent reading of that text is half of the program's value: where it behaves differently from a sensor stick, either the text has a gap or one of the two is wrong.

The price: the host needs a Bluetooth controller, and the program says nothing about energy, memory wear or radio timing. What must stay true: the radio face follows the definition and nothing else, and a run is reproducible.

## Read next

1. [scenario control](../docs/references/scenario-control/index.md): the HTTP API and, linked from it, the scenario document
2. [docs/references/glossary.md](docs/references/glossary.md): the terms of this unit
3. [docs/explanation/context.md](docs/explanation/context.md): what it inherits from above
4. [Decisions](docs/decisions/index.md)
5. [Writing a scenario](docs/skills/emulator-write-a-scenario/SKILL.md)
