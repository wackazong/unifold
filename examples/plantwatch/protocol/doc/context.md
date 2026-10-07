# Context of protocol

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## Decisions

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0002 Define the BLE profile and the reading format once](../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md) | The profile and the reading format are defined in one unit that no implementer owns. Both carry a version. A change within a major version keeps older counterparts working. | This unit is that definition. The version rules in both contracts carry out the last sentence. A change starts here and is decided where the decision lives. |
| [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | Every hop delivers at least once. A reading is identified by sensor id and sequence number, is never changed, and a receiver accepts one it already has. | The schema defines identity and immutability. Fetch and confirm are an at-least-once transfer. |
| [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | A reading carries a boot counter and seconds since boot. The side that fetches converts to UTC and marks a time it could not compute as estimated. | The record carries the tick count and no time. The profile defines the time reference. The JSON form has `taken_at` and `time_estimated`. |
| [plantwatch/0001 The phone relays between sensor stick and server](../../doc/decisions/0001-the-phone-relays-between-sensor-and-server.md) | A sensor stick talks only over BLE, to a phone that is often absent, and runs a year on a coin cell. | The profile has one counterpart, the central. Its procedures are short, and readings wait on the sensor stick. |

## References

| Source | What it says | What it means here |
|---|---|---|
| [Conventions: measured quantities](../../doc/references/conventions.md) | Soil moisture 0 to 100 percent in steps of 0.1; light 0 to 100 000 lux in steps of 1; temperature -20 to 60 °C in steps of 0.1. A value outside its range is rejected by the first receiver. An unmeasured quantity is absent, not zero. | The field ranges, the scaling in the record, the presence mask and the rejection rules of both forms. |
| [Conventions: identifiers](../../doc/references/conventions.md) | A sensor id has 8 bytes and is written as 16 lower-case hex digits. A sequence number is an unsigned 32-bit integer. | The sizes in Info, in the scan response and in the record; the form of `sensor_id` in JSON. |
| [Conventions: time](../../doc/references/conventions.md) | Outside the sensor stick every time is UTC, written as RFC 3339 with `Z` and whole seconds. An estimated time carries a flag. | The form of `taken_at`, and the field `time_estimated`. |
| [Conventions: delivery](../../doc/references/conventions.md) | A transfer may deliver an item twice. A receiver accepts it and reports success. A sender deletes only after a confirm. | A repeated `confirm` succeeds. A sensor stick deletes only after `confirm`. |
| [Conventions: HTTP ports](../../doc/references/conventions.md) | Field names in JSON are lower-case with underscores. | The member names of the JSON form. |
| [Glossary](../../doc/references/glossary.md) | Reading: one set of measurements with sequence number and time. Sensor stick: the device in the pot. Central: the BLE side that connects to it. Tick count: boot counter and seconds since boot. Batch: readings of one sensor stick transferred together. Pairing: binding a sensor stick to a phone and to a plant. | The contracts use these terms unchanged. Because pairing includes the plant, the profile calls the BLE step "bonding". |
| [Product parameters](../../doc/references/product-parameters.md) | Radio protocol version 1. Sampling interval 5 to 60 minutes. A sensor stick keeps at least 2 880 readings. | The profile's major version is 1. The ranges of `sampling_interval` and `capacity` in Info. |
