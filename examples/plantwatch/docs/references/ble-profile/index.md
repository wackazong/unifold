# BLE profile of the sensor stick

Defines how a sensor stick offers its readings to a central over Bluetooth Low Energy: what it advertises, which GATT attributes it has, and which procedures a central runs. Both sides of the radio link are built from this text. Version 1.0.

## Parts

| Part | Content |
|---|---|
| [advertising-and-connection.md](advertising-and-connection.md) | Advertising data, device address, connection parameters, bonding and encryption |
| [characteristics.md](characteristics.md) | The service, its characteristics, their byte layouts, op codes and result codes |
| [procedures.md](procedures.md) | Open a session, take a time reference, fetch stored readings and confirm, live readings, behaviour on errors |

A reading travels over the radio link as a record. The record is the binary form of the [reading schema](../reading-schema.md) and is part of this profile. The terms are defined in the [glossary](../glossary.md).

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

## UUIDs

All UUIDs of the profile share one 128-bit base. The 16-bit part `xxxx` selects the attribute:

```text
7077xxxx-9a1c-4e5b-b3a2-5d1f6c0e2a47
```

| `xxxx` | Attribute |
|---|---|
| `0001` | Reading service |
| `0002` | Info characteristic |
| `0003` | Status characteristic |
| `0004` | Live reading characteristic |
| `0005` | Transfer control characteristic |
| `0006` | Transfer data characteristic |

The base and the company identifier in the [advertising data](advertising-and-connection.md) are placeholders. Final values replace them before version 1.0 is released. Values `0007` to `00ff` are reserved for characteristics of later minor versions.

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
