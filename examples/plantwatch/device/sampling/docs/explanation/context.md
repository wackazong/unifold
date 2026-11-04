# Context of sampling

What this unit takes over from the units above, and what each item means here.

## From device

### [device/0003 Sequence numbers are derived from the tick count](../../../docs/decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md)

The sequence number of a reading is the boot counter times 262 144 plus the count of readings since that start, beginning with 1. Nothing is stored for it.

`sampling` computes the number this way and needs a boot counter that never repeats. It takes no more readings when the boot counter exceeds 16 383 or the count exceeds 262 143.

### [device/0002 Only one part of the firmware touches the hardware](../../../docs/decisions/0002-only-one-part-touches-the-hardware.md)

One part owns all hardware access. The other parts are hardware-independent and run on a development machine. `sampling` sees sensors only as raw numbers through `sensor-io`, and is tested with a table of raw values.

### [device/0001 Sleep between events and advertise all the time at a long interval](../../../docs/decisions/0001-sleep-between-events-and-advertise-all-the-time.md)

The firmware has no loop that waits. Work happens in short events, then the board sleeps. `sampling` does all work for a reading inside one alarm, sets the next alarm and returns.

### [device: energy budget](../../../docs/references/energy-budget.md)

One reading may cost 600 µC, most of it for powering the soil probe once. `sampling` therefore makes one request for raw values per reading.

### [device: glossary](../../../docs/references/glossary.md)

A start is the firmware beginning to run, not a wake-up from sleep. A raw value is a number as a sensor delivers it, before calibration. An alarm is a second of the tick count at which a part asks to be called. All documents of this unit use these terms unchanged.

## From plantwatch

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

A sensor stick numbers its readings in strictly increasing order and never reuses a number. A reading is never changed after it has been taken. The guarantees "sequence numbers rise strictly" and "a reading does not change" of `readings` come from this decision.

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../../docs/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

A reading carries a boot counter and the seconds since that boot instead of a time. `sampling` stamps a reading with the tick count of the moment of measuring.

### [plantwatch: conventions, measured quantities](../../../../docs/references/conventions.md#measured-quantities)

The convention defines three quantities:

- Soil moisture is given in percent of the calibrated range, from 0 to 100, with a resolution of 0.1.
- Light is given in lux, from 0 to 100 000, with a resolution of 1.
- Temperature is given in °C, from −20 to 60, with a resolution of 0.1.

A quantity that could not be measured is absent, not zero. The units, ranges and rounding of the [calibration](../references/calibration.md) come from this convention, and so does the rule "absent, not wrong".

### [plantwatch: glossary](../../../../docs/references/glossary.md)

A reading is one set of measurements taken at the same moment by one sensor stick, never a single value. The sampling interval is the time between two readings. In `sampling`, the three quantities of one reading come from one request for raw values.

### [plantwatch: product parameters](../../../../docs/references/product-parameters.md)

The sampling interval is 15 minutes by default and adjustable from 5 to 60 minutes. This unit uses the default of 900 s and the limits of 300 s and 3600 s. In this unit the interval is set when the code is built.
