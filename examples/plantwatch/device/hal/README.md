# hal

`hal` is the hardware abstraction of the sensor stick board. It is the only code that touches pins, peripherals and the radio stack of the microcontroller. It provides what the board can do as four small libraries whose meaning does not depend on the board: raw sensor values, a BLE peripheral, durable blocks of memory, and time. Code that uses only these four libraries runs unchanged on another board, or on a development machine with substitutes.

## Why

`hal` exists so that exactly one place knows the board. It changes when the board changes: a pin, a sensor part, the microcontroller, the radio stack of its vendor. Nothing else is a reason to touch it.

Three forces lead there. Testing: logic that is reached only through a soldered board is tested late and seldom; behind four narrow libraries a substitute can stand in for the board. Energy: with one owner of the power state, no two parts can each keep something awake. The radio stack: it comes as a binary, owns the radio and dictates when memory may be written; `hal` absorbs these constraints, so that its callers see plain calls.

The interface is four libraries and not one, so that a caller states only what it uses. The level is chosen so that `hal` needs no knowledge of the product: raw values instead of percent, GATT primitives instead of a profile, blocks instead of records. What must stay true: nothing outside this folder includes a vendor header, and nothing inside knows what a reading is.

## Capabilities

`hal` delivers the events and alarms of all four libraries one after another, never two at the same time. Whenever no event is being handled, `hal` puts the board to sleep; a caller does nothing for that. Asleep, the board keeps counting time and keeps the radio schedule, and draws the sleep current stated in the [board](docs/references/board.md) reference.

### `sensor-io`

One request powers the soil probe and the ambient sensor, measures once, powers both off and returns three raw values within 300 ms:

- soil, 0 to 4095: the output voltage of the probe divided by its supply voltage, times 4095. Higher means drier.
- light: one count is 0.01 lux at the sensor.
- temperature: one count is 1/16 °C at the sensor.

Each value can be "unavailable" on its own, for example when the ambient sensor does not answer. `hal` does not calibrate, filter, clamp or judge a value. Contract: [sensor-io](../docs/references/sensor-io.md).

### `radio`

A BLE peripheral with a GATT server, for one central at a time. The caller declares characteristics, supplies advertising data and answers every read and write. `hal` does what lies below:

- **Identity.** An 8-byte identifier that is unique per board and never changes, and a static random device address.
- **Advertising** at an interval between 100 ms and 2 s, whenever it is switched on and no central is connected.
- **Connection.** `hal` reports connect, disconnect and the ATT MTU, 23 to 131 bytes. It closes a connection on request, after a time without requests and after a longest duration; the caller sets both times.
- **Sending.** For each notification or indication `hal` says whether there was room, and reports when there is room again. It sends at least 4 notifications of 20 bytes per connection event.
- **Bonding and encryption.** `hal` bonds without user interaction, keeps at least 4 bonds across power loss, and accepts a new bond only while the caller has opened bonding. It rejects a request on a protected characteristic over an unencrypted connection by itself.
- **Time of events.** Every event carries the tick count at which it happened.

Limits: 16 characteristics, transmit power 0 dBm. `hal` knows nothing about the meaning of an attribute. Contract: [radio](../docs/references/radio.md).

### `flash`

20 blocks of 4096 bytes that keep their content without power. A write takes whole 4-byte words and can only change bits from 1 to 0; an erase takes a whole block and leaves every byte `0xFF`. A read returns within 1 ms, a write within 1 ms per word, an erase within 100 ms. Each block endures at least 10 000 erases.

When a call has returned, its effect survives power loss. Power loss during a write leaves only the words of that write undefined, power loss during an erase only that block. While the supply is below 2.1 V, `hal` refuses to write or erase, and nothing changes. Contract: [flash](../docs/references/flash.md).

### `timer`

- **Tick count.** A boot counter and the seconds since this start. The boot counter is 1 at the first start of a board, is higher at every later start, also after the cell was removed, and never repeats. The seconds rise by one per second, also while the board sleeps, with an error of at most 50 ppm.
- **Alarms.** Up to 4 alarms. The caller names a value of seconds since start; `hal` calls the caller at that second, not earlier and at most 100 ms later.

`hal` does not start the board while the supply is below 2.1 V. A weak cell therefore does not use up boot counters in a loop.

Limit: the boot counter ends at 65 535. `hal` does not start the board after that. Contract: [timer](../docs/references/timer.md).

## Needs

### `soil-probe`

An analogue voltage between 0 V and the supply voltage that falls as the soil gets wetter and is proportional to the supply voltage. `hal` switches the supply of the probe, 2.0 V to 3.3 V. The probe draws at most 5 mA, and its output is stable within 100 ms after power-on.

### `ambient-sensor`

One device on an I2C bus at 100 kHz that measures light up to at least 100 000 lux and temperature from −20 °C to 60 °C. It runs on 2.0 V to 3.3 V, delivers both values within 150 ms after a request, and draws at most 1 µA when idle.

## Out of scope

- Converting raw values to percent, lux or degrees.
- Deciding when to measure, what to keep and what to send.
- The meaning of GATT attributes and the layout of data in the blocks.
- Measuring the cell voltage for others. No capability provides it.
- Replacing the program of the board over the radio.

## Read next

1. The contracts of the four capabilities: [sensor-io](../docs/references/sensor-io.md), [radio](../docs/references/radio.md), [flash](../docs/references/flash.md), [timer](../docs/references/timer.md)
2. [docs/references/board.md](docs/references/board.md): pins, peripherals, memory map
3. [docs/explanation/context.md](docs/explanation/context.md): what `hal` inherits from above
4. [Context diagram](docs/diagrams/context.md)
5. [Decisions](docs/decisions/index.md)
