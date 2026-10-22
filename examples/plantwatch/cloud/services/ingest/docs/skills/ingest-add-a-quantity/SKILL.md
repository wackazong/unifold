---
name: ingest-add-a-quantity
description: Make the ingest service check and publish a measured quantity that readings newly carry. Use it when the reading format has gained a quantity that the events do not contain yet.
---
# Add a measured quantity to ingest

The result: `ingest` checks the range of the new quantity and publishes it
under a name of its own in `data.values`. Subscribers that do not know the
name are not disturbed.

## Before you start

- The quantity is defined with unit, range and resolution in the project
  conventions, and it is part of `reading-format` as an optional field.
  Both lie outside this unit. If one is missing, stop.
- `ingest` already accepts readings that carry the new field: unknown
  fields are allowed and pass on unchanged inside `data.reading`. This
  procedure only adds the check and the named value.

## Steps

1. **Cite the quantity.** Add its unit and range to the item on measured
   quantities in [context](../../explanation/context.md).
2. **Name it.** Choose the name in `values`: the name of the quantity in
   lower case with underscores. Add a row to the table of names in
   [reading events](../../references/reading-events.md).
3. **Check that the change is compatible.** A new optional name in
   `values` needs no new topic. Anything else does; see "Versions" in
   [reading events](../../references/reading-events.md).
4. **Add the range check** so that a value outside the range leads to
   `rejected` with `value_out_of_range`, as for the existing quantities
   ([ingest API](../../references/ingest-api.md), checks on each reading).
5. **Publish the value** in `data.values` when the reading has it, and
   leave the name out when it does not.
6. **Test** the cases under "Checks".

## Checks

- A reading with the new quantity in range produces an event with the
  value in `values` and the unchanged reading in `reading`.
- A reading with the new quantity out of range is `rejected`; the other
  readings of the batch are not affected.
- A reading without the new quantity is accepted as before, and its event
  has no entry for the name.
- The `id` of an event did not change.

## Reference

- [reading events](../../references/reading-events.md): names in
  `values`, versions
- [ingest API](../../references/ingest-api.md): the order of checks
- [context](../../explanation/context.md): the ranges of the measured quantities
