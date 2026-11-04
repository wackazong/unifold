# Context of device

What this unit takes over from the units above, and what each item means here.

## From plantwatch

### [plantwatch/0008 Define the BLE profile and the reading format as references of plantwatch](../../../docs/decisions/0008-define-the-profile-and-the-reading-format-as-references-of-plantwatch.md)

The BLE profile and the reading schema are references of plantwatch. Every connection that carries the profile names it as its contract; a reading travels inside the profile and the public API, and whoever reads or writes readings cites the schema. Both keep a version; a change within a major version keeps older counterparts working.

`ble-link` names the profile as its contract. The firmware implements that text and adds nothing to it.

### [plantwatch/0001 The phone relays between sensor stick and server](../../../docs/decisions/0001-the-phone-relays-between-sensor-and-server.md)

A sensor stick has BLE and nothing else, holds no network credentials, and must keep readings until a phone has taken them. The firmware has one radio interface, `ble-link`, and durable memory for readings. It never tries to reach anything by itself.

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

A sensor stick numbers readings in strictly increasing order and never reuses a number. A reading never changes. A place may delete a reading once the next place has confirmed it. The [invariants](invariants.md) state the rules on identity and release. Numbers must survive power loss, which leads to [0003](../decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md).

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../docs/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

A reading carries a boot counter and the seconds since that boot. The sensor stick never holds a wall-clock time. The firmware has no clock setting and no date. The boot counter rises at every start and never repeats.

### [plantwatch: product parameters, sampling interval and battery life](../../../docs/references/product-parameters.md)

The sampling interval is 15 minutes by default, adjustable from 5 to 60 minutes. A sensor stick runs at least 12 months on one CR2032 cell. In the firmware the interval is 900 s by default, a build setting between 300 s and 3600 s. The [energy budget](../references/energy-budget.md) keeps the average current at 19.4 µA.

### [plantwatch: product parameters, readings kept](../../../docs/references/product-parameters.md)

A sensor stick keeps at least 2 880 readings, 30 days at the default interval, and overwrites the oldest undelivered one when it is full. The radio protocol version is 1. These parameters set the capacity and the overflow behaviour of `ble-link`, and the major version the firmware implements.

### [plantwatch: conventions, measured quantities](../../../docs/references/conventions.md#measured-quantities)

Soil moisture is given in percent of the calibrated range, light in lux and temperature in °C. A quantity that could not be measured is absent, not zero. The convention sets the quantities of a reading, and the rule for a sensor that fails.

### [plantwatch: glossary](../../../docs/references/glossary.md)

A sensor stick is the hardware device in the pot of one plant. A central is the BLE side that connects to it, normally a phone.

These terms are used unchanged, as are reading, sequence number, sampling interval and tick count. The documents say "a central" and never name what it is. Terms only the firmware uses are in its own [glossary](../references/glossary.md).
