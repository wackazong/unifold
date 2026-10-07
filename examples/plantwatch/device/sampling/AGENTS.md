# AGENTS.md: sampling

This folder is a [unifold](https://unifold.md) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `unifold`. From
there, `python3 doc/skills/check-docs/scripts/unifold.py show device/sampling`
prints this unit with its neighbours.

## Why

A reading is made in exactly one place, and this is it. `sampling` changes
when what is measured changes, or how a raw value becomes a quantity: a
sensor part, a probe type, the housing, a new quantity.

Before `sampling` there are only raw signals; after it, a reading is kept or
passed on, never altered. Measuring, converting and numbering are one unit
so that the rule "a reading is complete and final when it leaves" has one
owner. `sampling` does not know where its readings go, and it does not know
the board: it converts numbers into numbers, which makes the calibration
testable with a table of values.

The main tension is identity. A reading must carry its sequence number
from the first moment, but this unit has no memory that survives a start.
The number is therefore computed from the tick count
(see [context](doc/context.md)). The price is a jump at every start.

What must stay true: one reading per interval, whatever the sensors do.
A reading with absent quantities says "alive, but could not measure",
which a missing reading cannot say.

## Read next

1. [README.md](README.md): what a subscriber gets
2. [doc/context.md](doc/context.md): rules from above, in particular how a reading is numbered
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): calibration per probe type
5. [doc/references/calibration.md](doc/references/calibration.md): formulas, constants and test cases
6. What `sampling` expects of its needs:
   [sensor-io](doc/references/sensor-io.md),
   [timer](doc/references/timer.md)

## Skills

| Skill | Use it when |
|---|---|
| [sampling-recalibrate-the-soil-probe](doc/skills/sampling-recalibrate-the-soil-probe/SKILL.md) | The probe type, its supply or its housing has changed, or measured boards disagree with the constants |

## Rules for work here

- The constants in [calibration.md](doc/references/calibration.md) and in
  the code are the same numbers. Change both in one change, and the
  example tables first: they are the test cases.
- What `sampling` expects of raw values and of time is written in the
  contracts of its two needs. A new expectation goes there before the
  code relies on it.
- The sampling times are computed from the seconds since start: first
  time plus n times the interval. Never "now plus interval"; that drifts
  by the duration of every measurement.
- One request for raw values per reading. Measuring twice to be sure
  doubles the largest item of the energy budget cited in
  [context](doc/context.md).
- Do not keep a value from an earlier reading to fill a gap. An
  unavailable value makes the quantity absent.
- The count of readings since start lives in RAM and starts at 1 with
  every start. Do not try to continue it from anywhere.
