---
name: add-a-measured-quantity
description: Add a new measured quantity, such as air humidity, to plantwatch from the sensor to the alert. Use it when the sensor stick shall measure something it does not measure yet.
---
# Add a measured quantity

A new quantity touches every part that handles a reading. The order below
keeps each step compatible with the parts that have not changed yet.

## Steps

1. **Decide.** Record a decision in this unit's
   [decisions](../../decisions/index.md) with status `proposed`: what is
   measured, why, and which hardware it needs. Wait for a human to accept it.
2. **Name it.** Add the quantity with unit, range and resolution to the
   table in [conventions.md](../../references/conventions.md).
   Add the term to the [glossary](../../references/glossary.md) if it is
   new.
3. **Declare the hardware.** If a new sensor is needed, add a need to the
   manifest, [unifold.yaml](../../../unifold.yaml), wire it to the part that reads
   it, and describe it in [README.md](../../../README.md).
4. **Extend the definitions.** In [protocol](../../../protocol/README.md),
   add the quantity to the reading format and to the radio protocol as an
   optional field, so that older parts keep working. Follow that unit's own
   skills.
5. **Simulate it.** In [emulator](../../../emulator/README.md), make the
   quantity available to scenarios.
6. **Test it first.** In [test-rig](../../../test-rig/README.md), add an
   end-to-end test that fails until the remaining steps are done.
7. **Measure it.** In [device](../../../device/README.md), read the new
   sensor and include the quantity in readings.
8. **Carry it.** In [mobile](../../../mobile/README.md), store, upload and
   show the quantity.
9. **Judge it.** In [cloud](../../../cloud/README.md), store the quantity
   and, if it can cause an alert, add a threshold for it.
10. **Finish** with `unifold check --fix`, then `unifold check`.

Inside each part, start with its `AGENTS.md` and use the skills listed
there.

## What else changes

The measured quantities are restated in the context files of most units.
After step 2, list them with the `cited-by` command of the tool on
[conventions.md](../../references/conventions.md) and correct each
restatement that names the quantities.

## Checks

- The checker reports no error and no new warning.
- The end-to-end test of step 6 passes against the simulated sensor stick.
- A part that has not been updated still accepts readings that contain the
  new quantity.
