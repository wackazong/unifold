---
status: proposed
date: 2026-10-06
---
# One catalogue for real and simulated devices; what cannot run is skipped

## Context and Problem Statement

The device under test is either a real sensor stick or a simulated one.
Only the simulated one comes with `scenario-control`, which lets a test set
sensor values and move time. Most end-to-end promises concern courses of
values over hours or days. How are the tests organised over the two kinds
of device?

## Decision Drivers

- A difference in behaviour between a real and a simulated device must
  become visible
- A run on real hardware must not look more complete than it is
- A new test costs one piece of work, not two

## Considered Options

- Two suites: one written for the simulated device, one for real hardware
- One suite that runs only against the simulated device; real hardware is
  tested by hand
- One catalogue; every test states the configurations it runs in; a test
  that needs `scenario-control` is reported as skipped when it is absent

## Decision Outcome

Chosen option: "one catalogue, skip what cannot run", because the same
test code then meets both kinds of device, and the report of a real run
lists by name what it did not cover.

A test never branches on the kind of device to check something different.
It either runs as written or is skipped. Where a promise can be tested on
real hardware by other means, that is a test of its own; ALERT-03 and
ALERT-04 of the [catalogue](../references/test-catalogue.md) reach alerts
by setting thresholds instead of values.

The rig is in the configuration `simulated` exactly when `scenario-control`
is configured and answers, and in `real` otherwise. The details are in
[configurations.md](../references/configurations.md).

### Consequences

- Good: a test that passes against one device and fails against the other
  points at a real difference, not at two different tests.
- Good: the number of skipped tests in a report is an honest measure of
  what real hardware was not asked.
- Good: tests that need no scenario are written without one, which keeps
  the share that runs on real hardware as large as possible.
- Bad: a real run takes far longer than a simulated one, because the rig
  waits for readings in real time.
- Bad: promises about courses of values are never checked on real
  hardware by the rig.
- Bad: a skipped test is easy to overlook. The report must be read, not
  only its exit status.
