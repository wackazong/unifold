# AGENTS.md: sampling

This folder is a [youmedoc](https://youmedoc.example) unit.

## Why

A reading is made in exactly one place. Before sampling there are only raw
signals; after it, a reading is kept or passed on, never altered. Putting
measuring, converting and numbering into one unit gives the rule "a
reading is complete and final when it leaves" one owner.

sampling does not know where its readings go. It serves subscribers, so
that keeping a reading and showing it at once are two uses that sampling
need not tell apart. And it does not know the board: it converts numbers
into numbers, which makes the calibration testable with a table of values.

The main tension is identity. A reading must carry its sequence number
from the first moment, but this unit has no memory that survives a start.
The number is therefore computed from the tick count
(see [context](doc/context.md)). The price is a jump in the numbers at
every start and an upper limit of starts.

What must stay true: one reading per interval, whatever the sensors do.
A reading with absent quantities says "alive, but could not measure",
which a missing reading cannot say.

## Read next

1. [README.md](README.md): what a subscriber gets
2. [doc/context.md](doc/context.md): rules from above, in particular how a reading is numbered
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): calibration per probe type
5. [doc/references/calibration.md](doc/references/calibration.md): formulas and constants

## Skills

| Skill | Use it when |
|---|---|
| [sampling-recalibrate-the-soil-probe](doc/skills/sampling-recalibrate-the-soil-probe/SKILL.md) | The probe type, its supply or its housing has changed, or measured boards disagree with the constants |

## Rules for work here

- The constants in [calibration.md](doc/references/calibration.md) and in
  the code are the same numbers. Change both in one change.
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
