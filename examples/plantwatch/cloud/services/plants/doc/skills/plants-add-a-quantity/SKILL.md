---
name: plants-add-a-quantity
description: Give a new measured quantity thresholds and a history in the plants service. Use it when reading events carry a quantity that plants does not store yet.
---
# Add a measured quantity to plants

The result: a plant can have thresholds for the new quantity, and the
history returns it in raw readings and in aggregates. Rows written before
the change stay valid.

## Before you start

- The quantity is defined in the project conventions and is part of the
  plant and of the history in the contract that this unit serves. Both lie
  outside this unit ([context](../../context.md)). If one is missing,
  stop.
- Events that already carry the new name in `values` are handled without
  error: `plants` ignores names it does not know. Their values do not
  enter the aggregates; see step 5.

## Steps

1. **Cite the quantity.** Add its unit, range and resolution to the item
   on measured quantities in [context](../../context.md), and its name to
   the table of fields in
   [reading events](../../references/reading-events.md).
2. **Extend the data model.** Add the column for the value to `reading`
   and the three columns for `min`, `mean` and `max` to `hour_aggregate`
   in [data model](../../references/data-model.md).
3. **Write the migration.** The new columns allow empty values and have
   no default, so the migration is quick and the previous version of the
   service keeps running during it.
4. **Change the handling of events.** Store the value from `values` and
   include the quantity when the hour is recomputed.
5. **Mind the order of rollout.** Readings that were handled before this
   change keep an empty value for the new quantity: a stored reading is
   never handled again, and this unit does not interpret the stored
   `reading` field. Deploy this change before events carry the quantity.
   If that order was missed, tell a human which period has the gap.
6. **Change the validation of thresholds.** Accept `min` and `max` for
   the new quantity within its range.
7. **Change the history response.** Return the quantity in aggregates. A
   raw reading already contains it.
8. **Test** the cases under "Checks".

## Checks

- A `PUT` with a threshold for the new quantity outside its range gets
  `400`; inside the range it is stored and returned by the lookup by
  sensor id.
- An event with the quantity leads to an hourly aggregate with its `min`,
  `mean` and `max`.
- An hour whose readings lack the quantity has no entry for it.
- The same event handled twice leaves `count` and all aggregates
  unchanged.
- A history request over a period before the change still works.

## Reference

- [data model](../../references/data-model.md): tables, how an event
  changes them
- [plants API](../../references/plants-api.md): the lookup by sensor id
- [context](../../context.md): the contract of plants and history, the
  measured quantities
