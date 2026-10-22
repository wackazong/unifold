---
name: rules-add-a-quantity
description: Make the rules library judge a measured quantity it does not judge yet. Use it when readings carry a new quantity that shall open and close alerts.
---

# Add a measured quantity to rules

The result: `evaluate` returns "open" and "close" for the new quantity, with a margin of its own. States written before the change stay readable.

## Before you start

- The quantity is defined with unit, range and resolution, thresholds for it can exist, and the contract that this unit implements names it. All of that lies outside this unit ([context](../../explanation/context.md)). If something is missing, stop.
- Know how the quantity is judged: by the value of the reading, or over a period. Judging over a period needs memory in the state and must be agreed before you start.

## Steps

1. **Cite the quantity** with unit and resolution in the item on measured quantities in [context](../../explanation/context.md).
2. **Add the judged value** as a row to the table "Judged value" in
   [evaluation](../../../../docs/references/evaluation.md).
3. **Choose the margin.** It is in the unit of the quantity, at least five times its resolution, and small against the usual distance between a threshold and the normal value. Add it to the table "Margins". Have a human confirm the number.
4. **If the quantity needs memory**, add a field to the state, describe it in the section "State", and keep `v` at its value as long as an old state without the field is still read correctly. Otherwise raise `v` and write the code that reads both forms.
5. **Write the tests first**, each as a sequence of readings with the expected changes, and add the first of them to the table "Examples": see "Checks". The tests meet the need `thresholds` with a table of answers, not with a network.
6. **Implement** the judged value and the margin. The table "Opening and closing" applies unchanged; do not add a special case there.
7. **Check the size** of the state with the new field against the limit of 4 kB.

## Checks

Each is a test with a sequence of readings:

- Below `min`: one "open". Further readings below: no change.
- Back above `min` but inside the margin: no change. Beyond the margin: one "close" with `recovered`.
- The same two for `max`.
- The threshold removed while open: "close" with `threshold_changed`.
- A reading without the quantity while open: no change.
- The same reading passed twice: the second call returns no changes and the same state.
- A state written before this change, passed with a reading that has the new quantity: no error, and what was open stays open.

## Reference

- [evaluation](../../../../docs/references/evaluation.md): judged values, opening and closing, margins, state
- [0001](../../decisions/0001-flapping-is-prevented-by-a-margin-on-closing.md):
  what a margin is for and how large it must be
