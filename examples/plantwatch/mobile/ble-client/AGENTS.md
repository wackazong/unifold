# AGENTS.md: ble-client

This folder is a [unifold](https://unifold.md) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `unifold`. From
there, `python3 doc/skills/check-docs/scripts/unifold.py show mobile/ble-client`
prints this unit with its neighbours.

## Why

The radio is the part of a phone program that fails most often and differs
most between iOS and Android: sensor sticks go out of range in the middle of
a transfer, the operating system suspends the program after seconds, the
owner switches Bluetooth off. This library exists so that all of that stays
in one place. Its consumer gets a plain promise: here is a batch of
readings, tell me when you have stored it.

The unit changes for two reasons that both come from the radio:
`link-profile` gets a new version, or iOS or Android change what a program
may do with BLE in the background. Nothing else should reach it.

The main trade-off: the client stores no readings. A reading exists on the
sensor stick until the consumer has acknowledged it, so there is no third
place where readings could wait or get lost. The price is that a fetch
depends on a consumer that answers within seconds, and that an interrupted
fetch repeats work
([0001](doc/decisions/0001-confirm-in-chunks-and-resume-at-the-oldest-unconfirmed-reading.md)).

What must stay true: the client never confirms a reading to a sensor stick
before the consumer has acknowledged it.

## Read next

1. [README.md](README.md): what the client provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/diagrams/context.md](doc/diagrams/context.md): the client among its
   neighbours
4. [doc/decisions/index.md](doc/decisions/index.md): decisions
5. [doc/references/fetch-session.md](doc/references/fetch-session.md): a
   fetch as a state machine, with sizes and timeouts
6. [doc/references/sensor-readings.md](doc/references/sensor-readings.md)
   and [doc/references/pairing.md](doc/references/pairing.md): the contracts
7. [doc/references/glossary.md](doc/references/glossary.md): acknowledge
   and confirm, chunk, session, anchor

## Skills

| Skill | Use it when |
|---|---|
| [ble-client-support-a-profile-version](doc/skills/ble-client-support-a-profile-version/SKILL.md) | `link-profile` has a new version and the client shall speak it |

## Rules for work here

- The order "deliver, wait for the acknowledgement, confirm" is not an
  optimisation target. Do not confirm early to save a round trip.
- Take every UUID, field layout and timing from `link-profile`. Do not copy
  them into the documents of this unit; they would drift.
- Platform code implements one common interface. A capability that only one
  platform has does not become part of a provided port.
- A background slot is short; see [doc/context.md](doc/context.md). Work
  that is not needed to fetch, deliver and confirm does not run in it.
- Test on real phones against a real or simulated sensor stick. Simulators
  of the phone platforms have no usable BLE.
- The client's own state is small on purpose: the pairings and the time
  anchors
  ([0002](doc/decisions/0002-keep-a-time-anchor-per-boot.md)). Do not add
  a cache of readings.
