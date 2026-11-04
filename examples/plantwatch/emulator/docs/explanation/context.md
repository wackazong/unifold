# Context of emulator

What this unit takes over from the units above, and what each item means here.

## From plantwatch

### [plantwatch/0008 Define the BLE profile and the reading format as references of plantwatch](../../../docs/decisions/0008-define-the-profile-and-the-reading-format-as-references-of-plantwatch.md)

The BLE profile and the reading schema are references of plantwatch. Every connection that carries the profile names it as its contract; a reading travels inside the profile and the public API, and whoever reads or writes readings cites the schema. Both keep a version; a change within a major version keeps older counterparts working.

`ble-link` names the profile as its contract. The program is built from that text and follows its tolerance rules.

### [plantwatch/0003 The emulator implements the profile independently of the firmware](../../../docs/decisions/0003-the-emulator-implements-the-profile-independently.md)

The emulator is written separately, from the protocol definition alone, so that two implementations of one text show where the text is ambiguous. It says nothing about energy use, flash wear or radio timing.

No code and no behaviour is taken from another implementation. A scenario states physical values, not sensor signals. A gap in the definition is reported, not filled by guessing.

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

A sensor stick numbers its readings in strictly increasing order and never reuses a number. Transfers are at-least-once. Within a scenario, sequence numbers only rise, also across a simulated restart. A reading stays stored until a central confirms it.

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../docs/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

A reading carries a boot counter and the seconds since that boot, never a wall-clock time. Simulated time appears on the radio link only as a tick count. A scenario has no dates.

### [plantwatch: conventions, measured quantities](../../../docs/references/conventions.md#measured-quantities)

The convention defines three quantities:

- Soil moisture goes from 0 to 100 percent, with a resolution of 0.1.
- Light goes from 0 to 100 000 lux, with a resolution of 1.
- Temperature goes from −20 to 60 °C, with a resolution of 0.1.

A quantity that could not be measured is absent, not zero. The [scenario format](../../../docs/references/scenario-format.md) uses these allowed values and this rounding. `null` in a track makes a quantity absent.

### [plantwatch: conventions, identifiers](../../../docs/references/conventions.md#identifiers)

A sensor id is 8 bytes, written as 16 lower-case hex digits. A sequence number is an unsigned 32-bit integer. These rules set the form of `sensor_id` and the range of `first_sequence_number` in a scenario.

### [plantwatch: conventions, HTTP ports](../../../docs/references/conventions.md#http-ports)

Bodies are JSON in UTF-8 with lower-case field names with underscores. An error has `code` and `message`. A request that repeats an earlier successful request succeeds again.

These rules set the form of the [scenario-control API](../../../docs/references/scenario-control/index.md). Requests name absolute targets, so that a repetition changes nothing.

### [plantwatch: glossary](../../../docs/references/glossary.md)

A scenario is a scripted course of sensor values over simulated time, used instead of real hardware. A central is the BLE side that connects to a sensor stick. These terms are used unchanged, as are sensor stick, reading and tick count. The unit's own terms are in its [glossary](../references/glossary.md).

### [plantwatch: product parameters](../../../docs/references/product-parameters.md)

The sampling interval is 15 minutes by default and ranges from 5 to 60 minutes. A sensor stick keeps at least 2 880 readings and overwrites the oldest when full. The radio protocol version is 1.

These parameters set the default and the range of `sampling_interval_s`, the capacity and the overflow of the simulated sensor stick, and the profile version.
