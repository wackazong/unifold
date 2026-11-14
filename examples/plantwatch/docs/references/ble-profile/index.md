# BLE profile of the sensor stick

Contract of the radio link: `device.ble-link` and `emulator.ble-link` serve it, `mobile.sensor-link` and `test-rig.device-under-test` use it. It defines how a sensor stick serves its readings to a central over Bluetooth Low Energy: what it advertises, which GATT attributes it has, and which procedures a central runs. Both sides of the radio link are built from this text. Notation: byte layouts in tables and bytes in hexadecimal; the steps of a procedure as text.
Sources: Bluetooth Core Specification 4.2.
Binding: ble
Version: 1.0

A reading travels over the radio link as a record. The record is the binary form of the [reading schema](../reading-schema.md) and is part of this profile. The terms are defined in the [glossary](../glossary.md).

## Use

A central finds a sensor stick by its advertising, opens a session and reads Info and Status. To get the stored readings, it writes `fetch` and stores the records so that they survive its own failure. Then it writes `confirm` up to `last` of the fetch result, and while `more` is 1, it fetches again. It disconnects as soon as it has what it came for.

A central learns that its connection has ended from `disconnected`. Every request on Transfer control gets one result, and while a fetch runs, the sensor stick accepts no other request there.

1. `advertising`, then `open-session`, then `info` and `status`.
2. `fetch`, then the central stores the records, then `confirm` up to `last` of the fetch result. While `more` is 1, `fetch` again. Then the central disconnects, and the sensor stick raises `disconnected` and advertises again.
3. To end a fetch early, the central disconnects. It keeps the complete records it has received.
4. When the connection is lost after the central has stored the records and before it has confirmed them, the central confirms them in the next connection without fetching again.
5. When `open-session` fails with `Pairing Not Supported`, the connection stays unencrypted. Info and Status are readable on it, and `fetch` is refused with ATT error `0x05`.

The roles: the sensor stick is the BLE peripheral and GATT server; it advertises, accepts one connection, serves its readings and releases a reading only after a confirm or on overflow. The central is the BLE central and GATT client; it scans, connects, fetches readings, stores them durably and confirms them.

Rules that hold for every part:

- The profile uses Bluetooth Core Specification 4.2 or later, LE 1M PHY.
- All multi-byte integers are little-endian.
- A sender writes reserved bits and bytes as 0. A receiver ignores them.
- A sensor stick never initiates anything except advertising, notifications and indications that the central has enabled, and a disconnect.
- When a sensor stick restarts, it loses the connection and all descriptor settings, keeps stored readings and delivered marks, and starts a new boot counter; the central takes a new time reference after reconnecting.

A sensor stick conforms to version 1.0 when it advertises as described, has the service with all five characteristics, and behaves as the procedures say. A central conforms when it follows the procedures and the rules for its side in [version](version.md). A statement in this profile that says what a side "may" do is a permission; every other statement is a requirement.

Not part of version 1.0: setting the sampling interval over the radio link, which the Info characteristic reports; battery level; updating the program of a sensor stick; binding a sensor stick to a plant, since the profile ends at the bond between a sensor stick and a central.

## States

Start: disconnected.

| State | Part | Result | Next |
|---|---|---|---|
| disconnected | `advertising` | | disconnected |
| disconnected | `open-session` | ok | connected |
| disconnected | `open-session` | `Pairing Not Supported` | connected |
| connected | `info` | | connected |
| connected | `status` | | connected |
| connected | `live-reading` | | connected |
| connected | `fetch` | | connected |
| connected | `confirm` | | connected |
| connected | `disconnected` | | disconnected |

## Qualities

| Aspect | Guarantee |
|---|---|
| concurrency | a sensor stick has at most one connection at a time, and it advertises only while no central is connected to it |
| ordering | the records of one fetch arrive in ascending order of sequence number; every request on Transfer control gets one result |
| delivery | a reading can reach a central more than once: after a lost connection, after a lost confirm, as a live reading and in a fetch; the central recognises it by the sequence number and keeps one copy; this is intended |
| latency | advertising starts within 10 s after the sensor stick starts and within 1 s after a disconnect; the tick count in a Status value is never older than 1 s when the value leaves the sensor stick |
| limits | every procedure works with the default ATT MTU of 23 bytes, and a larger MTU only makes a fetch faster; a sensor stick supports an MTU of at least 67 bytes and keeps at least 4 bonds across a restart; it may disconnect after 30 s without an ATT request and after 10 minutes of connection |
| security | bonding is LE Secure Connections, Just Works, and a new bond is accepted only for 5 minutes after the sensor stick starts; Just Works does not protect against an attacker who is active in that window; the static random device address makes a sensor stick trackable, and advertising data, Info and Status are readable by anyone in range, with the sensor id and counters but no measured values |
| compatibility | within one major version a later minor version only adds, as [version](version.md) says; a central ignores what it does not know and does not write to a sensor stick whose major version is higher than it implements |

## Parts

| Part | Content |
|---|---|
| [advertising](advertising.md) | what a sensor stick advertises, and its device address |
| [open-session](open-session.md) | connect, check the version, bond and encrypt, enable what is needed |
| [info](info.md) | the Info characteristic: facts that do not change while the sensor stick runs |
| [status](status.md) | the Status characteristic: tick count, stored readings, flags |
| [live-reading](live-reading.md) | the newest reading, notified as it is taken |
| [fetch](fetch.md) | stored readings as records on Transfer data |
| [confirm](confirm.md) | the cumulative mark that releases readings |
| [disconnected](disconnected.md) | the end of a connection, by either side or by the radio link |
| [transfer-result](transfer-result.md) | the result of a request on Transfer control, its codes and the ATT errors |
| [time-reference](time-reference.md) | how a central turns a tick count into a UTC time |
| [reading-service](reading-service.md) | the Reading service: its UUIDs and characteristics |
| [version](version.md) | the version of the profile, and what a minor version may change |

## Fake

A simulated sensor stick in memory that a test loads with readings: it answers Info and Status, serves `fetch` and `confirm` by the rules of the parts, and notifies live readings when the test adds one. Faults it can inject: a lost connection after any number of records, raised as `disconnected`, a `storage-failure`, a restart with a new boot counter, an overflow, a closed bonding window.
