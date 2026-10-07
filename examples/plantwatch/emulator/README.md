# emulator

`emulator` is a desktop program that behaves like a sensor stick. A central
that connects to it over BLE finds the same service, the same procedures
and the same kind of readings as on a sensor stick. The measured values
come from a scenario instead of sensors, and time is simulated: a month of
readings takes seconds. The program exists so that everything that talks
to a sensor stick can be developed and tried out without hardware and
without waiting.

## Provides

### `ble-link`

Through a Bluetooth controller of the host, the program does everything
the definition behind `link-profile` requires of a sensor stick in version
1.0: advertising, the service with all its characteristics, every
procedure, every result code and the behaviour on failures. It sends
nothing the definition does not name: no further characteristic and no
further byte in the advertising data. Where the definition leaves a
choice or sets only a bound, a central observes this:

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
| Connections | One central at a time. Closed after 30 s without a request, and after 10 minutes in any case. |
| Bonding | Open during the first 300 s of simulated time after every start. 4 bonds are kept through a simulated restart. |
| Repetition | The same scenario and the same sequence of control requests give the same readings, sequence numbers and tick counts |

Limits:

- The host needs a Bluetooth LE controller that can act as a peripheral: a
  real adapter, or a virtual controller. Without one the port does not
  exist.
- Advertising, connections and the bonding handshake run in real time.
  Sampling, the tick count and the time in which bonding is open follow
  simulated time.
- A scenario can ask for bonding that is always open. The program then
  departs from the definition in this one point.
- One process simulates one sensor stick.
- At start the program loads the built-in scenario `steady` (constant
  mid-range values, sampling interval 900 s) and runs simulated time at
  rate 1. It then behaves like a sensor stick with nobody controlling it.
  Loading a scenario replaces `steady`.

### `scenario-control`

An HTTP API on the local machine. A client loads a scenario, moves
simulated time forward, takes the simulated sensor stick out of radio range
or cuts a transfer, and looks at what the program has done.

What a client can rely on:

- Every request states an absolute target. A repeated request gives the
  same response and changes nothing.
- When a request that moves time has returned, every reading due up to the
  new time is taken and visible on the radio link. Moving time by 30 days
  at the default interval, 2 880 readings, takes at most 5 s.
- Simulated time stands still unless a client moves it or sets a rate.
- Loading a scenario gives a simulated sensor stick as new: nothing from
  before is stored, no central is bonded, bonding is open.
- The program remembers every reading it has taken in the scenario, also
  after a central has confirmed it, so that a client can compare what
  arrived elsewhere with what was sent.

Limits: the API listens on `127.0.0.1` only, by default on port 8650, and
has no authentication.

```sh
curl -X PUT localhost:8650/scenario --data @drying-out.scenario.json
curl -X PUT localhost:8650/time --data '{"elapsed_s": 259200}'
curl localhost:8650/state
```

Contract: [scenario-control API](doc/references/scenario-control-api.md).
The scenario document is defined in the
[scenario format](doc/references/scenario-format.md).

## Needs

### `link-profile`

The definition of what a sensor stick advertises, of its GATT service and
characteristics, of the record that carries a reading, and of the
procedures, for major version 1. The program is built from this text and
from nothing else, so the text has to be complete for the peripheral side:
every byte layout, every result code, and the behaviour on every failure.

## Out of scope

- Raw sensor signals and calibration. A scenario states values in percent,
  lux and degrees Celsius.
- Energy use, memory wear and radio timing of real hardware.
- The role of a central.
- Deciding whether a plant needs attention. The program produces readings
  and knows no thresholds.

## More

- [AGENTS.md](AGENTS.md): why the program is built this way
- [doc/context.md](doc/context.md): what it inherits from above
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- [Glossary](doc/references/glossary.md): the terms of scenarios and simulated time
- [Writing a scenario](doc/skills/emulator-write-a-scenario/SKILL.md)
