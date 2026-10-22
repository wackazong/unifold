# Glossary of protocol

The terms that have one fixed meaning in both contracts of this unit.
Terms of the whole project, such as reading, sensor stick, central and
tick count, are cited in [context](../explanation/context.md) and not repeated here.

| Term | Meaning |
|---|---|
| Profile | The [BLE profile](ble-profile/index.md), the contract of `ble-profile` |
| Schema | The [reading schema](reading-schema.md), the contract of `reading-schema` |
| Role | Sensor stick or central. The contracts name roles, never implementations. |
| Quantity | One measured value of a reading: soil moisture, light or temperature |
| Record | The binary form of one reading, as it crosses the radio link |
| Holder | Anything that keeps or passes on a reading after it has left the sensor stick |
| Bonding | BLE pairing with storage of the keys. It binds a sensor stick and a central, never a plant. |
| Stored | Of a reading on a sensor stick: taken, and neither covered by a confirm nor discarded |
| Fetch | The request with which a central has stored readings sent to it. It changes nothing. |
| Confirm | The request with which a central states that it holds every reading up to a sequence number. Only a confirm releases readings. |
| Overflow | A sensor stick discarding its oldest stored readings to make room for new ones |
| Time reference | A tick count of a sensor stick together with the UTC time at which a central read it |
| Live reading | The newest reading, sent to a connected central at the moment it is taken |
