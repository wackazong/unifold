# radio

The contract of the capability `radio`: a BLE peripheral with a GATT server
for one central at a time, Bluetooth 4.2 on the LE 1M PHY.

## What the caller sets

| Setting | Behaviour |
|---|---|
| Characteristics | Declared once at start: up to 16, in one or more services. Each has a 128-bit UUID, its properties, a largest length of up to 128 bytes, and whether it requires an encrypted connection. |
| Advertising data, scan response | Up to 31 bytes each. The caller may replace them at any time; the next advertising event carries the new bytes. |
| Advertising | On or off, at an interval of 100 ms to 2 s. While it is on and no central is connected, `hal` advertises connectable and scannable on all three advertising channels. After a disconnect it resumes within 1 s. |
| Connection limits | A time without requests and a longest duration. `hal` closes the connection when either is reached. The caller may also close it at once. |
| Preferred connection | An interval range and a peripheral latency that `hal` requests from the central. `hal` accepts every interval the central chooses. |
| Bonding open | A duration. `hal` accepts a new bond only until it ends. |

## What hal reports

Every event carries the tick count at which it happened. Events arrive in
the order in which they happened.

| Event | Content |
|---|---|
| Connected, disconnected | |
| MTU changed | The ATT MTU, 23 to 131 bytes |
| Read, write | The characteristic and, for a write, its bytes. The caller answers with a value, with success, or with an ATT error code of its choice. `hal` sends the answer. |
| Subscription changed | The characteristic, and whether notifications or indications are now on |
| Room again | Follows a notification or indication that `hal` did not take for lack of room |

## What hal does by itself

- **Identity.** An 8-byte identifier, unique per board, that never
  changes, and a static random device address that never changes.
- **Sending.** The caller hands over one notification or indication; `hal`
  takes it or answers "no room". Per connection event `hal` sends at least
  4 notifications of up to 20 bytes.
- **Subscriptions.** `hal` keeps the state per characteristic and switches
  everything off at each new connection, also for a bonded central.
- **Encryption.** `hal` answers a request on a characteristic that requires
  encryption over an unencrypted connection itself: ATT error `0x05` when
  the central has no bond, `0x0F` when it has one. The caller sees no
  event.
- **Bonding.** LE Secure Connections, Just Works. `hal` never asks the
  central for security. It keeps at least 4 bonds across power loss; when
  all places are taken, a new bond replaces the one used longest ago.
  While bonding is closed, `hal` rejects pairing by a central without a
  bond with `Pairing Not Supported`.

Limit: transmit power is 0 dBm. `hal` knows nothing about the meaning of an
attribute.

## Examples

| Case | Expected |
|---|---|
| A central without a bond writes to a protected characteristic | ATT error `0x05`; no event |
| A bonded central does the same before encryption is on | ATT error `0x0F`; no event |
| The caller hands over 6 notifications in one connection event | `hal` takes at least 4, answers "no room" for the rest and later reports "room again" |
| A bonded central reconnects | Every subscription is off until the central switches it on |
| A fifth central bonds while bonding is open | Its bond replaces the one used longest ago |
| A central without a bond starts pairing 10 s after the open duration ended | Rejected with `Pairing Not Supported` |
| No request arrives for the time the caller set, 30 s | `hal` closes the connection and reports "disconnected" |
| The caller replaces the advertising data at an interval of 1285 ms | A scanner sees the new bytes at most 1285 ms later |
