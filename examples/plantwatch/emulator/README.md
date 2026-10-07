---
unit: emulator
summary: Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware
kind: tool
status: planned
provides:
  ble-link:
    kind: protocol
    summary: Serves live and stored readings to a nearby central over BLE, like a sensor stick
  scenario-control:
    kind: http
    summary: Loads a scenario of sensor values and moves simulated time forward
    contract: doc/references/scenario-control-api.md
needs:
  link-profile:
    kind: specification
    summary: The definition of the BLE services to implement
---
# emulator

emulator is a desktop program that behaves like a sensor stick. A central
that connects to it over BLE finds the same service, the same procedures
and the same kind of readings as on a sensor stick. The measured values
come from a scenario instead of sensors, and time is simulated: a month of
readings takes a moment. The program exists so that everything that talks
to a sensor stick can be developed and tried out without hardware and
without waiting.

## Provides

### `ble-link`

Through a Bluetooth controller of the host, the program advertises as a
sensor stick, accepts one central, and serves Info, Status, live readings,
and fetch and confirm, as the definition behind `link-profile` says, in
version 1.0.

What a central can rely on:

- Nothing on the radio link reveals that the sensor stick is simulated.
- The readings are those of the loaded scenario: one per sampling interval
  of simulated time, with exactly the values the scenario states, rounded
  to the resolution of each quantity.
- The program keeps 2 880 readings until a central confirms them. When
  full, it overwrites the oldest and reports `overflow`.
- The same scenario and the same sequence of control requests produce the
  same readings, with the same sequence numbers and tick counts.
- Sequence numbers are consecutive, except where the scenario asks for a
  gap. The tick count follows simulated time.

Limits:

- The host needs a Bluetooth LE controller that can act as a peripheral: a
  real adapter, or a virtual controller. Without one the port does not
  exist.
- Radio timing is real time: advertising interval, idle disconnect,
  bonding handshake. Only sampling and the tick count follow simulated time.
- Bonding stays open all the time unless the scenario limits it. This
  deviates from a sensor stick on purpose.
- One process simulates one sensor stick.
- Before a scenario is loaded, the program does not advertise.

### `scenario-control`

An HTTP API on the local machine. A client loads a scenario, moves
simulated time forward, takes the simulated sensor stick out of radio range
or cuts a transfer, and looks at what the program has done.

What a client can rely on:

- Every request states an absolute target, so repeating it is harmless.
- When a request that moves time has returned, every reading due up to the
  new time is taken and visible on the radio link.
- Simulated time stands still unless a client moves it or sets a rate.
- The program remembers every reading it has taken in the scenario, also
  after a central has confirmed it, so that a client can compare what
  arrived elsewhere with what was sent.

Limits: the API listens on `127.0.0.1` only, by default on port 8650, and
has no authentication. Loading a scenario resets everything.

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
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- [Writing a scenario](doc/skills/emulator-write-a-scenario/SKILL.md)
