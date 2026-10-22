---
name: device-add-a-sensor-driver
description: Add a driver for a sensor part to the sensor stick firmware, or replace the part behind an existing quantity. Use it when the board gets a new or a different sensor.
---
# Add a sensor driver

The result is a firmware in which a new or replaced sensor part delivers
its quantity in readings, with the hardware access in one part and the
conversion in another. The order below keeps every step testable before
the next one starts.

## Steps

1. **Decide which case it is.**
   - *Replacement*: the quantity exists; another part measures it. No
     interface of this unit changes. Continue with step 3.
   - *New hardware*: the board gets a sensor it did not have. This unit
     gets a new need. Continue with step 2.
   - *New quantity*: readings get a value they did not have. That changes
     the definition behind `link-profile` and is not decided here. Stop
     and take it to whoever owns that definition; come back when it is
     changed.
2. **Declare the hardware.** Add a need of kind `hardware` to the
   manifest, [unifold.yaml](../../../unifold.yaml), and describe in the `README.md`
   what the firmware expects of the part: supply, bus, timing, idle
   current. Whoever composes this unit has to meet the new need.
3. **Check the energy first.** Take supply current, measuring time and
   idle current from the data sheet and run
   [device-check-the-energy-budget](../device-check-the-energy-budget/SKILL.md).
   If the part does not fit, stop here.
4. **Write the driver** in [hal](../../../hal/README.md). The driver
   delivers a raw value and can report it as unavailable. It contains no
   conversion to a physical unit. Work inside that unit by its own
   documents.
5. **Write the conversion** in [sampling](../../../sampling/README.md):
   from the raw value to the quantity, with range and rounding. Work
   inside that unit by its own documents and skills. Then read both ends
   of the wiring line that joins the two: scale, range, timing and
   "unavailable" of the raw value must agree.
6. **Test without a board.** Run the conversion against a table of raw
   values, including "unavailable", the lowest and the highest raw value.
7. **Test on a board.** Take 100 readings. Disconnect the sensor during
   the run: the quantity must become absent and readings must go on.
8. **Measure the energy** and replace the planned values, as the skill of
   step 3 describes.
9. **Update the documents**: the limits in
   [README.md](../../../README.md) if a guarantee changed, and
   [runtime.md](../../explanation/runtime.md) if a duration in its table
   changed. Run the unifold generator and checker.

## Checks

- No file outside the hardware part mentions the sensor part by name.
- A failed sensor makes one quantity absent. It does not stop sampling
  and does not delay a reading by more than 1 s.
- The sum in the [energy budget](../../references/energy-budget.md) is
  still below the allowed average.
- Between two readings the sensor draws its idle current, measured, not
  assumed.

## Reference

- [Energy budget](../../references/energy-budget.md): what one reading
  may cost
- [Invariants](../../explanation/invariants.md): the invariants a driver must not
  break
