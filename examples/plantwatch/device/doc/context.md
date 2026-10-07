# Context of device

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From plantwatch

### [plantwatch/0001 The phone relays between sensor stick and server](../../doc/decisions/0001-the-phone-relays-between-sensor-and-server.md)

Says: a sensor stick has BLE and nothing else, holds no network credentials,
and must keep readings until a phone has taken them.

Here: the firmware has one radio interface, `ble-link`, and durable memory
for readings. It never tries to reach anything by itself.

### [plantwatch/0002 Define the BLE profile and the reading format once, in a unit of their own](../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md)

Says: the BLE profile is defined once, in a unit of its own, with a version.

Here: the firmware states the profile as the need `link-profile`,
implements that text and adds nothing to it.

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

Says: a sensor stick numbers readings in strictly increasing order and never
reuses a number. A reading never changes. A place may delete a reading once
the next place has confirmed it.

Here: the invariants on identity and release in the
[architecture](architecture.md). Numbers must survive power loss, which
leads to
[0003](decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md).

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

Says: a reading carries a boot counter and the seconds since that boot. The
sensor stick never holds a wall-clock time.

Here: the firmware has no clock setting and no date. The boot counter
rises at every start and never repeats.

### [plantwatch: product parameters, sampling interval and battery life](../../doc/references/product-parameters.md)

Says: the sampling interval is 15 minutes by default, adjustable from 5 to
60 minutes. A sensor stick runs at least 12 months on one CR2032 cell.

Here: 900 s by default, a build setting between 300 s and 3600 s. The
average current of 19.4 µA in the
[energy budget](references/energy-budget.md).

### [plantwatch: product parameters, readings kept](../../doc/references/product-parameters.md)

Says: a sensor stick keeps at least 2 880 readings, 30 days at the default
interval, and overwrites the oldest undelivered one when it is full. Radio
protocol version 1.

Here: the capacity and the overflow behaviour of `ble-link`, and the major
version the firmware implements.

### [plantwatch: conventions, measured quantities](../../doc/references/conventions.md)

Says: soil moisture in percent of the calibrated range, light in lux,
temperature in °C. A quantity that could not be measured is absent, not zero.

Here: the quantities of a reading, and the rule for a sensor that fails.

### [plantwatch: glossary](../../doc/references/glossary.md)

Says: a sensor stick is the hardware device in the pot of one plant. A
central is the BLE side that connects to it, normally a phone.

Here: used unchanged, as are reading, sequence number, sampling interval
and tick count. The documents say "a central" and never name what it is.
Terms only the firmware uses are in its own
[glossary](references/glossary.md).
