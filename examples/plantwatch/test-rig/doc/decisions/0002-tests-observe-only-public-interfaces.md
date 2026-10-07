---
status: proposed
date: 2026-10-06
---
# Tests observe only public interfaces

## Context and Problem Statement

An end-to-end test has to find out whether a reading arrived and whether
an alert was raised. The quickest way to find out is often to look inside:
a database row, a log line, a message on an internal bus, a debug command
of a device. What may a test of the rig look at?

## Considered Options

- Whatever is convenient: databases, logs, internal messages, debug hooks
- Public interfaces, plus read-only access to internals for diagnosis when
  a test fails
- Public interfaces only: the BLE link as `link-profile` defines it,
  `scenario-control` where it exists, and the public API

## Decision Outcome

Chosen option: "public interfaces only", because a promise that cannot be
observed from outside is not a promise to anyone, and because tests that
look inside break with every internal change and then get switched off.

The rig shares no code with anything it tests. It builds its central from
`link-profile` and its API client from the documented public API.

`scenario-control` is a stimulus, not an observation: the rig uses it to
set values and move time, never to ask what the device under test did.

### Consequences

- Good: everything behind the interfaces can be rewritten without touching
  a test.
- Good: the rig can test any device and any server that keep the public
  interfaces, including ones it has never seen.
- Good: a failing test describes a fault in terms a user of the interfaces
  understands.
- Bad: a failure says what is wrong at the interface, not where the fault
  lies behind it. Finding the cause is work for whoever owns the part.
- Bad: what the public API does not show cannot be tested. The message to
  the owner about an alert is the main example.
- Bad: tests wait for outcomes through the API instead of being told, so
  they poll and need waiting times.
