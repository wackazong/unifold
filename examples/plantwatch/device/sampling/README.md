# sampling

`sampling` is the place where a reading comes into being. At every sampling interval it asks for raw sensor values, converts them into soil moisture, light and temperature, gives the reading its sequence number and tick count, and hands it to everyone who has subscribed.

## Why

What this unit hides is the calibration from raw values to percent, lux and degrees ([0001](docs/decisions/0001-calibrate-per-probe-type-not-per-board.md)). A reading is made in exactly one place, and this is it. `sampling` changes when what is measured changes, or how a raw value becomes a quantity: a sensor part, a probe type, the housing, a new quantity.

Before `sampling` there are only raw signals; after it, a reading is kept or passed on, never altered. Measuring, converting and numbering are one unit so that the rule "a reading is complete and final when it leaves" has one owner. `sampling` does not know where its readings go, and it does not know the board: it converts numbers into numbers, which makes the calibration testable with a table of values.

The main tension is identity. A reading must carry its sequence number from the first moment, but this unit has no memory that survives a start. The number is therefore computed from the tick count (see [context](docs/explanation/context.md)). The price is a jump at every start.

What must stay true: one reading per interval, whatever the sensors do. A reading with absent quantities says "alive, but could not measure", which a missing reading cannot say.

## Read next

1. [docs/references/calibration.md](docs/references/calibration.md): formulas, constants and test cases
2. What `sampling` expects of its needs: [sensor-io](../docs/references/sensor-io.md), [timer](../docs/references/timer.md)
3. [docs/explanation/context.md](docs/explanation/context.md): what `sampling` inherits from above
4. [Decisions](docs/decisions/index.md)
