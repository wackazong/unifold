# Context of emulator

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From plantwatch

### [plantwatch/0003 The emulator implements the profile independently of the firmware](../../doc/decisions/0003-the-emulator-implements-the-profile-independently.md)

Says: the emulator is written separately, from the protocol definition
alone, so that two implementations of one text show where the text is
ambiguous. It says nothing about energy use, flash wear or radio timing.

Here: no code and no behaviour is taken from another implementation. A
scenario states physical values, not sensor signals. A gap in the
definition is reported, not filled by guessing.

### [plantwatch/0002 Define the BLE profile and the reading format once, in a unit of their own](../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md)

Says: the BLE profile is defined once, with a version. A change within a
major version keeps older counterparts working.

Here: the program does not describe the profile. It states it as the need
`link-profile` and follows the tolerance rules of the definition.

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

Says: a sensor stick numbers its readings in strictly increasing order and
never reuses a number. Transfers are at-least-once.

Here: within a scenario, sequence numbers only rise, also across a
simulated restart. A reading stays stored until a central confirms it.

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

Says: a reading carries a boot counter and the seconds since that boot,
never a wall-clock time.

Here: simulated time appears on the radio link only as a tick count. A
scenario has no dates.

### [plantwatch: conventions, measured quantities](../../doc/references/conventions.md)

Says: soil moisture 0 to 100 percent, resolution 0.1; light 0 to 100 000
lux, resolution 1; temperature −20 to 60 °C, resolution 0.1. A quantity
that could not be measured is absent, not zero.

Here: the allowed values and the rounding in the
[scenario format](references/scenario-format.md). `null` in a track makes
a quantity absent.

### [plantwatch: conventions, identifiers](../../doc/references/conventions.md)

Says: a sensor id is 8 bytes, written as 16 lower-case hex digits. A
sequence number is an unsigned 32-bit integer.

Here: the form of `sensor_id` and the range of `first_sequence_number` in
a scenario.

### [plantwatch: conventions, HTTP ports](../../doc/references/conventions.md)

Says: bodies are JSON in UTF-8 with lower-case field names with
underscores. An error has `code` and `message`. A request that repeats an
earlier successful request succeeds again.

Here: the form of the
[scenario-control API](references/scenario-control-api.md). Requests name
absolute targets, so that a repetition changes nothing.

### [plantwatch: glossary](../../doc/references/glossary.md)

Says: a scenario is a scripted course of sensor values over simulated
time, used instead of real hardware. A central is the BLE side that
connects to a sensor stick.

Here: used unchanged, as are sensor stick, reading and tick count. The
unit's own terms are in its [glossary](references/glossary.md).

### [plantwatch: product parameters](../../doc/references/product-parameters.md)

Says: sampling interval 15 minutes by default, 5 to 60 minutes. A sensor
stick keeps at least 2 880 readings and overwrites the oldest when full.
Radio protocol version 1.

Here: the default and the range of `sampling_interval_s`; the capacity and
the overflow of the simulated sensor stick; the profile version.
