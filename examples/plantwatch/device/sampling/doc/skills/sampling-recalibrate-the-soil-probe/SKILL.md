---
name: sampling-recalibrate-the-soil-probe
description: Determine new calibration constants for the soil probe and put them into the calibration reference and the code of the sampling unit. Use it when the probe type, its supply or its housing has changed, or when measured boards disagree with the constants.
---
# Recalibrate the soil probe

The result is a new pair `SOIL_DRY` and `SOIL_WET`, new plausibility
limits, and a calibration reference and code that agree. The constants
hold for a probe type, so they are measured on several probes.

## Steps

1. **Take at least 10 boards** with the probe type in question, in their
   housing, at 20 to 25 °C, each with a fresh cell.
2. **Read raw values.** Use a debug build that prints the soil raw value
   of every request. Take 20 values per board and per state, and use the
   median.
3. **Dry point.** Probe clean and dry, in free air, at least 10 cm away
   from any surface. Note the median per board.
4. **Wet point.** Probe in tap water up to the mark on the probe, not
   deeper. Wait one minute. Note the median per board.
5. **Compute.** `SOIL_DRY` is the mean of the dry medians, `SOIL_WET` the
   mean of the wet medians, both rounded to 10.
6. **Check the spread.** For each board, compute the soil moisture of its
   own dry and wet median with the new constants. If any result is more
   than 5 percentage points away from 0 or 100, stop: the probe type
   spreads too much for calibration per type. Report this; it calls the
   [decision](../../decisions/0001-calibrate-per-probe-type-not-per-board.md)
   into question.
7. **Repeat with a weak cell** (2.2 V from a bench supply) on three
   boards. The medians must stay within 30 counts of the values at 3.0 V.
   If not, the raw value is not a clean ratio to the supply; report it to
   whoever provides `sensor-io`.
8. **Set the plausibility limits.** `SOIL_MAX_PLAUSIBLE` is halfway
   between the highest dry median and 4095. `SOIL_MIN_PLAUSIBLE` is half
   of the lowest wet median.
9. **Write the constants** into the table of the
   [calibration reference](../../references/calibration.md), with the
   date and "measured on n boards" as source, and recompute the example
   table there.
10. **Change the code** to the same numbers and update the test table from
    the example table.

## Checks

- The example table in the calibration reference and the test table in
  the code have the same rows.
- A board in air reads 0.0 to 5.0 %, a board in water 95.0 to 100.0 %.
- A board with the probe unplugged gives a reading with soil moisture
  absent.

## Reference

- [Calibration](../../references/calibration.md): formulas, constants,
  examples
