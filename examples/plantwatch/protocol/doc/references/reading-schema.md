# Reading schema

Defines what a reading is: its fields, its identity, its JSON form and its
binary form. Everything that produces, stores or transfers a reading conforms
to this schema. Version 1.0.

## Fields

| Field | Type | Unit and range | In JSON | In binary | Meaning |
|---|---|---|---|---|---|
| `sensor_id` | 8 bytes | | required | not carried | The sensor stick that took the reading |
| `sequence_number` | unsigned 32 bit | 1 to 4 294 967 295 | required | required | Number of the reading on its sensor stick |
| `boot_counter` | unsigned 16 bit | 0 to 65 535 | required | required | First part of the tick count |
| `seconds_since_boot` | unsigned 32 bit | seconds | required | required | Second part of the tick count |
| `taken_at` | time | UTC, whole seconds | required | not carried | When the reading was taken |
| `time_estimated` | boolean | | required | not carried | `true` if `taken_at` is an estimate |
| `soil_moisture` | decimal | percent, 0.0 to 100.0, step 0.1 | optional | optional | Soil moisture as a share of the calibrated range |
| `light` | integer | lux, 0 to 100 000 | optional | optional | Illuminance |
| `temperature` | decimal | °C, -20.0 to 60.0, step 0.1 | optional | optional | Temperature at the sensor stick |

`soil_moisture`, `light` and `temperature` are the measured quantities. A
quantity that the sensor stick could not measure is absent. It is never
encoded as zero or as a special number. A reading without any quantity is
valid.

## Identity and order

- The pair `sensor_id` and `sequence_number` identifies a reading. Two
  readings with the same pair are the same reading.
- The sequence number 0 is never given to a reading. Interfaces use 0 to say
  "none".
- On one sensor stick, a reading with a higher sequence number was taken
  later. Sequence numbers are not consecutive: a receiver draws no conclusion
  from a gap.
- The tick count orders readings of one sensor stick in the same way:
  first by `boot_counter`, then by `seconds_since_boot`.

## Immutability

- The fields carried in the binary form are fixed when the sensor stick takes
  the reading.
- `sensor_id`, `taken_at` and `time_estimated` are added once, by the central
  that fetches the reading from the sensor stick. The rule for computing
  `taken_at` is the time reference procedure of the
  [BLE profile](ble-profile/procedures.md).
- After that, no holder changes any field. A holder that receives a reading
  it already has keeps the one it has and reports success.

## JSON form

A reading is a JSON object. This form is used wherever a reading is stored
as a document or uploaded.

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

| Rule | Detail |
|---|---|
| Encoding | UTF-8 |
| `sensor_id` | String of 16 lower-case hex digits. The first two digits are byte 0. |
| `taken_at` | RFC 3339 string with the suffix `Z` and whole seconds |
| Integers | JSON numbers without fraction or exponent |
| Decimals | JSON numbers with at most one digit after the decimal point |
| Absent quantity | The member is left out. `null` is invalid. |
| Unknown members | A receiver ignores them and keeps them if it passes the reading on |
| Member order | Without meaning |

A receiver rejects a reading in which a required member is missing, a member
has the wrong type, or a value lies outside its range. It rejects the single
reading, not the batch it arrived in.

## Binary form

A reading on the radio link is one record. All multi-byte integers are
little-endian. Version 1.0 records have 19 bytes.

| Offset | Size | Field | Encoding |
|---|---|---|---|
| 0 | 1 | `length` | Number of bytes that follow this byte. 18 in version 1.0. |
| 1 | 1 | `present` | Bit mask of the quantities that are present, see below |
| 2 | 4 | `sequence_number` | Unsigned |
| 6 | 2 | `boot_counter` | Unsigned |
| 8 | 4 | `seconds_since_boot` | Unsigned |
| 12 | 2 | `soil_moisture` | Unsigned, percent × 10, 0 to 1000 |
| 14 | 3 | `light` | Unsigned, lux, 0 to 100 000 |
| 17 | 2 | `temperature` | Signed two's complement, °C × 10, -200 to 600 |

Bits of `present`:

| Bit | Quantity |
|---|---|
| 0 | `soil_moisture` |
| 1 | `light` |
| 2 | `temperature` |
| 3 to 7 | Reserved for quantities of later versions. Sent as 0. |

Rules:

- Every field has its place in every record. The bytes of an absent quantity
  are sent as 0, and its bit in `present` is 0.
- A receiver reads `length` first. It skips bytes beyond the fields it knows.
  It treats a quantity whose bytes lie beyond `length` as absent.
- A receiver ignores bits of `present` it does not know.
- A record is at most 64 bytes long in major version 1.
- A receiver rejects a record whose `length` is below 11, or in which a
  present quantity lies outside its range.

The reading of the JSON example as a record:

```text
12 07 67 12 00 00 0C 00 80 51 01 00 9F 01 E0 2E 00 D6 00
```

## Converting between the forms

| Binary | JSON |
|---|---|
| `soil_moisture` 415 | `"soil_moisture": 41.5` |
| `light` 12000 | `"light": 12000` |
| `temperature` 214 | `"temperature": 21.4` |
| Bit in `present` is 0 | Member is left out |
| Not carried | `sensor_id` from the connection, `taken_at` and `time_estimated` from the time reference |

The conversion is exact in both directions. No holder rounds a value again.

## Version

The schema has a version `major.minor`. This document describes 1.0. An
interface that carries readings states the major version it carries.

Within one major version, a later minor version may only:

- add an optional quantity. In the JSON form it is a new member. In the
  binary form it gets the next free bit of `present` and bytes after the last
  existing field.
- add an optional member to the JSON form that is not a quantity.

Within one major version, no version:

- removes or renames a field, or makes an optional field required,
- changes the type, unit, range, scaling or position of a field,
- changes what identifies a reading.

A change of the second list makes a new major version.
