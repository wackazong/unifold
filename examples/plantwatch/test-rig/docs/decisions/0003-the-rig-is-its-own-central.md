---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# The rig is its own central and does not drive a phone

## Context and Problem Statement

Between the device under test and the public API a reading is carried by a central, in daily use a phone. An end-to-end test needs something in that place. What carries the readings during a test?

## Decision Drivers

- Runs on a CI runner without special hardware beyond a BLE adapter
- Deterministic: the test decides when a fetch and an upload happen
- The test can misbehave on purpose: fetch twice, cut a connection, upload a batch again

## Considered Options

- Drive a real phone, or a phone simulator, through its user interface
- Reuse, inside the rig, the code that fetches and uploads on a phone
- The rig implements a minimal central and API client of its own

## Decision Outcome

Chosen option: "a minimal central and API client of its own", because the tests need control over every step of the transfer, which a phone does not give, and because the rig must not share code with what could be under test
([0002](0002-tests-observe-only-public-interfaces.md)).

The rig's central does what the BLE profile asks of a central and nothing more: find, pair, fetch, confirm, read the tick count, convert to UTC. It uploads what it fetched, unchanged, as readings in the reading schema.

### Consequences

- Good: a run needs one machine, one BLE adapter and no phone.
- Good: the tests for repeated and interrupted transfers are possible at all.
- Good: the rig is a third reading of the BLE profile, next to the devices it tests. Disagreements surface early.
- Bad: nothing that happens on a phone is tested here, for example fetching in the background or the arrival of a notification.
- Bad: the rig's central can be wrong in its own way. A failed `link` test needs a look at the definition before anyone is blamed.
- Bad: the conversion of tick counts to UTC exists once more, in the rig.
