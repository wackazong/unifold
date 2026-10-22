# radio as link expects it

The contract of the need `radio`: the BLE peripheral `link` requires of
whoever provides it, so that `link` can do what `link-profile` asks of a
sensor stick. `link` adds the meaning of the attributes and nothing below
them.

| Matter | What `link` expects |
|---|---|
| Role | BLE peripheral with a GATT server, one central at a time, Bluetooth 4.2 or later, LE 1M PHY |
| Identity | An identifier of 8 bytes, unique per board, that never changes; `link` reports it as the sensor id. A static random device address that never changes. |
| Advertising | Connectable and scannable, on all three advertising channels, whenever `link` has it switched on and no central is connected. `link` sets the interval, 1285 ms. Advertising resumes within 1 s after a disconnect. |
| Advertising data | Advertising data and scan response of up to 31 bytes each. `link` may replace them at any time; the next advertising event carries the new bytes. |
| Characteristics | `link` declares one service with 5 characteristics at start and needs room for 8. Each has a 128-bit UUID, its properties, a largest length of up to 64 bytes, and whether it requires an encrypted connection. |
| Requests | Every read and write reaches `link` as an event. `link` answers with a value, with success, or with an ATT error code of its choice. |
| Sending | `link` hands over one notification or indication and learns whether it was taken or there was no room; later it learns that there is room again. At least 4 notifications of 20 bytes per connection event. |
| Subscriptions | Whether notifications or indications are on, per characteristic. Everything is off at a new connection, also for a bonded central. |
| Connection | Connect, disconnect and the ATT MTU are reported; an MTU of at least 67 bytes is supported. Every connection interval from 15 ms to 100 ms is accepted; `link` can request an interval range and a peripheral latency. |
| Closing | `link` can close the connection at once. It sets a time without requests, 30 s, and a longest duration, 10 minutes; the provider closes the connection when either is reached and tells `link`. |
| Encryption | A request on a characteristic that requires encryption over an unencrypted connection never reaches `link`. The central gets ATT error `0x05` without a bond and `0x0F` with one. |
| Bonding | LE Secure Connections, Just Works, started only by the central. At least 4 bonds survive power loss; when all places are taken, a new bond replaces the one used longest ago. A new bond is accepted only for a duration that `link` opens, 300 s after a start. Otherwise pairing by an unknown central is rejected with `Pairing Not Supported`. |
| Time | Every event carries the tick count at which it happened |

## Examples

The cases a provider has to pass, a substitute included.

| Case | Expected |
|---|---|
| A central without a bond reads a characteristic declared as protected | ATT error `0x05`. `link` sees no event. |
| `link` answers a write with ATT error `0xFE` | The central receives `0xFE` for that write |
| `link` hands over 5 notifications of 19 bytes in one connection event | At least 4 are taken. For the rest `link` is told "no room" and later "room again". |
| A bonded central connects again | Every subscription is off |
| An unknown central starts pairing 301 s after the start | Rejected with `Pairing Not Supported` |
| `link` replaces the advertising data | A scanner sees the new bytes within 1285 ms |
| A central sends nothing for 30 s | The connection is closed and `link` is told |
| A read request arrives 86 405 s after the start | The event carries that tick count |
