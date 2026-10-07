# plantwatch

plantwatch tells people when their house plants need water. A sensor stick in
the pot measures the soil and its surroundings. A phone app collects the
readings when the phone is near, shows the state of each plant, and passes the
readings on to a server. The server keeps the history and raises an alert when
a plant needs attention.

**Status:** design. Every unit has `status: planned`; the documents are the
design and no product code exists yet. This project is the worked example of
the unifold standard.

**Map:** the [architecture diagram](doc/diagrams/architecture.md) shows all
parts and how they depend on each other. Each part is a folder with its own
`README.md`.
[unifold.html](unifold.html) is the same map as a page in which every box can
be clicked; `unifold site` writes it.

This repository is documented with [unifold](https://unifold.md): some
folders are units with a declared interface. The interface of the project as
a whole is in [unit.yaml](unit.yaml) and described below. Why the project is
cut the way it is, is in [AGENTS.md](AGENTS.md).

## Provides

### `app-ui`

The phone app as its user sees it. For each plant it shows the latest reading,
the history, and whether the plant needs water, more light or a warmer place.
It works without a network connection and shows the last known state.
A plant that needs attention produces one notification, not a series.

The end-to-end catalogue named as `verified-by` in the manifest checks the
path from a sensor value to an alert and to the notification being handed
on. It cannot observe a phone. What the screens show, and use without a
network, are checked by the part that builds the app, once its checks exist.

### `test-report`

The result of the automated end-to-end tests as a JUnit XML file. A run
exercises the path from a sensor value to an alert. It can run against a real
sensor stick or against a simulated one.

## Needs

### `soil-probe`

A capacitive probe that sits in the soil and delivers an analogue voltage that
falls as the soil gets wetter. It runs from a supply of 2.0 to 3.3 V, draws at
most 5 mA, and its output is stable within 100 ms after power is applied and
proportional to the supply. The calibration is described by the unit that
reads it.

### `ambient-sensor`

A combined light and temperature sensor on an I2C bus at 100 kHz, close
enough to the plant to stand for its conditions. It measures 0 to 100 000 lux
and -20 to 60 °C, delivers a measurement within 150 ms, and draws about 1 µA
when idle.

### `push-service`

A service such as APNs or FCM.

- A phone registers with it for the notifications of one owner, can end that
  registration, and is told when its address at the service has changed.
- A sender hands it a notification for an owner: a title, a body, a few data
  fields that reach the phone unchanged, a time to live, and an identifier
  under which a repeated notification replaces the earlier one.
- It answers each request with one of three results: taken, refused for
  good, failed for now.
- It delivers a taken notification to every phone registered for that owner.
  Delivery may be delayed and is not guaranteed.

### `container-host`

Something that

- runs containers and restarts one that stops,
- connects them with a private network in which they find each other by
  name,
- gives them volumes that survive the replacement of a container, on at
  least two separate storage devices,
- publishes exactly one port to the outside and terminates TLS for it, and
- keeps the clocks of the containers within 10 seconds of UTC.

## Out of scope

- Automatic watering. plantwatch tells people; it does not act.
- Sensor sticks that reach the server by themselves. See
  [decision 0001](doc/decisions/0001-the-phone-relays-between-sensor-and-server.md).
- Identifying plant species. The user sets the thresholds or picks a preset.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md): what to read, what to change with
your change, and how to run the generator and the checker.

## Licence

The example is part of the unifold repository and under its licence: MIT or
Apache-2.0, at your option
([LICENSE-MIT](doc/references/unifold/LICENSE-MIT),
[LICENSE-APACHE](doc/references/unifold/LICENSE-APACHE)).

## More

- [AGENTS.md](AGENTS.md): why the system is cut this way
- [doc/architecture.md](doc/architecture.md): the path of a reading, and where things run
- [Context diagram](doc/diagrams/context.md), [component diagram](doc/diagrams/component.md),
  [architecture diagram](doc/diagrams/architecture.md)
- [Decisions](doc/decisions/index.md)
- [Glossary](doc/references/glossary.md), [conventions](doc/references/conventions.md),
  [product parameters](doc/references/product-parameters.md)
