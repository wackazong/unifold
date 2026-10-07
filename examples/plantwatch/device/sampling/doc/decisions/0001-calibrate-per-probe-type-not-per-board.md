---
status: proposed
date: 2026-10-06
---
# Calibrate the soil probe per probe type, not per board

## Context and Problem Statement

Soil moisture is a percentage of the calibrated range: 0 for the probe in
dry air, 100 for the probe in water. Capacitive probes of one type differ
from each other by a few percent of that range. The two end points can be
fixed once for the type, or measured for every single board. Measured
values would have to be stored on the board, and `sampling` has no memory
that survives a start.

## Considered Options

- One pair of constants for the probe type, compiled into the firmware
- A pair of constants per board, measured in production and stored on the
  board
- Calibration by the user: hold the sensor stick in air, then in water

## Decision Outcome

Chosen option: "one pair of constants for the probe type", because a
watering hint needs to tell dry from moist, not 41 % from 43 %, and the
option needs neither a production step nor stored data.

### Consequences

- Good: no calibration data that can be lost or wrong on a single board.
- Good: the conversion is a pure function of the raw value and can be
  tested with a table.
- Bad: two boards in the same pot can differ by up to 5 percentage
  points.
- Bad: a new probe type, or a change of the probe's supply, needs new
  constants and a new firmware build.
- Bad: values of different probe types are only roughly comparable.

## More Information

Constants and formulas are in the
[calibration reference](../references/calibration.md). How to determine
them is the skill
[sampling-recalibrate-the-soil-probe](../skills/sampling-recalibrate-the-soil-probe/SKILL.md).
