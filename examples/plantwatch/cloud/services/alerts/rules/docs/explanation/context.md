# Context of rules

What this unit takes over from the units above, and what each item means here.

## From alerts

### [alerts/0001 Evaluation and notification are libraries beside one process](../../../docs/decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md)

Judging is a library without state and without database access. What it must remember, it returns to the process that calls it. This gives the shape of the function: state in, state out.

### [alerts/0003 Thresholds reach the judging logic through an adapter](../../../docs/decisions/0003-thresholds-reach-the-judging-logic-through-an-adapter.md)

The logic that judges a reading asks for plant and thresholds through a function in its own words. An adapter of its own turns that into HTTP.

`rules` is that logic. Its need `thresholds` is a function call, and its contract is a reference of `alerts`, the unit that wires it. It knows no HTTP and keeps no answer.

### [alerts: glossary](../../../docs/references/glossary.md)

The evaluation state is what judging the earlier readings of a sensor stick concluded. A change is one "open" or "close" of an alert.

The evaluation state is the value that `evaluate` takes and returns, and the changes are the entries of its result.

## From cloud

### [cloud: public API, alerts](../../../../../../docs/references/public-api/alert.md)

The reference describes the behaviour that this unit implements:

- An alert is about one plant, one `quantity` and one `bound`: `min` when the judged value is below the lower threshold, `max` when it is above the upper one.
- Soil moisture and temperature are judged by the value of the reading. Light is judged by the highest value of the hour of the reading and the 24 full hours before it, and not during the first 24 hours of a plant.
- A reading with an estimated time, or not newer than the last judged reading of its sensor stick, is not judged.
- An alert opens when the judged value is beyond a threshold and none is open for the same plant, quantity and bound.
- An alert closes with `recovered` when the value is back on the good side by a margin of at most 10 percent of the range of the quantity, and with `threshold_changed` when the threshold is gone or has moved so that the last judged value is on its good side.

`rules` implements exactly this and chooses the margins within the bound. Closing with `expired` is not its business.

### [cloud: public API, general rules](../../../../../../docs/references/public-api/index.md)

A changed threshold applies to readings that are evaluated more than 60 seconds after the change. This rule sets the age that `rules` allows an answer of `thresholds` to have.

## From plantwatch

### [plantwatch: conventions, measured quantities](../../../../../../docs/references/conventions.md#measured-quantities)

Soil moisture is given in percent in steps of 0.1, light in lux in steps of 1, and temperature in °C in steps of 0.1. An unmeasured quantity is absent.

These are the units of the margins; no margin is smaller than a step. An absent quantity is not judged.

### [plantwatch: glossary](../../../../../../docs/references/glossary.md)

A threshold is a limit for one measured quantity of a plant. An alert opens once, stays open while the reason lasts, and closes.

The threshold is what `rules` compares, and the alert is what its "open" and "close" refer to.
