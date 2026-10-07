---
unit: hal
summary: Hardware abstraction of the sensor stick board
kind: library
status: planned
provides:
  sensor-io:
    kind: library
    summary: Raw values from the soil probe and the ambient sensor, on request
  radio:
    kind: library
    summary: BLE peripheral role - advertise, accept a connection, exchange GATT data
  flash:
    kind: library
    summary: Read, write and erase blocks of memory that survive power loss
  timer:
    kind: library
    summary: Wake-up timers and a tick counter that keeps running in deep sleep
needs:
  soil-probe:
    kind: hardware
    summary: Analogue voltage that falls as the soil gets wetter
  ambient-sensor:
    kind: hardware
    summary: Light and temperature sensor on an I2C bus
---
# hal

hal is the hardware abstraction of the sensor stick board. It is the only
code that touches pins, peripherals and the radio stack of the
microcontroller. It offers what the board can do as four small libraries
whose meaning does not depend on the board: raw sensor values, a BLE
peripheral, durable blocks of memory, and time. Code that uses only these
four libraries runs unchanged on another board or on a development machine
with substitutes.

## Provides

All four libraries deliver their events and alarms one after another,
never at the same time. When no event is being handled, hal puts the board
into its lowest state that keeps time and the radio schedule. A caller does
nothing to make the board sleep.

### `sensor-io`

One call powers the sensors, measures, powers them off and returns three
raw values. The call returns within 250 ms.

| Value | Range | Meaning |
|---|---|---|
| Soil | 0 to 4095 | Output voltage of the soil probe divided by the supply voltage, times 4095. Falls as the soil gets wetter. |
| Light | 0 to 2³² − 1 | Counts of the ambient sensor. One count is the same amount of light at every brightness. |
| Temperature | −32 768 to 32 767 | Steps of 1/16 °C as the ambient sensor reports them |

Each value can be "unavailable" on its own, for example when the ambient
sensor does not answer. hal does not calibrate, filter, clamp or judge a
value.

### `radio`

A BLE peripheral with a GATT server, for one central at a time.

- **Identity.** An 8-byte identifier that is unique per board and never
  changes, and a static random device address.
- **Advertising.** The caller supplies advertising data and scan response,
  up to 31 bytes each, and an interval between 100 ms and 2 s. It may
  replace the data at any time. hal advertises whenever advertising is
  switched on and no central is connected.
- **Connection.** hal reports connect, disconnect and the ATT MTU, which is
  between 23 and 131 bytes. The caller may close the connection. It may
  set a time after which hal closes a connection that carries no request,
  and a longest duration after which hal closes any connection.
- **GATT server.** The caller declares services and characteristics once
  at start: UUID, properties, largest length, and whether an encrypted
  connection is required. hal delivers each read and write as an event and
  sends the caller's answer, which may be an ATT error. The caller sends
  notifications and indications; hal says whether there was room and
  reports when there is room again. hal keeps the subscription state of a
  characteristic and resets it at every connection.
- **Bonding.** hal carries out LE Secure Connections bonding without user
  interaction, keeps at least 4 bonds across power loss and replaces the
  bond used longest ago. It accepts a new bond only while bonding is
  open. The caller opens bonding for a duration it names.
- **Time of events.** Every event carries the tick count at which it
  happened.

Limits: transmit power is 0 dBm. hal knows nothing about the meaning of an
attribute.

### `flash`

20 blocks of 4096 bytes that keep their content without power.

| Operation | Behaviour |
|---|---|
| Read | Any range inside a block |
| Write | Whole 4-byte words. A write can only change bits from 1 to 0. |
| Erase | A whole block. Afterwards every byte is `0xFF`. |

- Each block endures at least 10 000 erases.
- When a call returns, its effect survives power loss.
- Power loss during a write leaves the words of that write undefined and
  all other words unchanged. Power loss during an erase leaves that block
  undefined and all other blocks unchanged.
- A write takes up to 1 ms per word, an erase up to 100 ms. hal fits the
  operation between radio events; the caller waits.

### `timer`

- **Tick count.** A boot counter and the seconds since this start. The
  boot counter is 1 at the first start of a board and rises by exactly one
  at every later start, also after the cell was removed. It never repeats.
  The seconds rise by one per second, also while the board sleeps, with an
  error of at most 50 ppm.
- **Alarms.** Up to 4 alarms. The caller names a value of seconds since
  start; hal calls the caller at that second, not earlier and at most
  100 ms later.

hal does not start the board while the supply voltage is too low to write
memory. A weak cell therefore does not use up boot counters in a loop.

Limit: the boot counter ends at 65 535. hal does not start the board after
that.

## Needs

### `soil-probe`

An analogue voltage between 0 V and the supply voltage that falls as the
soil gets wetter and is proportional to the supply voltage. hal switches
the supply of the probe, 2.0 V to 3.3 V. The probe draws at most 5 mA, and
its output is stable within 100 ms after power-on.

### `ambient-sensor`

One device on an I2C bus at 100 kHz that measures light up to at least
100 000 lux and temperature from −20 °C to 60 °C. It runs on 2.0 V to
3.3 V, delivers both values within 150 ms after a request, and draws at
most 1 µA when idle.

## Out of scope

- Converting raw values to percent, lux or degrees.
- Deciding when to measure, what to store and what to send.
- The meaning of GATT attributes and the layout of data in the blocks.
- Measuring the cell voltage for others. No port offers it.
- Updating the firmware over the radio.

## More

- [AGENTS.md](AGENTS.md): why the board is hidden behind four libraries
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- [Board](doc/references/board.md): pins, peripherals and memory map as planned
