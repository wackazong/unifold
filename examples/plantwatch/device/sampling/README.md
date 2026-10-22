# sampling

`sampling` is the place where a reading comes into being. At every sampling interval it asks for raw sensor values, converts them into soil moisture, light and temperature, gives the reading its sequence number and tick count, and hands it to everyone who has subscribed.

## Why

A reading is made in exactly one place, and this is it. `sampling` changes when what is measured changes, or how a raw value becomes a quantity: a sensor part, a probe type, the housing, a new quantity.

Before `sampling` there are only raw signals; after it, a reading is kept or passed on, never altered. Measuring, converting and numbering are one unit so that the rule "a reading is complete and final when it leaves" has one owner. `sampling` does not know where its readings go, and it does not know the board: it converts numbers into numbers, which makes the calibration testable with a table of values.

The main tension is identity. A reading must carry its sequence number from the first moment, but this unit has no memory that survives a start. The number is therefore computed from the tick count (see [context](docs/explanation/context.md)). The price is a jump at every start.

What must stay true: one reading per interval, whatever the sensors do. A reading with absent quantities says "alive, but could not measure", which a missing reading cannot say.

## Capabilities

### `readings`

A subscriber registers once, at start. From then on it receives every reading, once, in order, at the moment the reading is taken.

A reading consists of:

| Part | Form |
|---|---|
| Sequence number | Unsigned 32 bit, never 0 |
| Tick count | Boot counter and seconds since start at the moment of measuring |
| Soil moisture | 0.0 to 100.0 percent in steps of 0.1, or absent |
| Light | 0 to 100 000 lux in steps of 1, or absent |
| Temperature | −20.0 to 60.0 °C in steps of 0.1, or absent |

What a subscriber can rely on:

- **One reading per sampling interval.** The first is taken within 10 s after start, the following ones at whole multiples of the interval after the first; a measurement begins at most 1 s after its time. If no sensor answers, the reading has all three quantities absent; it is still taken.
- **The interval** is 900 s unless the build sets another value between 300 s and 3600 s. It does not change after start. `sampling` tells a caller the interval on request.
- **Sequence numbers rise strictly** over the whole life of a board, also across starts. They are consecutive between two starts and jump at a start.
- **Absent, not wrong.** A quantity is absent when its raw value is unavailable or outside the plausible limits of the [calibration](docs/references/calibration.md). No quantity is ever outside its range.
- **Order of delivery.** `sampling` calls the subscribers one after another, in the order in which they registered. All of them have returned before the next reading is taken.
- **A reading does not change** after it has been handed out.

Limits: up to 4 subscribers. A board gives readings for 16 383 starts and for 262 143 readings per start; after that `sampling` takes no more. Soil moisture is calibrated for the type of probe, not for the single board, and is accurate to 5 percentage points.

A reading as a subscriber sees it:

```text
sequence number   3 145 825        (start 12, 97th reading)
tick count        12 / 86 405 s
soil moisture     41.5 %
light             12 000 lx
temperature       21.4 °C
```

Contract: [readings](../docs/references/readings.md).

## Needs

### `sensor-io`

On request, one set of raw values within 300 ms: a soil value as a share of the probe's supply, a light value in counts of 0.01 lux, a temperature value in counts of 1/16 °C. Each can be reported as unavailable on its own. `sampling` asks once per reading and expects the sensors to draw no current in between. Contract: [sensor-io](../docs/references/sensor-io.md).

### `timer`

A tick count whose boot counter is higher at every start than ever before and whose seconds go on while the board sleeps, wrong by at most 100 ppm; and an alarm that calls `sampling` not before the second it names and at most 1 s after it. Contract: [timer](../docs/references/timer.md).

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
