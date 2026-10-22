# Service and characteristics

The GATT attributes of a sensor stick and the layout of their values. Part of the [BLE profile](index.md). The UUIDs are listed in the [index](index.md).

## The Reading service

A sensor stick has exactly one instance of the Reading service, as a primary service. The service has five characteristics:

| Characteristic | Properties | Encrypted connection | Value length |
|---|---|---|---|
| Info | Read | not required | 18 bytes |
| Status | Read, Notify | not required | 17 bytes |
| Live reading | Read, Notify | required | One record, or 0 bytes |
| Transfer control | Write, Indicate | required | 1 to 20 bytes |
| Transfer data | Notify | required | One or more records |

Every characteristic with Notify or Indicate has a Client Characteristic Configuration descriptor. A sensor stick resets these descriptors to 0 at every new connection, also for a bonded central.

## Info

Facts that do not change while the sensor stick runs.

| Offset | Size | Field | Meaning |
|---|---|---|---|
| 0 | 1 | `major` | Major version of the profile: 1 |
| 1 | 1 | `minor` | Minor version of the profile: 0 |
| 2 | 8 | `sensor_id` | The sensor id, byte 0 first |
| 10 | 1 | `quantities` | Quantities this sensor stick can measure, bits as in `present` of the record |
| 11 | 2 | `sampling_interval` | Sampling interval in seconds, 300 to 3600 |
| 13 | 2 | `capacity` | Number of readings the sensor stick can hold, at least 2880 |
| 15 | 3 | `build` | Version of the implementation: major, minor, patch. For display and diagnosis only. |

## Status

The state of the sensor stick at the moment it sends the value.

| Offset | Size | Field | Meaning |
|---|---|---|---|
| 0 | 2 | `boot_counter` | Current tick count, first part |
| 2 | 4 | `seconds_since_boot` | Current tick count, second part |
| 6 | 4 | `oldest` | Sequence number of the oldest stored reading, 0 if `count` is 0 |
| 10 | 4 | `newest` | Sequence number of the newest reading ever taken, 0 if none |
| 14 | 2 | `count` | Number of stored readings |
| 16 | 1 | `flags` | Bit 0 `overflow`, bit 1 `bonding-open`, bit 2 `fetch-active`, bits 3 to 7 reserved |

"Stored" is used as the [glossary](../glossary.md) defines it. `overflow` is 1 when the sensor stick has discarded at least one stored reading to make room, since the last successful confirm or since its start. It discards the oldest stored readings first.

A sensor stick notifies Status after it has taken a reading and after it has carried out a confirm. The tick count in a value is never older than 1 s when the value leaves the sensor stick.

## Live reading

The newest reading the sensor stick has taken, as one record in the binary form of the [reading schema](../reading-schema.md). The value has length 0 as long as the sensor stick has taken no reading since its start.

A sensor stick notifies the value each time it takes a reading. The reading is the same one that a fetch delivers later, with the same sequence number.

## Transfer control

The central writes requests to this characteristic and receives one result per request as an indication. The central uses Write Request, not Write Command.

### Requests

| Op code | Name | Parameters after the op code | Length |
|---|---|---|---|
| `0x01` | `fetch` | `first`: sequence number, 4 bytes. `limit`: largest number of records, 2 bytes, 0 means no limit. | 7 |
| `0x02` | `confirm` | `up_to`: sequence number, 4 bytes | 5 |
| `0x03` | `abort` | none | 1 |

### Results

Every result starts with `0x80`, the op code it answers and a result code.

| Answer to | Bytes after the result code | Length |
|---|---|---|
| `fetch` | `sent`: number of records sent, 2 bytes. `last`: sequence number of the last record sent, 4 bytes, 0 if none. `more`: 1 byte, 1 if stored readings with a higher number remain, else 0. | 10 |
| `confirm` | `count`: number of stored readings afterwards, 2 bytes. `oldest`: sequence number of the oldest stored reading afterwards, 4 bytes, 0 if none. | 9 |
| `abort` | none | 3 |
| unknown op code | none | 3 |

When the result code is neither `success` nor `aborted`, the bytes after it are 0.

### Result codes

| Code | Name | Meaning |
|---|---|---|
| `0x00` | `success` | The request has been carried out |
| `0x01` | `op-code-not-supported` | The sensor stick does not know the op code |
| `0x02` | `invalid-parameter` | The request is shorter than its op code requires |
| `0x03` | `out-of-range` | `confirm` names a sequence number above the newest reading taken |
| `0x04` | `aborted` | The fetch ended because the central wrote `abort` |
| `0x05` | `storage-failure` | The sensor stick could not read or change its stored readings |
| `0x06` | `mtu-too-small` | A record does not fit into one notification with the current ATT MTU |

### ATT errors

The sensor stick rejects the write itself in these cases. No indication follows.

| ATT error | When |
|---|---|
| `0xFD` CCC descriptor improperly configured | Indications of Transfer control are not enabled, or `fetch` is written while notifications of Transfer data are not enabled |
| `0xFE` Procedure already in progress | `fetch` or `confirm` is written while a fetch is running |
| `0x05`, `0x0F` | The connection is not encrypted, see [bonding and encryption](advertising-and-connection.md) |

`abort` is accepted at any time. Without a running fetch it does nothing and its result is `success`.

## Transfer data

Carries the records of a running fetch. A notification contains one or more whole records, one after the other, without a header. The records are in the binary form of the [reading schema](../reading-schema.md); each starts with its own length.

- A sensor stick never splits a record across notifications.
- A notification holds at most as many records as fit into ATT MTU minus 3 bytes. With the default MTU of 23 that is one record of version 1.0.
- Records of one fetch arrive in ascending order of sequence number.
- A sensor stick sends Transfer data only between a `fetch` request and its result.

## Examples

Info of a sensor stick with the sensor id `00a1b2c3d4e5f607`, all three quantities, an interval of 900 s, a capacity of 2 880 and build 1.0.0; then its Status at tick count 12 / 87 305 with the 96 stored readings 4711 to 4806 and no flag set:

```text
01 00 00 A1 B2 C3 D4 E5 F6 07 07 84 03 40 0B 01 00 00
0C 00 09 55 01 00 67 12 00 00 C6 12 00 00 60 00 00
```

Requests and results on Transfer control, as bytes, are in the [procedures](procedures.md).
