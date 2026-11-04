# Context of plant-lookup

What this unit takes over from the units above, and what each item means here.

## From alerts

### [alerts/0003 Thresholds reach the judging logic through an adapter](../../../docs/decisions/0003-thresholds-reach-the-judging-logic-through-an-adapter.md)

The logic that judges a reading asks for plant and thresholds through a function in its own words. An adapter of its own turns that into HTTP.

`plant-lookup` is that adapter. HTTP, repeats, time limits and kept answers are its business and nobody else's. It may keep answers in memory.

## From cloud

### [cloud/0001 Services learn about readings through events, not calls](../../../../../docs/decisions/0001-services-learn-about-readings-through-events.md)

A service that needs state that changes rarely, such as the thresholds of a plant, asks for it with a call. No copy is kept current through events.

So `plant-lookup` asks when it is called. A copy of all thresholds is not an option inside this unit.

### [cloud: calls between services](../../../../../docs/references/service-calls.md)

An internal operation lies below `/internal/v1/` and carries no owner. A caller waits 5 seconds and repeats a failure at most twice, after 0.2 and 1 s.

These rules say how `plant-lookup` calls whoever provides `plants-api`, and why `lookup` takes at most 17 seconds.

### [cloud: public API, general rules](../../../../../../docs/references/public-api/index.md)

A changed threshold applies to readings that are evaluated more than 60 seconds after the change. This rule sets the longest time an answer is kept.

### [cloud: public API, errors](../../../../../../docs/references/public-api/error.md)

An error has the body `{"code", "message"}`; `404` is `not_found`, `503` is `unavailable`. These codes are the answer of the registry that means `unattached`, and the one that is repeated.

### [cloud: public API, plants](../../../../../../docs/references/public-api/plant.md)

Thresholds are given per quantity as an object with `min`, `max` or both. A plant has a `name` of 1 to 60 characters. This is the form in which thresholds arrive and are passed on.

### [cloud: glossary](../../../../../docs/references/glossary.md)

The registry is the stored plants with their owners, attached sensor sticks and thresholds. The registry is what `lookup` asks.

## From plantwatch

### [plantwatch: glossary](../../../../../../docs/references/glossary.md)

A sensor stick is attached to a plant when the plant names its sensor id. It is attached to at most one plant.

This is the question that `lookup` answers, and it gives the meaning of `attached` and `unattached`.

### [plantwatch: conventions, identifiers](../../../../../../docs/references/conventions.md#identifiers)

A sensor id is 16 lower-case hex digits. Plant and owner have a UUID in lower-case text form. These forms apply to the argument of `lookup` and the identifiers in its answer.
