# Context of store

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From device

| Source | What it says | What it means here |
|---|---|---|
| [device/0002 Only one part of the firmware touches the hardware](../../doc/decisions/0002-only-one-part-touches-the-hardware.md) | Only one part of the firmware touches the hardware. Everything else is hardware-independent. | store reaches memory only through `flash` and runs on a development machine with a substitute that can cut power at any word. |
| [device/0003 Sequence numbers are derived from the tick count](../../doc/decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md) | Sequence numbers rise strictly but jump at every start of the board. | store orders and compares by sequence number and never computes a count from two numbers. |
| [device/0001 Sleep between events and advertise all the time at a long interval](../../doc/decisions/0001-sleep-between-events-and-advertise-all-the-time.md) | Work happens in short events; between them the board sleeps. Nothing runs in the background. | store does all its work inside the call that needs it: an erase happens while a reading is accepted. There is no clean-up task. |
| [Energy budget](../../doc/references/energy-budget.md) | One reading may cost 600 µC including storing it. | A slot write and, once per block, an erase of about 255 µC fit into this. A layout that erases per reading would not. |

## From plantwatch

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | A reading is never changed after it has been taken. A place deletes a reading only after the next place has confirmed it. | A slot is written once. A reading leaves the log only through a mark from outside, apart from overflow. |
| [Conventions: delivery](../../../doc/references/conventions.md) | A sender deletes an item only after the receiver has confirmed it. A repeated confirmation succeeds. | Read changes nothing. Mark as delivered may be repeated. |
| [Product parameters](../../../doc/references/product-parameters.md) | A sensor stick keeps at least 2 880 readings, 30 days at the default sampling interval. When it is full, the oldest undelivered reading is overwritten. | The guaranteed capacity and the behaviour when full. |
| [Glossary](../../../doc/references/glossary.md) | Reading: one set of measurements with a sequence number and a time. Sequence number: strictly increasing, never reused. Tick count: boot counter and seconds since that boot. | The content of a slot. |
