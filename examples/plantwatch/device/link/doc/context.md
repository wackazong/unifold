# Context of link

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From device

### [device/0001 Sleep between events and advertise all the time at a long interval](../../doc/decisions/0001-sleep-between-events-and-advertise-all-the-time.md)

Says: the firmware advertises every 1285 ms whenever no central is
connected. It closes a connection without requests after 30 s and every
connection after 10 minutes. Work happens in short events.

Here: the advertising interval and the two times that `link` sets. `link`
reacts to events and never waits in a loop.

### [device/0002 Only one part of the firmware touches the hardware](../../doc/decisions/0002-only-one-part-touches-the-hardware.md)

Says: one part owns all access to the hardware and the radio stack. The
other parts are hardware-independent and run on a development machine.

Here: `link` uses the radio only through `radio` and is tested against a
substitute.

### [device/0003 Sequence numbers are derived from the tick count](../../doc/decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md)

Says: sequence numbers rise strictly but jump at every start of the board.

Here: `link` takes counts from `reading-log` and never derives them from two
sequence numbers.

### [device: glossary](../../doc/references/glossary.md)

Says: a reading is stored while it is in durable memory and neither
delivered nor discarded. Delivered means covered by a confirm of a central.
A start is the firmware beginning to run, not a wake-up from sleep.

Here: used unchanged. "Stored" here and in the profile mean the same.

## From plantwatch

### [plantwatch/0002 Define the BLE profile and the reading format once, in a unit of their own](../../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md)

Says: the BLE profile is defined once, in a unit of its own, with a
version. A change within a major version keeps older counterparts working.

Here: `link` implements the profile and does not define it. The definition
reaches `link` as the need `link-profile`; unclear points are raised where
the definition lives.

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

Says: transfers are at-least-once. A reading never changes, and a place
may delete it once the next place has confirmed it.

Here: a fetch changes nothing; only a confirm releases readings. `link`
sends a reading unchanged.

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

Says: at fetch time the phone reads the sensor stick's current tick count
and computes the UTC time of each reading from it.

Here: Status carries the tick count of the moment of the request.

### [plantwatch: glossary](../../../doc/references/glossary.md)

Says: a central is the BLE role of the side that connects to a sensor
stick. The sensor id is the unchangeable identifier of a sensor stick.

Here: `link` says "a central" and never names what it is. The identifier it
gets through `radio` is the sensor id.

### [plantwatch: product parameters](../../../doc/references/product-parameters.md)

Says: radio protocol version 1.

Here: the major version `link` implements and reports.
