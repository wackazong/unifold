# BLE profile of the sensor stick

Contract of the radio link: `device.ble-link` and `emulator.ble-link` serve it, `mobile.sensor-link` and `test-rig.device-under-test` use it. It defines how a sensor stick serves its readings to a central over Bluetooth Low Energy: what it advertises, which GATT attributes it has, and which procedures a central runs. Both sides of the radio link are built from this text. Version 1.0. Notation: byte layouts in tables and bytes in hexadecimal; the steps of a procedure as text.
Sources: Bluetooth Core Specification 4.2; decisions 0005, 0008, 0009 and 0010 of plantwatch.

A reading travels over the radio link as a record. The record is the binary form of the [reading schema](../reading-schema.md) and is part of this profile. The terms are defined in the [glossary](../glossary.md).

## Parts

| Part | Content |
|---|---|
| [advertising](advertising.md) | what a sensor stick advertises, and its device address |
| [open-session](open-session.md) | connect, check the version, bond and encrypt, enable what is needed |
| [info](info.md) | the Info characteristic: facts that do not change while the sensor stick runs |
| [status](status.md) | the Status characteristic: tick count, stored readings, flags |
| [time-reference](time-reference.md) | how a central turns a tick count into a UTC time |
| [live-reading](live-reading.md) | the newest reading, notified as it is taken |
| [fetch](fetch.md) | stored readings as records on Transfer data |
| [confirm](confirm.md) | the cumulative mark that releases readings |
| [abort](abort.md) | ends a running fetch |
| [transfer-result](transfer-result.md) | the result of a request on Transfer control, its codes and the ATT errors |

## Roles

| Role | BLE roles | Task |
|---|---|---|
| Sensor stick | Peripheral, GATT server | Advertises, accepts one connection, serves its readings, releases a reading only after a confirm or on overflow |
| Central | Central, GATT client | Scans, connects, fetches readings, stores them durably, confirms them |

## General rules

- The profile uses Bluetooth Core Specification 4.2 or later, LE 1M PHY.
- All multi-byte integers are little-endian.
- A sender writes reserved bits and bytes as 0. A receiver ignores them.
- A sensor stick has at most one connection at a time.
- Every procedure works with the default ATT MTU of 23 bytes. A larger MTU only makes a fetch faster.
- A sensor stick never initiates anything except advertising, notifications and indications that the central has enabled, and a disconnect.
- A reading can reach a central more than once: after a lost connection, after a lost confirm, as a live reading and in a fetch. The central recognises it by the sequence number and keeps one copy. This is intended.

## The Reading service

A sensor stick has exactly one instance of the Reading service, as a primary service. All UUIDs of the profile share one 128-bit base; the 16-bit part `xxxx` selects the attribute:

```text
7077xxxx-9a1c-4e5b-b3a2-5d1f6c0e2a47
```

| `xxxx` | Characteristic | Properties | Encrypted connection | Value length |
|---|---|---|---|---|
| `0001` | Reading service | | | |
| `0002` | Info | Read | not required | 18 bytes |
| `0003` | Status | Read, Notify | not required | 17 bytes |
| `0004` | Live reading | Read, Notify | required | one record, or 0 bytes |
| `0005` | Transfer control | Write, Indicate | required | 1 to 20 bytes |
| `0006` | Transfer data | Notify | required | one or more records |

Every characteristic with Notify or Indicate has a Client Characteristic Configuration descriptor. A sensor stick resets these descriptors to 0 at every new connection, also for a bonded central. The base and the company identifier in the advertising data are placeholders; final values replace them before version 1.0 is released. Values `0007` to `00ff` are reserved for characteristics of later minor versions.

When a sensor stick restarts, it loses the connection and all descriptor settings, keeps stored readings and delivered marks, and starts a new boot counter; the central takes a new time reference after reconnecting.

## Version

The profile has a version `major.minor`. A sensor stick reports both numbers in the Info characteristic and the major number in its advertising data.

Within one major version, a later minor version may only:

- add a characteristic to the service,
- add an op code or a result code,
- add bytes at the end of a characteristic value or of an op code's parameters,
- give a meaning to a reserved bit,
- add a quantity to the record, as the [reading schema](../reading-schema.md) allows.

Within one major version, no version removes anything, moves a field, or changes the meaning, size or scaling of an existing field.

What each side does so that this works:

| Side | Rule |
|---|---|
| Central | Ignores characteristics, trailing bytes, flag bits and record fields it does not know |
| Central | Treats a result code it does not know as a failure of that request |
| Central | Works with a sensor stick whose value is shorter than it knows: a missing trailing field counts as absent or 0 |
| Central | Does not write to a sensor stick whose major version is higher than the highest it implements |
| Sensor stick | Answers an op code it does not know with the result `op-code-not-supported` |
| Sensor stick | Accepts parameters that are longer than it knows and ignores the extra bytes |

## Conformance

A sensor stick conforms to version 1.0 when it advertises as described, has the service with all five characteristics, and behaves as the procedures say. A central conforms when it follows the procedures and the rules for its side above. A statement in this profile that says what a side "may" do is a permission; every other statement is a requirement.

## Not part of version 1.0

- Setting the sampling interval over the radio link. The Info characteristic reports it.
- Battery level.
- Updating the program of a sensor stick.
- Binding a sensor stick to a plant. The profile ends at the bond between a sensor stick and a central.

## Fake

A simulated sensor stick in memory that a test loads with readings: it answers Info and Status, serves `fetch`, `confirm` and `abort` by the rules of the parts, and notifies live readings when the test adds one. Faults it can inject: a lost connection after any number of records, a `storage-failure`, a restart with a new boot counter, an overflow, a closed bonding window.
