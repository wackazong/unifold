# Context of rules

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

| Source | What it says | What it means here |
|---|---|---|
| [alerts/0001 Evaluation and notification are libraries beside one process](../../doc/decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md) | Judging is a library without state and without database access. What it must remember, it returns to the process that calls it. | The shape of the function: state in, state out. |
| [cloud: public API, alerts](../../../../doc/references/public-api/alerts.md) | An alert is about one plant, one `quantity` and one `bound` (`min` or `max`). Soil moisture and temperature are judged by the value of the reading, light by the highest value of the day that ends with the reading (its hour and the 24 full hours before it) and not during the first 24 hours. An alert closes with `recovered` when the value is back by a margin whose size is not part of the contract, and with `threshold_changed` when the threshold is gone or has moved to the other side of the last judged value. A reading with an estimated time or older than the last judged one is not judged. | The behaviour that `rules` implements. `rules` chooses the margins. Closing with `expired` is not its business. |
| [cloud: public API, plants](../../../../doc/references/public-api/plants.md) | Thresholds are given per quantity as `min`, `max` or both. `min` is the threshold below which the plant needs attention, `max` the one above which it does. | The meaning of what the need `thresholds` returns. |
| [cloud: public API, general rules](../../../../doc/references/public-api/index.md) | A changed threshold applies to readings that are evaluated more than 60 seconds after the change. | The longest time `rules` may reuse a lookup. |
| [cloud: calls between services](../../../../doc/references/service-calls.md) | A caller waits at most 5 seconds and repeats a failed call at most twice, after 0.2 and 1 second. Internal operations carry no owner header. | How `rules` calls whoever provides `thresholds`. |
| [plantwatch: measured quantities](../../../../../doc/references/conventions.md) | Soil moisture 0 to 100 percent, resolution 0.1. Light 0 to 100 000 lux, resolution 1. Temperature -20 to 60 degrees Celsius, resolution 0.1. An unmeasured quantity is absent. | The units of the margins. An absent quantity is not judged. |
| [plantwatch: HTTP ports](../../../../../doc/references/conventions.md) | Bodies are JSON in UTF-8 with lower-case field names; an error has `code` and `message`. | The form `rules` expects from the lookup. |
| [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | A reading whose time could not be computed is marked as having an estimated time. | `rules` does not judge such a reading, because it cannot place it among the others. |
| [plantwatch: threshold, alert](../../../../../doc/references/glossary.md) | A threshold is a limit for one measured quantity of a plant. An alert opens once, stays open while the reason lasts, and closes. | What `rules` compares, and what its "open" and "close" refer to. |
