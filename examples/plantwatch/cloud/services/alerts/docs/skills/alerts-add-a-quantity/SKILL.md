---
name: alerts-add-a-quantity
description: Make a new measured quantity able to cause an alert in the alerts service. Use it when plants can have thresholds for a quantity that alerts does not judge yet.
---
# Add a measured quantity to alerts

The result: a reading that violates a threshold of the new quantity opens
an alert, and the owner gets a notification with fitting words. The work
happens in two children; this procedure gives the order.

## Before you start

- The quantity is defined in the project conventions, reading events
  carry it, and the contract of alerts that this unit serves names it as
  a value of `quantity`. All three lie outside this unit
  ([context](../../explanation/context.md)). If one is missing, stop.
- Decide with a human how the quantity is judged: per reading, or over a
  period as light is. If over a period, record a decision in this unit
  first.

## Steps

1. **Check the contract.** The item on the public API in
   [context](../../explanation/context.md) must name the quantity. Add it there.
2. **Word the notification first.** In
   [notifier](../../../notifier/README.md), add the texts for the new
   quantity, one for each bound, with the skill of that unit. Until this
   is done, an alert of the new quantity could not be told to the owner.
3. **Then judge it.** In [rules](../../../rules/README.md), add the
   quantity with its margin, with the skill of that unit. From the
   release that contains this step on, alerts of the new quantity open.
4. **Check the rest.** [server](../../../server/README.md) stores and
   returns any quantity name it is given, and
   [plant-lookup](../../../plant-lookup/README.md) passes on thresholds
   for any quantity name. Confirm both with a test; no change is expected
   there.
5. **Release** the service as a whole.

## Checks

- A sequence of readings that crosses a threshold of the new quantity
  and comes back opens one alert, sends one notification and closes the
  alert.
- The same sequence handled twice gives the same single alert.
- Readings without the new quantity change nothing for it.
- Alerts of the existing quantities behave as before.

## Reference

- [invariants](../../explanation/invariants.md),
  [runtime](../../explanation/runtime.md): invariants and the life of an
  alert
- [context](../../explanation/context.md): the contract of alerts, the measured
  quantities
