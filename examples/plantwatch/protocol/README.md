# protocol

`protocol` is the written definition of two things that several independently
built parts have to agree on: how a sensor stick offers its readings to a
central over Bluetooth Low Energy, and what a reading is once it has left
the sensor stick. The unit contains documents and no code. Whoever
implements one side of the radio link, or stores or transfers readings,
builds against these documents.

## Why

The radio link and the reading are each implemented more than once, by
parts that are built and released separately; this unit exists so that
their definition belongs to none of them. It changes when what a sensor
stick and a central exchange changes, or what a reading contains, and
never because an implementation changed.

Both definitions are in one unit because the record on the radio link is
an encoding of the reading. Defined apart, the two would drift.

Two forces shape the text. It must be exact enough that two implementers
who never talk build parts that work together, so it uses byte tables,
numbered procedures and worked examples. And it must be changeable without
replacing all parts at once, so each contract has a version and rules for
what a minor version may do.

The trade-off: prose and tables are easy to review, but no tool checks
code against them. What must stay true: the text never depends on an
implementation, and behaviour that is not in the text is undefined.

## Capabilities

### `ble-profile`

The profile says what a sensor stick advertises, which GATT service and
characteristics it has, how every value is laid out byte by byte, and which
procedures a central runs: open a session, take a time reference, fetch
stored readings and confirm them, receive live readings. The record that
carries a reading over the radio link is the binary form of
`reading-schema`; the profile includes it.

What an implementer can rely on:

- **One answer per request.** For every request a central can write, the
  profile names the response of the sensor stick: a result code, an ATT
  error, or the behaviour when something fails.
- **Version.** The current version is 1.0. Within major version 1, a part
  built for a later version works with a part built for an earlier one.
  The profile lists what each side has to ignore for that.
- **A fetch deletes nothing.** A sensor stick releases a reading only
  after a central has confirmed it, or to make room when its memory is
  full, which it reports. A transfer can break at any point and be
  repeated.
- **Default MTU.** Every procedure works with an ATT MTU of 23 bytes.

Limits: one central per sensor stick at a time. Version 1.0 has no way to
set the sampling interval, to read a battery level or to update the
program of a sensor stick. The UUIDs and the company identifier are
placeholders until release.

A fetch of 96 readings and its confirm, as bytes:

```text
central → sensor stick  Transfer control  01 00 00 00 00 60 00
sensor stick → central  Transfer data     12 07 67 12 00 00 0C 00 ...  (96 times)
sensor stick → central  Transfer control  80 01 00 60 00 C6 12 00 00 00
central → sensor stick  Transfer control  02 C6 12 00 00
sensor stick → central  Transfer control  80 02 00 00 00 00 00 00 00
```

Contract: [BLE profile](docs/references/ble-profile/index.md).

### `reading-schema`

The schema defines the fields of a reading with types, units and ranges,
what identifies a reading, and two encodings: a JSON object for storing and
uploading, and a 19-byte binary record for the radio link.

What an implementer can rely on:

- **Identity.** Sensor id and sequence number together identify a reading.
  No holder changes a reading.
- **Absent, not zero.** A quantity that was not measured is absent in both
  encodings. It is never zero and never `null`.
- **Exact conversion.** A value converted from one encoding to the other
  and back is the same value.
- **Version.** Within major version 1, fields are only added, and only as
  optional ones. A receiver built for 1.0 reads every 1.x reading.

```json
{
  "sensor_id": "00a1b2c3d4e5f607",
  "sequence_number": 4711,
  "boot_counter": 12,
  "seconds_since_boot": 86400,
  "taken_at": "2026-10-06T07:15:00Z",
  "time_estimated": false,
  "soil_moisture": 41.5,
  "light": 12000,
  "temperature": 21.4
}
```

Contract: [reading schema](docs/references/reading-schema.md).

## Out of scope

- How an implementation is built or tested.
- The envelope around a batch of readings and the interface that accepts
  it. The schema defines one reading.
- Plants, thresholds and alerts. A reading does not know its plant.
- Machine-readable definitions. Version 1 is prose and tables; nothing
  generates code from it.

## Read next

1. [docs/references/glossary.md](docs/references/glossary.md): the terms of both contracts
2. [docs/references/ble-profile/index.md](docs/references/ble-profile/index.md): the BLE profile
3. [docs/references/reading-schema.md](docs/references/reading-schema.md): the reading schema
4. [docs/explanation/context.md](docs/explanation/context.md): what the definitions inherit
5. [Context diagram](docs/diagrams/context.md)
6. [Decisions](docs/decisions/index.md)
7. [Changing a definition](docs/skills/protocol-change-a-definition/SKILL.md)
