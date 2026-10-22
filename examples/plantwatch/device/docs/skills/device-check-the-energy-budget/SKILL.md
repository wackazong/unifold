---
name: device-check-the-energy-budget
description: Check a change to the sensor stick firmware against its energy budget, first by calculation and then by measurement on a board. Use it when a change makes the board wake more often, stay awake longer, use the radio more or power another part.
---

# Check a change against the energy budget

The result is an updated energy budget and a clear answer: the change fits, or it needs a decision. The procedure exists because a change of a few lines can halve the life of the cell without failing any test.

## Steps

1. **Name the events** the change adds or alters: how often per day, and what is powered for how long in each.
2. **Compute the charge per event**: current times duration for each powered part, summed. Take currents from the data sheet, or from the measured values in the [energy budget](../../references/energy-budget.md) if they exist.
3. **Compute the average current**: charge per event times events per day, divided by 86 400 s.
4. **Compare.** Add the result to the sum in the budget.
   - The change adds less than 1 µA and the sum stays below the allowed average: go on.
   - The change adds more than 1 µA, or the reserve falls below 3 µA: stop and write a decision in [decisions](../../decisions/index.md) with status `proposed`, stating what the change costs in months of cell life.
5. **Enter the planned figures** in the budget table: a new row for a new activity, a changed row otherwise. Mark them as planned.
6. **Measure, when a board exists.** Supply the board with 3.0 V through a current analyser. Record at least one hour that contains the new event at its normal rate, with no central connected, then one connection with a fetch.
7. **Take three numbers from the recording**: the current while asleep, the charge of one event of each kind, the average over the hour.
8. **Replace the planned figures** by the measured ones and state the date and the board revision in the table. If measurement and plan differ by more than a quarter, find out why before going on.
9. **Repeat at 2.2 V.** Parts draw differently from a weak cell, and the board must still start and write memory.

## Checks

- The rows of the budget table add up to the sum shown.
- The cell life computed from the sum is 12 months or more.
- The sleeping current is measured over at least 10 minutes without an event of the new kind; a part that is not switched off shows here and nowhere else.
- [README.md](../../../README.md) still tells the truth about cell life and about what shortens it.

## Reference

- [Energy budget](../../references/energy-budget.md): the table to update and the limits that follow from it
- [Decision 0001](../../decisions/0001-sleep-between-events-and-advertise-all-the-time.md):
  why advertising takes the largest share
