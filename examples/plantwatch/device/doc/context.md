# Context of device

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## Decisions

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0001 The phone relays between sensor stick and server](../../doc/decisions/0001-the-phone-relays-between-sensor-and-server.md) | A sensor stick has BLE and nothing else, holds no network credentials, and must keep readings until a phone has taken them. The phone may be away for days. | The firmware has one radio interface, `ble-link`, and durable memory for readings. It never tries to reach anything by itself. |
| [plantwatch/0002 Define the BLE profile and the reading format once](../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md) | The BLE profile is defined once, in a unit of its own, with a version. | The firmware states the profile as the need `link-profile`. It implements the text and does not add to it. |
| [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | A sensor stick numbers readings in strictly increasing order and never reuses a number. A reading never changes. A place deletes a reading only after the next place has confirmed it. | The invariants on identity and release in the architecture. Sequence numbers must survive power loss, which leads to [device/0003](decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md). |
| [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | A reading carries a boot counter and the seconds since that boot. The sensor stick never holds a wall-clock time. | The firmware has no clock setting and no date. The boot counter must rise at every start and never repeat. |

## References

| Source | What it says | What it means here |
|---|---|---|
| [Product parameters: sampling interval](../../doc/references/product-parameters.md) | 15 minutes by default, adjustable from 5 to 60 minutes. | 900 s by default. In this firmware the interval is a build setting between 300 s and 3600 s; nothing changes it at run time. |
| [Product parameters: battery life](../../doc/references/product-parameters.md) | At least 12 months on one CR2032 cell at the default interval. | The average current of 19.4 µA in the energy budget, and with it the whole control flow. |
| [Product parameters: readings kept](../../doc/references/product-parameters.md) | At least 2 880 readings, 30 days at the default interval. When the sensor stick is full, the oldest undelivered reading is overwritten. | The guaranteed capacity and the overflow behaviour of `ble-link`. |
| [Product parameters: radio protocol version](../../doc/references/product-parameters.md) | Version 1. | The major version the firmware implements. |
| [Conventions: measured quantities](../../doc/references/conventions.md) | Soil moisture in percent of the calibrated range, light in lux, temperature in °C, each with a range and a resolution. A quantity that could not be measured is absent, not zero. | The quantities of a reading and the rule for a failed sensor. |
| [Conventions: delivery](../../doc/references/conventions.md) | A transfer may deliver an item more than once. A sender deletes only after the receiver has confirmed. | The firmware may send a reading again and releases it only after a confirm. |
| [Glossary](../../doc/references/glossary.md) | Sensor stick: the hardware device in the pot. Reading: one set of measurements taken at the same moment. Central: the BLE side that connects to a sensor stick. Tick count: boot counter and seconds since that boot. Sequence number, sampling interval, sensor id. | The firmware's documents use these terms unchanged. They say "a central" and never name what the central is. |
