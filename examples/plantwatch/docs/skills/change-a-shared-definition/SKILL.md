---
name: change-a-shared-definition
description: Change the BLE profile or the reading schema so that parts built for the previous version keep working. Use it when a field, a quantity, a characteristic, an op code or a rule of one of the two contracts shall be added or changed.
---

# Change a definition compatibly

The result is a new version of a contract that parts built for the previous version of the same major version still work with. The procedure exists because the implementations are updated one after the other, not together.

## Steps

1. **Classify the change.** Compare it with the version rules of the contract: [profile](../../references/ble-profile/index.md), [schema](../../references/reading-schema.md). If the rules allow it, it is a minor change. If not, it needs a new major version: stop and get the decision that [Changing a shared definition](../../references/conventions.md#changing-a-shared-definition) names.
2. **Record the reason.** If the change had alternatives that concern only the shape of the definition, add a decision to [decisions](../../decisions/index.md) with status `proposed`.
3. **Change the schema first** if a reading changes. Add the field to the field table, to the JSON rules, to the binary layout and to the examples. A new quantity is optional, takes the next free bit of `present` and bytes after the last field.
4. **Change the profile.** Add new bytes only at the end of a value. Take new op codes, result codes and UUID numbers from the unused ranges. Write what a side built for the previous version does when it meets the new element; if the tolerance rules do not already cover it, the change is not minor.
5. **Update the procedures**, the failure table and the examples in [procedures.md](../../references/ble-profile/procedures.md) if behaviour changes. Write the example of a new case before anything else: it is the first test of every implementation.
6. **Raise the version** in the first paragraph and the section "Version" of each changed contract, and in the [Info layout](../../references/ble-profile/characteristics.md#info) if the profile changed.
7. **Recompute every byte example**: in the [schema](../../references/reading-schema.md#examples), the [characteristics](../../references/ble-profile/characteristics.md#examples), the [advertising](../../references/ble-profile/advertising-and-connection.md#examples) and the [procedures](../../references/ble-profile/procedures.md#examples).
8. **Check the shared ranges.** If a unit, range or identifier form changes, it must first change at its source, the [conventions](../../references/conventions.md). Then correct each `Says` that cites it (`unifold cited-by`).
9. Run the unifold generator and checker and fix what they report.

## Checks

- Walk through "fetch stored readings and confirm" twice: old central with new sensor stick, new central with old sensor stick. Every step has a defined outcome.
- Decode the example record by hand with the old layout table. Every field the old version knows has its old value.
- No file exceeds 200 lines. If a part of the profile does, split it and link the new part from the profile's index.
- The contracts name no implementation. Every unit whose manifest names a contract still conforms to it.

## Reference

- [BLE profile](../../references/ble-profile/index.md): version rules and the reserved ranges
- [Reading schema](../../references/reading-schema.md): version rules
