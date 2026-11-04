---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Fixed slots instead of free prose: qualities, events, binding, carrier, version, configuration

## Context and Problem Statement

What a connection promises beyond its parts, such as latency, throughput, delivery or limits, ended up in prose scattered over sections that each contract invented. Which units are processes, how a connection travels, and which settings differ per deployment had no place at all. Implementers need these first. Where do they go?

## Decision

- `## Qualities` of a contract is a table `Aspect | Guarantee`, one row per aspect: latency, throughput, concurrency, ordering, delivery, idempotency, timeout, availability, limits, security, or others. The checker reads the form of the table.
- An event has `When:` (what raises it) and `Delivery:` (at-most-once, at-least-once or exactly-once, and the order key), and examples with `Action` and `Emitted`.
- The header of a contract may say `Binding:` (how the connection travels), `Carried by:` (a link to the contract of the transport an event stream rides on; a hop on the stream counts as a use of the carrier) and `Version:` (a contract of a capability or need of the root should have one; a breaking change of such a contract should be a decision).
- The manifest key `runs-as` says what a unit runs as.
- Configuration is a need: its contract lists the settings as parts, with name, type, default and who sets each; its fake is a table of values.

## Consequences

- Good: an implementer finds the guarantees, the transport and the settings in fixed places, and a contract invents no sections.
- Bad: a few more lines per contract, and a table where a sentence would have done.
