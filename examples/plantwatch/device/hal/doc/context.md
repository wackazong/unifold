# Context of hal

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From device

| Source | What it says | What it means here |
|---|---|---|
| [device/0002 Only one part of the firmware touches the hardware](../../doc/decisions/0002-only-one-part-touches-the-hardware.md) | Only one part of the firmware touches registers, pins and the radio stack. Everything else is hardware-independent. | hal is that part. Its four libraries carry no board-specific type. |
| [device/0001 Sleep between events and advertise all the time at a long interval](../../doc/decisions/0001-sleep-between-events-and-advertise-all-the-time.md) | The firmware has no loop that waits. It sleeps unless a timer or the radio wakes it, and it advertises every 1285 ms. | hal owns the sleep state and enters it whenever no event is being handled. The advertising interval is inside the range `radio` offers. |
| [device/0003 Sequence numbers are derived from the tick count](../../doc/decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md) | A sequence number is computed from the boot counter and a count within the boot, so a boot counter that repeats would repeat sequence numbers. | The boot counter is stored before `timer` reports it, and it survives everything short of erasing the chip. |
| [Energy budget](../../doc/references/energy-budget.md) | The firmware may draw 19.4 µA on average. The plan assigns 2.0 µA to sleep, 600 µC to one reading and 12 µC to one advertising event. | These three figures are hal's to keep. A change of clock source, sensor supply or transmit power is checked against them. |

## From plantwatch

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | A sensor stick has no wall clock. Its time is a boot counter and the seconds since that boot. | `timer` provides exactly this pair and nothing that looks like a date. |
| [Glossary](../../../doc/references/glossary.md) | Tick count: a boot counter and the seconds since that boot. Sensor id: the unchangeable identifier of a sensor stick. Central: the BLE side that connects to a sensor stick. | The terms of the `timer` and `radio` libraries. The identifier that `radio` reports serves as sensor id. |
| [Conventions: identifiers](../../../doc/references/conventions.md) | A sensor id has 8 bytes. | The length of the identifier that `radio` reports. |
| [Product parameters](../../../doc/references/product-parameters.md) | A sensor stick runs at least 12 months on one CR2032 cell and keeps at least 2 880 readings. | The cell sets the supply range of 2.0 V to 3.0 V and the peak current the board may draw. The number of readings sets the size of the `flash` region. |
