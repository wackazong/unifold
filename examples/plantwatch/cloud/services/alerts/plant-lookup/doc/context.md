# Context of plant-lookup

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From alerts

### [alerts/0003 Thresholds reach the judging logic through an adapter](../../doc/decisions/0003-thresholds-reach-the-judging-logic-through-an-adapter.md)

Says: the logic that judges a reading asks for plant and thresholds through
a function in its own words. An adapter of its own turns that into HTTP.

Here: `plant-lookup` is that adapter. HTTP, repeats, time limits and kept
answers are its business and nobody else's. It may keep answers in memory.

## From cloud

### [cloud/0001 Services learn about readings through events, not calls](../../../../doc/decisions/0001-services-learn-about-readings-through-events.md)

Says: a service that needs state that changes rarely, such as the thresholds
of a plant, asks for it with a call. No copy is kept current through events.

Here: `plant-lookup` asks when it is called. A copy of all thresholds is not
an option inside this unit.

### [cloud: calls between services](../../../../doc/references/service-calls.md)

Says: an internal operation lies below `/internal/v1/` and carries no owner. A
caller waits 5 seconds and repeats a failure at most twice, after 0.2 and 1 s.

Here: how `plant-lookup` calls whoever provides `plants-api`, and why
`lookup` takes at most 17 seconds.

### [cloud: public API, general rules](../../../../doc/references/public-api/index.md)

Says: a changed threshold applies to readings that are evaluated more than
60 seconds after the change. An error has a `code`; `404` is `not_found`.

Here: the longest time an answer is kept, and the answer that means
`unattached`.

### [cloud: public API, plants](../../../../doc/references/public-api/plants.md)

Says: thresholds are given per quantity as an object with `min`, `max` or
both. A plant has a `name` of 1 to 60 characters.

Here: the form in which thresholds arrive and are passed on.

### [cloud: glossary](../../../../doc/references/glossary.md)

Says: a sensor stick is attached to a plant when the plant names its sensor
id, to at most one plant. The registry is the stored plants with thresholds.

Here: the question that `lookup` answers, and the meaning of `attached` and
`unattached`.

## From plantwatch

### [plantwatch: conventions, identifiers](../../../../../doc/references/conventions.md)

Says: a sensor id is 16 lower-case hex digits. Plant and owner have a UUID
in lower-case text form.

Here: the argument of `lookup` and the identifiers in its answer.
