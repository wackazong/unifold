# sampling

`sampling` is the place where a reading comes into being. At every sampling interval it asks for raw sensor values, converts them into soil moisture, light and temperature, gives the reading its sequence number and tick count, and hands it to everyone who has subscribed.

## Why

A reading is made in exactly one place, and this is it. `sampling` changes when what is measured changes, or how a raw value becomes a quantity: a sensor part, a probe type, the housing, a new quantity.

Before `sampling` there are only raw signals; after it, a reading is kept or passed on, never altered. Measuring, converting and numbering are one unit so that the rule "a reading is complete and final when it leaves" has one owner. `sampling` does not know where its readings go, and it does not know the board: it converts numbers into numbers, which makes the calibration testable with a table of values.

The main tension is identity. A reading must carry its sequence number from the first moment, but this unit has no memory that survives a start. The number is therefore computed from the tick count (see [context](docs/explanation/context.md)). The price is a jump at every start.

What must stay true: one reading per interval, whatever the sensors do. A reading with absent quantities says "alive, but could not measure", which a missing reading cannot say.

## Capabilities

### `readings`

- **One reading per sampling interval.** The first is taken within 10 s after start, the following ones at whole multiples of the interval after the first; a measurement begins at most 1 s after its time. If no sensor answers, the reading has all three quantities absent; it is still taken.
- **The interval** is 900 s unless the build sets another value between 300 s and 3600 s. It does not change after start.
- **Absent, not wrong.** A quantity is absent when its raw value is unavailable or outside the plausible limits of the [calibration](docs/references/calibration.md).

Limits: a board gives readings for 16 383 starts and for 262 143 readings per start; after that `sampling` takes no more. Soil moisture is calibrated for the type of probe, not for the single board, and is accurate to 5 percentage points.

## Needs

### `timer`

`sampling` copes with seconds that are wrong by up to 100 ppm and with an alarm that comes up to 1 s late.

## Out of scope

- Keeping readings. A reading that no subscriber keeps is gone.
- Sending readings anywhere.
- Changing the sampling interval after start.
- Smoothing over several readings. Every reading stands for one moment.
- Judging whether a value is good or bad for a plant.

## Read next

1. [docs/references/calibration.md](docs/references/calibration.md): formulas, constants and test cases
2. What `sampling` expects of its needs: [sensor-io](../docs/references/sensor-io.md), [timer](../docs/references/timer.md)
3. [docs/explanation/context.md](docs/explanation/context.md): what `sampling` inherits from above
4. [Context diagram](docs/diagrams/context.md)
5. [Decisions](docs/decisions/index.md)
