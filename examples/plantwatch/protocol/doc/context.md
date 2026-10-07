# Context of protocol

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From plantwatch

### [plantwatch/0002 Define the BLE profile and the reading format once, in a unit of their own](../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md)

Says: a separate unit owns both definitions. Both carry a version; a change
within a major version keeps older counterparts working.

Here: this unit is that definition. The version rules of both contracts
carry out the second sentence.

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

Says: every hop delivers at least once. Sensor id and sequence number
identify a reading; it never changes; a receiver accepts one it already has.

Here: the schema defines identity and immutability. Fetch and confirm are
an at-least-once transfer, and a repeated `confirm` succeeds.

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

Says: a reading carries a boot counter and the seconds since that boot. The
side that fetches converts to UTC and marks a time it cannot compute.

Here: the record carries the tick count and no time. The profile defines
the time reference. The JSON form has `taken_at` and `time_estimated`.

### [plantwatch/0001 The phone relays between sensor stick and server](../../doc/decisions/0001-the-phone-relays-between-sensor-and-server.md)

Says: a sensor stick has BLE and nothing else. It keeps readings until a
phone, which is not always near, has taken them.

Here: the profile has one counterpart, the central, and a reading waits on
the sensor stick until a confirm covers it.

### [plantwatch: conventions, measured quantities](../../doc/references/conventions.md)

Says: soil moisture 0 to 100 percent, resolution 0.1; light 0 to 100 000
lux, resolution 1; temperature −20 to 60 °C, resolution 0.1. The first
receiver rejects a value outside its range. A quantity that could not be
measured is absent, not zero.

Here: the field ranges, the scaling in the record, the presence mask and
the rejection rules of both forms.

### [plantwatch: conventions, identifiers and time](../../doc/references/conventions.md)

Says: a sensor id has 8 bytes, written as 16 lower-case hex digits; a
sequence number is an unsigned 32-bit integer. Outside the sensor stick a
time is UTC, RFC 3339 with `Z` and whole seconds, flagged when estimated.

Here: the sizes in Info, scan response and record; the forms of
`sensor_id` and `taken_at`; the field `time_estimated`.

### [plantwatch: conventions, HTTP ports](../../doc/references/conventions.md)

Says: field names in JSON are lower-case with underscores.

Here: the member names of the JSON form.

### [plantwatch: conventions, changing a shared definition](../../doc/references/conventions.md)

Says: the radio protocol and the reading format change first in the unit
that defines them. A change that an older counterpart cannot ignore needs a
new major version and a decision of plantwatch.

Here: the version rules of both contracts. The
[skill](skills/protocol-change-a-definition/SKILL.md) stops at a major
change until that decision exists.

### [plantwatch: glossary](../../doc/references/glossary.md)

Says: a central is the BLE role of the side that connects to a sensor
stick, normally a phone. Pairing binds a sensor stick to a phone and to a
plant.

Here: the contracts use the project's terms unchanged and call the phone's
side "central". Because pairing includes the plant, the unit's own
[glossary](references/glossary.md) calls the BLE step "bonding".

### [plantwatch: product parameters](../../doc/references/product-parameters.md)

Says: radio protocol version 1. Sampling interval 5 to 60 minutes. A sensor
stick keeps at least 2 880 readings and overwrites the oldest when full.

Here: the major version of the profile; the ranges of `sampling_interval`
and `capacity` in Info; the `overflow` flag in Status.
