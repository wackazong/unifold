---
unit: protocol
summary: Defines the BLE profile of the sensor stick and the format of a reading
kind: specification
status: planned
provides:
  ble-profile:
    kind: specification
    summary: GATT services, characteristics and procedures of the sensor stick
    contract: doc/references/ble-profile/index.md
  reading-schema:
    kind: specification
    summary: Fields, units and identity of a reading as it is stored and uploaded
    contract: doc/references/reading-schema.md
---
# protocol

protocol is the written definition of two things that several independently
built parts have to agree on: how a sensor stick offers its readings to a
central over Bluetooth Low Energy, and what a reading is once it has left
the sensor stick. The unit contains documents and no code. Whoever
implements one side of the radio link, or stores or transfers readings,
builds against these documents.

## Provides

### `ble-profile`

The profile says what a sensor stick advertises, which GATT service and
characteristics it has, how every value is laid out byte by byte, and which
procedures a central runs: open a session, take a time reference, fetch
stored readings and confirm them, receive live readings.

What an implementer can rely on:

- The text is complete for both roles. A sensor stick and a central that
  are each built from it alone work together.
- The current version is 1.0. Within major version 1, a part built for a
  later version works with a part built for an earlier one. The profile
  states what each side has to tolerate for that.
- A fetch deletes nothing. A sensor stick releases a reading only after a
  central has confirmed it, so a transfer can break at any point and be
  repeated.
- Every procedure works with the default ATT MTU.

Limits: one central per sensor stick at a time. Version 1.0 has no way to
set the sampling interval, to read a battery level or to update firmware.
The UUIDs and the company identifier are placeholders until release.

A fetch of 96 readings and its confirm, as bytes:

```text
central → sensor stick  Transfer control  01 00 00 00 00 60 00
sensor stick → central  Transfer data     12 07 67 12 00 00 0C 00 ...  (96 times)
sensor stick → central  Transfer control  80 01 00 60 00 C6 12 00 00 01
central → sensor stick  Transfer control  02 C6 12 00 00
sensor stick → central  Transfer control  80 02 00 00 00 00 00 00 00
```

Contract: [BLE profile](doc/references/ble-profile/index.md).

### `reading-schema`

The schema defines the fields of a reading with types, units and ranges,
what identifies a reading, and two encodings: a JSON object for storing and
uploading, and a 19-byte binary record for the radio link.

What an implementer can rely on:

- Sensor id and sequence number together identify a reading. No holder
  changes a reading.
- A quantity that was not measured is absent in both encodings. It is never
  zero and never `null`.
- The two encodings convert into each other without loss.
- Within major version 1, fields are only added, and only as optional
  ones. A receiver built for 1.0 reads every 1.x reading.

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

Contract: [reading schema](doc/references/reading-schema.md).

## Out of scope

- How an implementation is built or tested.
- The envelope around a batch of readings and the interface that accepts
  it. The schema defines one reading.
- Plants, thresholds and alerts. A reading does not know its plant.
- Machine-readable definitions. Version 1 is prose and tables; nothing
  generates code from it.

## More

- [AGENTS.md](AGENTS.md): why the definitions are a unit of their own
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- [Changing a definition](doc/skills/protocol-change-a-definition/SKILL.md)
