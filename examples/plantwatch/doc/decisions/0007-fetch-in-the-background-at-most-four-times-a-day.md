---
status: proposed
date: 2026-10-07
---
# Fetch in the background at most four times a day per sensor stick

## Context and Problem Statement

Comparing both ends of the wiring between the sensor stick and the phone app
showed a conflict. The firmware promises 12 months of cell life for 4
connections of 3 seconds a day. The app expects to connect as often as once
per sampling interval while it is in range, which is up to 96 connections a
day and costs more current than the cell has in reserve. Neither part is
wrong on its own; the product parameters name no target for how fresh the
readings on the phone must be.

## Considered Options

- The app fetches whenever a new reading exists; the cell lasts less than a
  year
- The app fetches in the background at most 4 times a day per sensor stick,
  and whenever the owner opens the app
- The sensor stick refuses connections beyond its budget

## Decision Outcome

Chosen option: "at most 4 background fetches a day, and on opening the app",
because alerts are raised by the server side from uploaded readings, a delay
of a few hours does not harm a plant, and a cell that lasts a year is the
promise the owner was given.

### Consequences

- Good: the cell life stays as promised.
- Good: a reading is never more than about 6 hours old on the server while
  the phone is in range, and fresh whenever the owner looks.
- Bad: an alert can be up to 6 hours late even when the phone is near.
- To do when this is accepted: [mobile](../../mobile/README.md) changes what
  it expects of `sensor-link` and when it fetches in the background;
  [emulator](../../emulator/README.md) and [device](../../device/README.md)
  need no change. Until then the documents of the app still say "as often as
  once per sampling interval".
