# Context of sampling

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From device

| Source | What it says | What it means here |
|---|---|---|
| [device/0003 Sequence numbers are derived from the tick count](../../doc/decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md) | The sequence number of a reading is the boot counter times 262 144 plus the count of readings since that start, beginning with 1. Nothing is stored for it. | sampling computes the number this way and relies on `timer` for a boot counter that never repeats. It stops taking readings when the boot counter exceeds 16 383 or the count exceeds 262 143. |
| [device/0002 Only one part of the firmware touches the hardware](../../doc/decisions/0002-only-one-part-touches-the-hardware.md) | Only one part of the firmware touches the hardware. Everything else is hardware-independent. | sampling sees sensors only as raw numbers through `sensor-io`, and runs on a development machine with a table of raw values. |
| [device/0001 Sleep between events and advertise all the time at a long interval](../../doc/decisions/0001-sleep-between-events-and-advertise-all-the-time.md) | The firmware has no loop that waits. Work happens in short events, then the board sleeps. | sampling does all work for a reading inside one alarm, sets the next alarm and returns. |
| [Energy budget](../../doc/references/energy-budget.md) | One reading may cost 600 µC, most of it for powering the soil probe once. | One request for raw values per reading. |

## From plantwatch

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | A sensor stick numbers its readings in strictly increasing order and never reuses a number. A reading is never changed after it has been taken. | The guarantees "sequence numbers rise strictly" and "a reading does not change" of `readings`. |
| [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | A reading carries a boot counter and the seconds since that boot instead of a time. | sampling stamps a reading with the tick count of the moment of measuring. |
| [Conventions: measured quantities](../../../doc/references/conventions.md) | Soil moisture in percent of the calibrated range, 0 to 100, resolution 0.1. Light in lux, 0 to 100 000, resolution 1. Temperature in °C, −20 to 60, resolution 0.1. A quantity that could not be measured is absent, not zero. | Units, ranges and rounding of the calibration; the rule "absent, not wrong". |
| [Glossary](../../../doc/references/glossary.md) | Reading: one set of measurements taken at the same moment, with a sequence number and a time; never a single value. Sampling interval: the time between two readings. Tick count: boot counter and seconds since that boot. | The terms of this unit. The three quantities of one reading come from one request for raw values. |
| [Product parameters](../../../doc/references/product-parameters.md) | The sampling interval is 15 minutes by default and adjustable from 5 to 60 minutes. | The default of 900 s and the limits of 300 s and 3600 s. In this firmware the interval is adjusted when the firmware is built. |
