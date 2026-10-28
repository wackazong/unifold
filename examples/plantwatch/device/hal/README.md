# hal

`hal` is the hardware abstraction of the sensor stick board. It is the only code that touches pins, peripherals and the radio stack of the microcontroller. It provides what the board can do as four small libraries whose meaning does not depend on the board: raw sensor values, a BLE peripheral, durable blocks of memory, and time. Code that uses only these four libraries runs unchanged on another board, or on a development machine with substitutes.

## Why

`hal` exists so that exactly one place knows the board. It changes when the board changes: a pin, a sensor part, the microcontroller, the radio stack of its vendor. Nothing else is a reason to touch it.

Three forces lead there. Testing: logic that is reached only through a soldered board is tested late and seldom; behind four narrow libraries a substitute can stand in for the board. Energy: with one owner of the power state, no two parts can each keep something awake. The radio stack: it comes as a binary, owns the radio and dictates when memory may be written; `hal` absorbs these constraints, so that its callers see plain calls.

The interface is four libraries and not one, so that a caller states only what it uses. The level is chosen so that `hal` needs no knowledge of the product: raw values instead of percent, GATT primitives instead of a profile, blocks instead of records. What must stay true: nothing outside this folder includes a vendor header, and nothing inside knows what a reading is.

## Capabilities

`hal` delivers the events and alarms of all four libraries one after another, never two at the same time. Whenever no event is being handled, `hal` puts the board to sleep; a caller does nothing for that. Asleep, the board keeps counting time and keeps the radio schedule, and draws the sleep current stated in the [board](docs/references/board.md) reference.

## Read next

1. The contracts of the four capabilities: [sensor-io](../docs/references/sensor-io.md), [radio](../docs/references/radio.md), [flash](../docs/references/flash.md), [timer](../docs/references/timer.md)
2. [docs/references/board.md](docs/references/board.md): pins, peripherals, memory map
3. [docs/explanation/context.md](docs/explanation/context.md): what `hal` inherits from above
4. [Context diagram](docs/diagrams/context.md)
5. [Decisions](docs/decisions/index.md)
