# advertising

Kind: event

```text
advertising data, 31 bytes:
  02 01 06                                   flags: LE general discoverable, BR/EDR not supported
  11 07 <16 bytes>                           complete list of 128-bit service UUIDs: the Reading service
  09 FF FF FF <major> <flags> <newest: 4>    manufacturer specific data: company id FFFF, then 6 bytes
scan response, 21 bytes:
  08 09 50 57 2D <4 hex digits>              complete local name: PW- and the last four hex digits of the sensor id
  0B FF FF FF <sensor id: 8 bytes>           manufacturer specific data: company id FFFF, then the sensor id, byte 0 first
```

A sensor stick advertises whenever no central is connected to it. A central that already holds the reading `newest` and sees `has-readings` as 0 has no reason to connect.

| Property | Value |
|---|---|
| Type | Connectable, scannable, undirected (`ADV_IND`) |
| Channels | 37, 38 and 39 |
| Interval | At most 2 s. The sensor stick chooses it within that limit. |
| Start | Within 10 s after the sensor stick starts, and within 1 s after a disconnect |

The manufacturer specific data of the advertising data, after the company identifier `0xFFFF`:

| Offset | Size | Field | Meaning |
|---|---|---|---|
| 0 | 1 | `major` | Major version of the profile |
| 1 | 1 | `flags` | Bit 0 `has-readings`: the sensor stick holds at least one reading that no central has confirmed. Bit 1 `bonding-open`: the sensor stick accepts a new bond. Bits 2 to 7 reserved. |
| 2 | 4 | `newest` | Sequence number of the newest reading the sensor stick has taken, 0 if none |

The scan response carries the complete local name, `PW-` followed by the last four hex digits of the sensor id in lower case, and manufacturer specific data with the 8 bytes of the sensor id, byte 0 first.

## Device address

A sensor stick uses a static random device address. The address does not change during the life of the sensor stick. A central may recognise a bonded sensor stick by its address alone. The static address makes a sensor stick trackable by its address, and advertising data, Info and Status are readable by anyone in range; they contain the sensor id and counters, no measured values.

## Examples

A sensor stick with the sensor id `00a1b2c3d4e5f607` that has taken reading 4806 and holds unconfirmed readings, 10 minutes after its start. Advertising data, 31 bytes, then scan response, 21 bytes:

```text
02 01 06  11 07 47 2A 0E 6C 1F 5D A2 B3 5B 4E 1C 9A 01 00 77 70
09 FF FF FF 01 01 C6 12 00 00

08 09 50 57 2D 66 36 30 37  0B FF FF FF 00 A1 B2 C3 D4 E5 F6 07
```

| Case | Expected |
|---|---|
| The same sensor stick 2 minutes after its start | `flags` in the advertising data is `03`: `has-readings` and `bonding-open` |
| The central disconnects | The sensor stick advertises again within 1 s |
| A scanner sees `has-readings` 0 and holds `newest` | It does not connect |
