# plantwatch

plantwatch tells people when their house plants need water. A sensor stick in the pot measures the soil and its surroundings. A phone app collects the readings when the phone is near, shows the state of each plant, and passes the readings on to a server. The server keeps the history and raises an alert when a plant needs attention.

## Why

The system is cut along the lines where things are built, shipped and run separately: firmware on the sensor stick, an app on the phone, services on a server. Each of the three has its own toolchain, its own release rhythm and its own failure modes, so each is a unit.

Two more units exist because of what lies between those three, and one thing that lies between them is not a unit:

- A simulated sensor stick makes tests fast. It is written independently of the firmware, so that it also tests the protocol definition ([0003](docs/decisions/0003-the-emulator-implements-the-profile-independently.md)).
- The promise "a dry plant leads to one notification" spans all parts. One unit owns the tests of that promise.
- The radio protocol and the reading format are shared by several parts and owned by none, so they are references of plantwatch, and every part that implements the protocol names it as the contract of its connection ([0008](docs/decisions/0008-define-the-profile-and-the-reading-format-as-references-of-plantwatch.md)). A specification is not a unit.

The decision that shapes everything else is that the sensor stick talks only to a phone ([0001](docs/decisions/0001-the-phone-relays-between-sensor-and-server.md)).

## This example

**This is a design written before any code.** It is the example of [unifold](https://unifold.md) that shows every document convention of the standard, in all 22 units. That is much more than a unit should cost. Start with the small example, slugline, which is a folder beside this one in the unifold repository, and come back here to see how READMEs, explanation files, decisions, context items and skills look when a team chooses to write them.

Every unit has `status: planned`, and every decision in force is accepted: the documents are the design, and no product code exists yet. The [architecture diagram](docs/diagrams/architecture.md) shows all units and how they depend on each other; [unifold.html](unifold.html), written by `unifold site`, is the same map as a page in which every box can be clicked.

## Capabilities

### `app-ui`

The end-to-end catalogue named as `verified-by` in the manifest checks the path from a sensor value to an alert and to the notification being handed on. It cannot observe a phone. What the screens show, and use without a network, are checked by the part that builds the app, once its checks exist.

## Out of scope

- Automatic watering. plantwatch tells people; it does not act.
- Sensor sticks that reach the server by themselves. See [decision 0001](docs/decisions/0001-the-phone-relays-between-sensor-and-server.md).
- Identifying plant species. The user sets the thresholds or picks a preset.

## Read next

1. [docs/explanation/requirements.md](docs/explanation/requirements.md): what the product must achieve, and which qualities win
2. [docs/explanation/reasoning.md](docs/explanation/reasoning.md): the long form of the why
3. [docs/explanation/invariants.md](docs/explanation/invariants.md), [runtime.md](docs/explanation/runtime.md), [deployment.md](docs/explanation/deployment.md): invariants, the path of a reading, where things run
4. [docs/references/glossary.md](docs/references/glossary.md): terms
5. [docs/references/conventions.md](docs/references/conventions.md): units of measure, identifiers, time, delivery
6. [docs/references/ble-profile/index.md](docs/references/ble-profile/index.md) and [docs/references/reading-schema.md](docs/references/reading-schema.md): the radio protocol and the reading format, which several parts implement
7. [docs/references/product-parameters.md](docs/references/product-parameters.md): the numbers version 1 is designed for
8. [Component diagram](docs/diagrams/component.md), [architecture diagram](docs/diagrams/architecture.md), [decisions](docs/decisions/index.md), [risks](docs/explanation/risks.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md): what to read, what to change with your change, and how to run the generator and the checker.

## Licence

The example is part of the unifold repository and under its licence: MIT or Apache-2.0, at your option. The licence texts are in the root of that repository.
