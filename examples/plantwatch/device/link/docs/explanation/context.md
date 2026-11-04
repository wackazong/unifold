# Context of link

What this unit takes over from the units above, and what each item means here.

## From device

### [device/0001 Sleep between events and advertise all the time at a long interval](../../../docs/decisions/0001-sleep-between-events-and-advertise-all-the-time.md)

The firmware advertises every 1285 ms whenever no central is connected. It closes a connection without requests after 30 s and every connection after 10 minutes. Work happens in short events.

`link` sets the advertising interval and the two times. `link` reacts to events and never waits in a loop.

### [device/0002 Only one part of the firmware touches the hardware](../../../docs/decisions/0002-only-one-part-touches-the-hardware.md)

One part owns all access to the hardware and the radio stack. The other parts are hardware-independent and run on a development machine. `link` uses the radio only through `radio` and is tested against a substitute.

### [device/0003 Sequence numbers are derived from the tick count](../../../docs/decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md)

Sequence numbers rise strictly but jump at every start of the board. `link` takes counts from `reading-log` and never derives them from two sequence numbers.

### [device: glossary](../../../docs/references/glossary.md)

A reading is stored while it is in durable memory and neither delivered nor discarded. Delivered means covered by a confirm of a central. A start is the firmware beginning to run, not a wake-up from sleep.

`link` uses these terms unchanged. "Stored" here and in the profile mean the same.

## From plantwatch

### [plantwatch/0008 Define the BLE profile and the reading format as references of plantwatch](../../../../docs/decisions/0008-define-the-profile-and-the-reading-format-as-references-of-plantwatch.md)

The BLE profile and the reading schema are references of plantwatch. Every connection that carries the profile names it as its contract; a reading travels inside the profile and the public API, and whoever reads or writes readings cites the schema. Both keep a version; a change within a major version keeps older counterparts working.

`ble-link` names the profile as its contract. `link` implements it and does not define it; unclear points are raised at the root.

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

Transfers are at-least-once. A reading never changes, and a place may delete it once the next place has confirmed it. In `link`, a fetch changes nothing; only a confirm releases readings. `link` sends a reading unchanged.

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../../docs/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

At fetch time the phone reads the sensor stick's current tick count and computes the UTC time of each reading from it. Status therefore carries the tick count of the moment of the request.

### [plantwatch: glossary](../../../../docs/references/glossary.md)

A central is the BLE role of the side that connects to a sensor stick. The sensor id is the unchangeable identifier of a sensor stick. `link` says "a central" and never names what it is. The identifier it gets through `radio` is the sensor id.

### [plantwatch: product parameters](../../../../docs/references/product-parameters.md)

The radio protocol version is 1. `link` implements and reports this major version.
