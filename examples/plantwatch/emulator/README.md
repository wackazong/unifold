# emulator

`emulator` is a desktop program that behaves like a sensor stick. A central that connects to it over BLE finds the same service, the same procedures and the same kind of readings as on a sensor stick. The measured values come from a scenario instead of sensors, and time is simulated: a month of readings takes seconds. The program exists so that everything that talks to a sensor stick can be developed and tried out without hardware and without waiting.

## Why

A sensor stick is slow to work with: one reading in 15 minutes, a full memory after a month, and a board on the desk. The emulator exists to remove the board and the waiting and to keep everything else, so that what is developed against it also works with a sensor stick. It changes when the definition it implements changes, or when a situation has to be reproduced that no scenario can express yet.

That gives the program two faces. The radio face must be indistinguishable from a sensor stick, so it speaks real BLE and has nothing of its own. The control face is what a sensor stick does not have: a way to dictate values and time. It is kept off the radio, on a local HTTP port.

The program is built from the profile definition alone. A second, independent reading of that text is half of the program's value: where it behaves differently from a sensor stick, either the text has a gap or one of the two is wrong.

The price: the host needs a Bluetooth controller, and the program says nothing about energy, memory wear or radio timing. What must stay true: the radio face follows the definition and nothing else, and a run is reproducible.

## Capabilities

### `ble-link`

The program uses a Bluetooth controller of the host. It sends nothing the BLE profile does not name: no further characteristic and no further byte in the advertising data. Where the profile leaves a choice or sets only a bound, a central observes this:

| Matter | Behaviour |
|---|---|
| Sampling interval | As the scenario states: 300 s to 3600 s of simulated time, 900 s by default |
| Readings | One at every simulated start, then one per interval, with exactly the values the scenario states, rounded to the resolution of each quantity |
| A quantity the scenario marks as failed | Absent from the reading. The reading is still taken. |
| Sequence numbers | Rise strictly, also across a simulated restart. Consecutive unless the scenario asks for a gap. |
| Tick count | The boot counter rises by one at every simulated restart. The seconds follow simulated time exactly. |
| Unconfirmed readings | 2 880 are kept, also through a simulated restart |
| Full memory | The program discards the oldest reading and reports the overflow |
| Advertising | Every 250 ms while no central is connected and the simulated sensor stick is in range |
| Connections | Closed after 30 s without a request, and after 10 minutes in any case |
| Bonding | Open during the first 300 s of simulated time after every start. 4 bonds are kept through a simulated restart. |
| Repetition | The same scenario and the same sequence of control requests give the same readings, sequence numbers and tick counts |

Limits:

- The host needs a Bluetooth LE controller that can act as a peripheral: a real adapter, or a virtual controller. Without one the capability does not exist.
- Advertising, connections and the bonding handshake run in real time. Sampling, the tick count and the time in which bonding is open follow simulated time.
- A scenario can ask for bonding that is always open. The program then departs from the profile in this one point.
- One process simulates one sensor stick.
- At start the program loads the built-in scenario `steady` (constant mid-range values, sampling interval 900 s) and runs simulated time at rate 1. It then behaves like a sensor stick with nobody controlling it. Loading a scenario replaces `steady`.

## Read next

1. [scenario control](../docs/references/scenario-control/index.md): the HTTP API and, linked from it, the scenario document
2. [docs/references/glossary.md](docs/references/glossary.md): the terms of this unit
3. [docs/explanation/context.md](docs/explanation/context.md): what it inherits from above
4. [Context diagram](docs/diagrams/context.md)
5. [Decisions](docs/decisions/index.md)
6. [Writing a scenario](docs/skills/emulator-write-a-scenario/SKILL.md)
