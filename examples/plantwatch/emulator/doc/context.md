# Context of emulator

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## Decisions

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0003 The emulator implements the profile independently of the firmware](../../doc/decisions/0003-the-emulator-implements-the-profile-independently.md) | The emulator is written separately, from the protocol definition alone, so that two implementations of one text show where the text is ambiguous. It says nothing about energy use, flash wear or radio timing. | No code and no behaviour is taken from another implementation. A scenario states physical values, not sensor signals. A gap in the definition is reported, not filled by guessing. |
| [plantwatch/0002 Define the BLE profile and the reading format once](../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md) | The BLE profile is defined once, with a version. A change within a major version keeps older counterparts working. | The program does not describe the profile. It states it as the need `link-profile` and follows the tolerance rules of the definition. |
| [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | A sensor stick numbers its readings in strictly increasing order and never reuses a number. Transfers are at-least-once. | Within a scenario, sequence numbers only rise, also across a simulated restart. A reading stays stored until a central confirms it. |
| [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | A reading carries a boot counter and seconds since boot, never a wall-clock time. | Simulated time appears on the radio link only as a tick count. A scenario has no dates. |

## References

| Source | What it says | What it means here |
|---|---|---|
| [Conventions: measured quantities](../../doc/references/conventions.md) | Soil moisture 0 to 100 percent in steps of 0.1; light 0 to 100 000 lux in steps of 1; temperature -20 to 60 °C in steps of 0.1. An unmeasured quantity is absent, not zero. | The allowed values and the rounding in the scenario format; `null` in a track makes a quantity absent. |
| [Conventions: identifiers](../../doc/references/conventions.md) | A sensor id is 8 bytes, written as 16 lower-case hex digits. A sequence number is an unsigned 32-bit integer. | The form of `sensor_id` and the range of `first_sequence_number` in a scenario. |
| [Conventions: HTTP ports](../../doc/references/conventions.md) | Bodies are JSON in UTF-8. Field names are lower-case with underscores. An error has `code` and `message`. A request that repeats an earlier successful request succeeds again. | The form of the scenario-control API. Requests name absolute targets so that a repetition changes nothing. |
| [Glossary](../../doc/references/glossary.md) | Scenario: a scripted course of sensor values over simulated time, used instead of real hardware. Sensor stick: the device in the pot. Central: the BLE side that connects to it. Reading: one set of measurements, never a single value. Tick count: boot counter and seconds since boot. | The documents of this unit use these terms unchanged. |
| [Product parameters](../../doc/references/product-parameters.md) | Sampling interval 15 minutes by default, 5 to 60 minutes. A sensor stick keeps at least 2 880 readings and overwrites the oldest when full. Radio protocol version 1. | The default and the range of `sampling_interval_s`; the capacity of the simulated sensor stick and its overflow behaviour; the profile version the program implements. |
