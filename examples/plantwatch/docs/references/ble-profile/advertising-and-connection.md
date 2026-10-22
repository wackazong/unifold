# Advertising and connection

How a central finds a sensor stick, connects to it and secures the connection. Part of the [BLE profile](index.md).

## Advertising

A sensor stick advertises whenever no central is connected to it.

| Property | Value |
|---|---|
| Type | Connectable, scannable, undirected (`ADV_IND`) |
| Channels | 37, 38 and 39 |
| Interval | At most 2 s. The sensor stick chooses it within that limit. |
| Start | Within 10 s after the sensor stick starts, and within 1 s after a disconnect |

### Advertising data

31 bytes, in this order:

| AD type | Length of content | Content |
|---|---|---|
| Flags (`0x01`) | 1 | `0x06`: LE general discoverable, BR/EDR not supported |
| Complete list of 128-bit service UUIDs (`0x07`) | 16 | UUID of the Reading service |
| Manufacturer specific data (`0xFF`) | 8 | Company identifier `0xFFFF`, then the 6 bytes below |

| Offset | Size | Field | Meaning |
|---|---|---|---|
| 0 | 1 | `major` | Major version of the profile |
| 1 | 1 | `flags` | Bit 0 `has-readings`: the sensor stick holds at least one reading that no central has confirmed. Bit 1 `bonding-open`: the sensor stick accepts a new bond. Bits 2 to 7 reserved. |
| 2 | 4 | `newest` | Sequence number of the newest reading the sensor stick has taken, 0 if none |

A central that already holds the reading `newest` and sees `has-readings` as 0 has no reason to connect.

### Scan response

| AD type | Length of content | Content |
|---|---|---|
| Complete local name (`0x09`) | 7 | `PW-` followed by the last four hex digits of the sensor id, lower case |
| Manufacturer specific data (`0xFF`) | 10 | Company identifier `0xFFFF`, then the 8 bytes of the sensor id, byte 0 first |

## Device address

A sensor stick uses a static random device address. The address does not change during the life of the sensor stick. A central may recognise a bonded sensor stick by its address alone.

## Connection

| Property | Value |
|---|---|
| Connections at a time | 1. While connected, the sensor stick does not advertise. |
| Connection interval | The central chooses. The sensor stick accepts 15 ms to 100 ms and may request 30 ms to 50 ms. |
| Peripheral latency | 0 during a fetch. Otherwise the sensor stick may request up to 4. |
| Supervision timeout | 4 s |
| ATT MTU | The sensor stick accepts an MTU exchange and supports at least 67 bytes. It works with 23. |
| Idle disconnect | The sensor stick may disconnect when the central has sent no ATT request for 30 s. |
| Longest connection | The sensor stick may disconnect a central after 10 minutes. |

A central disconnects as soon as it has what it came for. A sensor stick lives on a coin cell, and every second of connection costs it energy.

## Bonding and encryption

"Bonding" here means BLE pairing with storage of the keys. It binds a sensor stick and a central. It does not bind a plant.

| Property | Value |
|---|---|
| Method | LE Secure Connections, Just Works, with bonding |
| Who starts | The central, after connecting. The sensor stick sends no security request. |
| When a new bond is accepted | Only while bonding is open: for 5 minutes after the sensor stick starts |
| How a user opens bonding | By restarting the sensor stick, that is by taking out and putting back the cell |
| Bonds a sensor stick keeps | At least 4. They survive a restart. |
| When all bond places are taken | A new bond replaces the bond that was used longest ago |
| Outside the bonding time | The sensor stick rejects pairing requests of unknown centrals with `Pairing Not Supported` |

Which attributes need an encrypted connection is listed with the [characteristics](characteristics.md). A request on such an attribute over an unencrypted connection fails with the ATT error `Insufficient Authentication` (`0x05`) when no bond exists and `Insufficient Encryption` (`0x0F`) when one exists.

Limits of this scheme:

- Just Works does not protect against an attacker who is active during the 5 minutes in which bonding is open.
- Advertising data, Info and Status are readable by anyone in range. They contain the sensor id and counters, no measured values.
- The static address makes a sensor stick trackable by its address.

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
| An unknown central starts pairing 301 s after the start | Rejected with `Pairing Not Supported` |
| A central without a bond writes to Transfer control | ATT error `0x05` |
| A bonded central writes to Transfer control before encryption is on | ATT error `0x0F` |
| A fifth central bonds with a sensor stick that keeps 4 bonds | Its bond replaces the one that was used longest ago |
| The central disconnects | The sensor stick advertises again within 1 s |
