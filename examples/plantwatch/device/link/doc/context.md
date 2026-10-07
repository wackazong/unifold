# Context of link

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From device

| Source | What it says | What it means here |
|---|---|---|
| [device/0001 Sleep between events and advertise all the time at a long interval](../../doc/decisions/0001-sleep-between-events-and-advertise-all-the-time.md) | The firmware advertises whenever no central is connected, every 1285 ms. Connections are kept short: idle ones are closed after 30 s. Work happens in short events. | The advertising interval and the idle timeout that link sets. link reacts to events and never waits in a loop. |
| [device/0002 Only one part of the firmware touches the hardware](../../doc/decisions/0002-only-one-part-touches-the-hardware.md) | Only one part of the firmware touches the hardware and the radio stack. Everything else is hardware-independent. | link uses the radio only through `radio` and runs on a development machine against a substitute. |
| [device/0003 Sequence numbers are derived from the tick count](../../doc/decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md) | Sequence numbers rise strictly but jump at every start of the board. | link takes counts from `reading-log` and never derives them from sequence numbers. |
| [Energy budget](../../doc/references/energy-budget.md) | An advertising event may cost 12 µC. Four connections a day of 9 mC each are planned. | link does not shorten the advertising interval and closes connections that are idle. |

## From plantwatch

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0002 Define the BLE profile and the reading format once](../../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md) | The BLE profile is defined once, in a unit of its own, with a version. A change within a major version keeps older counterparts working. | link implements the profile and does not define it. The definition reaches link as the need `link-profile`. Unclear points are raised where the definition lives. |
| [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | Transfers are at-least-once. A place deletes a reading only after the next place has confirmed it. | A fetch changes nothing; only `confirm` releases readings. link sends a reading unchanged. |
| [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | The side that fetches reads the sensor stick's current tick count and converts the tick counts of the readings to UTC. | Status must carry the tick count of the moment of the request. |
| [Glossary](../../../doc/references/glossary.md) | Central: the BLE role of the side that connects to a sensor stick. Sensor id: the unchangeable identifier of a sensor stick. Reading, sequence number, tick count. | The terms of this unit. link never names what the central is. |
| [Product parameters](../../../doc/references/product-parameters.md) | Radio protocol version 1. | The major version link implements and reports. |
