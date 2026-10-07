# Context of hal

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From device

### [device/0002 Only one part of the firmware touches the hardware](../../doc/decisions/0002-only-one-part-touches-the-hardware.md)

Says: one part owns all access to registers, pins and the radio stack and
offers it as libraries without hardware types. The other parts run on a
development machine.

Here: `hal` is that part. No function of its four libraries hands out a
board-specific type, so each can be replaced by a substitute.

### [device/0001 Sleep between events and advertise all the time at a long interval](../../doc/decisions/0001-sleep-between-events-and-advertise-all-the-time.md)

Says: the firmware has no loop that waits. It sleeps unless an alarm or the
radio wakes it, and it advertises every 1285 ms.

Here: `hal` owns the sleep state and enters it whenever no event is being
handled. 1285 ms lies inside the range `radio` offers.

### [device/0003 Sequence numbers are derived from the tick count](../../doc/decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md)

Says: a sequence number is computed from the boot counter and a count
within that start. A boot counter that repeated would repeat numbers.

Here: `hal` counts a start before `timer` reports a tick count, and does not
start the board when it could not count the start.

### [device: energy budget](../../doc/references/energy-budget.md)

Says: the firmware may draw 19.4 µA on average. The plan gives 2.0 µA to
sleep, 600 µC to one reading and 12 µC to one advertising event.

Here: these three figures are `hal`'s to keep. A change of clock source,
sensor supply or transmit power is checked against them.

### [device: glossary](../../doc/references/glossary.md)

Says: a start is the firmware beginning to run, not a wake-up from sleep.
An event is an alarm or a radio occurrence that wakes the board. A raw
value is a number as a sensor delivers it, before calibration.

Here: the words of the four contracts, used unchanged.

## From plantwatch

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

Says: a sensor stick has no wall clock. Its time is a boot counter and the
seconds since that boot.

Here: `timer` provides exactly this pair and nothing that looks like a
date.

### [plantwatch: glossary](../../../doc/references/glossary.md)

Says: the tick count is a boot counter and the seconds since that boot. The
sensor id is the unchangeable identifier of a sensor stick. A central is
the BLE side that connects to a sensor stick.

Here: the terms of `timer` and `radio`. The identifier that `radio`
reports serves as sensor id.

### [plantwatch: conventions, identifiers](../../../doc/references/conventions.md)

Says: a sensor id has 8 bytes.

Here: the length of the identifier that `radio` reports.

### [plantwatch: product parameters](../../../doc/references/product-parameters.md)

Says: a sensor stick runs at least 12 months on one CR2032 cell and keeps
at least 2 880 readings.

Here: the cell sets the supply range of 2.0 V to 3.0 V, and with it the
2.1 V below which `hal` writes nothing. The number of readings sets the 20
blocks of `flash`.
