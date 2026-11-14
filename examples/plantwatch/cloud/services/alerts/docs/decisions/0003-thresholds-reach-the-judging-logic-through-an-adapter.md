---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Thresholds reach the judging logic through an adapter

## Context and Problem Statement

To judge a reading, the judging logic must know the plant of the sensor stick and its thresholds. Both live in the registry of plants, which `alerts` reaches through its need `plants-api`, over HTTP. The library that judges had declared that HTTP need itself. It also repeated failed calls and kept answers for 60 seconds. That contradicts the reason for which judging is a library
([0001](0001-evaluation-and-notification-are-libraries-beside-one-process.md)):
logic that is pure and can be tested with tables of readings. Who talks to the registry?

## Considered Options

- The judging library calls the registry over HTTP itself
- The process looks up plant and thresholds and passes them to the judging library as an argument
- The judging library states a need for a lookup function, in its own words and with a contract it owns; an adapter unit provides that function and needs `plants-api`

## Decision Outcome

Chosen option: "a need for a lookup function, met by an adapter", because the judging logic then depends on nothing but functions, and everything that has to do with the network sits in one small unit that changes for its own reasons.

The adapter is [plant-lookup](../../plant-lookup/README.md). It is built into the same program as the other children. Unlike them it may keep state between two calls: answers of the registry, in memory, for a time that it decides and states in its port. That is the one exception to the rule of
[0001](0001-evaluation-and-notification-are-libraries-beside-one-process.md)
that a library has no state of its own. Nothing depends on this state surviving.

Notifying follows the same pattern: [notifier](../../notifier/README.md) stands between a need of the process for a function and the HTTP need `push`.

### Consequences

- Good: the judging logic is tested with a stand-in that returns fixed answers. No test of a rule needs a network.
- Good: path, time limits, repeats and kept answers are stated and tested in one place.
- Good: another source of thresholds replaces the adapter and nothing else.
- Good: every need of this unit that is met over HTTP is passed to an adapter, and the judging library names no HTTP interface at all.
- Bad: one more unit and one more contract to keep in step. The interface between the judging logic and the adapter is written down on both sides.
- Bad: a judgement still depends on an answer from outside its arguments. It is the same for the same reading, state and answer, not for the same reading and state alone.
- Bad: the kept answers are state outside the database, per instance.

## Pros and Cons of the Options

### The judging library calls the registry itself

- Good: one unit less.
- Bad: the unit that changes with every new rule also changes with every change of an HTTP interface, and its tests need a fake server.

### The process looks up and passes thresholds as an argument

- Good: judging becomes a function of its arguments alone.
- Bad: the process would have to know when a lookup is needed. A reading with an estimated time, or older than the last judged one, needs none; that is a rule of judging.
- Bad: the process would learn about plants and thresholds, which it is kept free of.
