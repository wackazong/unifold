# Board

The pins, peripherals and memory regions of the sensor stick board that `hal`
uses. All values are planned values for board revision A; no board exists
yet.

## Microcontroller

| Property | Value |
|---|---|
| Part | nRF52832, QFN48, 512 kB flash, 64 kB RAM |
| Supply | CR2032 cell, 3.0 V new, usable down to 2.0 V. Internal DC/DC converter on. |
| High-frequency clock | 32 MHz crystal, running only while the radio or the ADC needs it |
| Low-frequency clock | 32.768 kHz crystal, ±20 ppm at 25 °C, always running |
| Radio stack | The vendor's BLE peripheral stack as a binary, peripheral role only |

## Pins

| Pin | Direction | Connected to | Note |
|---|---|---|---|
| P0.00, P0.01 | | 32.768 kHz crystal | |
| P0.02 (AIN0) | analogue in | Output of the soil probe | Through 1 kΩ, 100 nF to ground |
| P0.03 | out | Supply switch of the soil probe | High: probe powered |
| P0.04 | out | Supply switch of the ambient sensor | High: sensor powered |
| P0.26 | in/out | I2C SDA | 10 kΩ pull-up to the switched sensor supply |
| P0.27 | out | I2C SCL | 10 kΩ pull-up to the switched sensor supply |
| P0.06 | out | Test pad, debug output | Not driven in release builds |
| SWDIO, SWDCLK | | Programming header | Firmware is written here |
| P0.21 (reset) | in | Programming header | No button on the board |
| ANT | | Printed 2.4 GHz antenna | |

All other pins are unconnected and configured as disconnected inputs.

## Peripherals

| Peripheral | Used for | Setting |
|---|---|---|
| SAADC | Soil value of `sensor-io` | 12 bit, input AIN0, reference VDD/4, gain 1/4, 8 times oversampling. The result is the ratio to the supply voltage. |
| TWIM0 | Ambient sensor of `sensor-io` | 100 kHz, address `0x44`. Enabled only during a measurement. |
| RTC1 | Seconds and alarms of `timer` | Low-frequency clock, prescaler for 8 Hz, 4 compare channels |
| RTC0, TIMER0, RADIO | Owned by the radio stack | Not touched by `hal` directly |
| NVMC, through the radio stack | `flash`, boot counter, bonds | The stack schedules writes and erases between radio events |
| POWER | Supply supervision | Power-fail warning at 2.1 V. Below it `hal` starts no write and no erase. |
| GPIO | Supply switches, test pad | |

## Sequence of one measurement

| Step | Duration |
|---|---|
| Switch on probe and ambient sensor | |
| Wait for the probe output to settle | 100 ms |
| Convert the soil value; request light and temperature | 1 ms |
| Switch off the probe; wait for the ambient sensor | up to 150 ms |
| Read light and temperature; switch off the ambient sensor | 2 ms |

The processor sleeps during both waits.

## Ambient sensor

The part is not selected yet. `hal` assumes: one I2C device at address
`0x44`, a single-shot command that measures light and temperature, light
as a mantissa and an exponent that `hal` combines into counts of 0.01 lux,
temperature as a signed number in steps of 1/16 °C.

## Memory map

| Region | Address | Size | Content |
|---|---|---|---|
| Radio stack | `0x00000` to `0x18FFF` | 100 kB | Vendor binary |
| Firmware | `0x19000` to `0x67FFF` | 316 kB | The firmware image |
| Blocks of `flash` | `0x68000` to `0x7BFFF` | 20 blocks, 80 kB | Block n starts at `0x68000` + n × `0x1000` |
| Boot counter | `0x7C000` to `0x7CFFF` | 1 block | See [decision 0002](../decisions/0002-count-boots-as-cleared-bits-in-a-block-of-its-own.md) |
| Bonds | `0x7D000` to `0x7EFFF` | 2 blocks | Keys of bonded centrals, managed by the radio stack |
| Reserved | `0x7F000` to `0x7FFFF` | 1 block | Empty, except while the boot counter block is erased |

One block is one flash page of the microcontroller: 4096 bytes, erased as
a whole, 10 000 erase cycles.

## Currents

| State | Current | Used by |
|---|---|---|
| Sleep, low-frequency clock and RTC running, RAM kept | 2.0 µA | Everything between events |
| Processor running | 4 mA | Event handling |
| Radio transmitting at 0 dBm | 6 mA | Advertising, connection events |
| Soil probe powered | 5 mA | 100 ms per measurement |
| Ambient sensor measuring | 0.3 mA | 150 ms per measurement |
| Flash erase | 3 mA for 85 ms | One block |
