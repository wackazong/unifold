# Context of store

What this unit inherits from the levels above. This is the only file of the unit that links upward. Each item is restated so that the unit can be understood when the link is not available.

## From device

### [device/0002 Only one part of the firmware touches the hardware](../../../docs/decisions/0002-only-one-part-touches-the-hardware.md)
<!-- unifold:cites sha=c5740edf -->

Says: one part owns all hardware access. The other parts are hardware-independent and run on a development machine.

Here: `store` reaches memory only through `flash` and is tested with a substitute that can cut power at any word.

### [device/0003 Sequence numbers are derived from the tick count](../../../docs/decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md)
<!-- unifold:cites sha=f6e3de04 -->

Says: sequence numbers rise strictly but jump at every start of the board.

Here: `store` orders and compares by sequence number and never computes a count from two numbers.

### [device/0001 Sleep between events and advertise all the time at a long interval](../../../docs/decisions/0001-sleep-between-events-and-advertise-all-the-time.md)
<!-- unifold:cites sha=6158570e -->

Says: work happens in short events; between them the board sleeps. Nothing runs in the background.

Here: `store` does all its work inside the call that needs it: an erase happens while a reading is accepted. There is no clean-up task.

### [device: energy budget](../../../docs/references/energy-budget.md)
<!-- unifold:cites sha=6acc06b8 -->

Says: one reading may cost 600 µC. Of that, 15 µC are for writing it to memory, the share of a block erase included.

Here: a slot write and, once per 204 readings, an erase of about 255 µC fit into this. A layout that erased per reading would not.

### [device: glossary](../../../docs/references/glossary.md)
<!-- unifold:cites sha=944e7489 -->

Says: a reading is stored while it is in durable memory and neither delivered nor discarded. Delivered means covered by a confirm of a central; the mark is the sequence number up to which that holds.

Here: the words of `reading-log`. Overflow, block and substitute are used as defined there too.

## From plantwatch

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)
<!-- unifold:cites sha=cdc44cc5 -->

Says: a reading is never changed after it has been taken. A place may delete a reading as soon as the next place has confirmed it.

Here: a slot is written once. A reading leaves the log only through a mark from outside, or through overflow.

### [plantwatch: product parameters](../../../../docs/references/product-parameters.md)
<!-- unifold:cites sha=b11fccd4 -->

Says: a sensor stick keeps at least 2 880 readings, 30 days at the default sampling interval. When it is full, the oldest undelivered reading is overwritten.

Here: the guaranteed capacity, and the behaviour when full.

### [plantwatch: glossary](../../../../docs/references/glossary.md)
<!-- unifold:cites sha=082ae761 -->

Says: a reading is one set of measurements with a sequence number and a time. A sequence number is strictly increasing and never reused.

Here: the content of a slot, and the only key of the log.
