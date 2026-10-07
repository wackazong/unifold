---
name: test-rig-add-an-end-to-end-test
description: Add an end-to-end test to the test rig, or change one because its promise changed. Use it when a promise that spans the sensor link and the public API shall be guarded, not for behaviour that one part can test alone.
---
# Add an end-to-end test

A test of the rig guards a promise that is visible at public interfaces.
The procedure starts with the promise and ends with a test that runs in
every configuration it can.

## Steps

1. **State the promise** in one sentence that a user of the interfaces
   would sign, without naming an implementation. "A reading that is uploaded
   twice is stored once", not "the duplicate check works".
2. **Check that it belongs here.** If the promise can be observed at one
   interface alone and needs no second one, it is a test for whoever
   provides that interface. Say so to the human and stop.
3. **Find the observation.** Name what the rig will see at `cloud-api` or at
   the BLE link when the promise holds, and what it will see when it does
   not. If neither interface shows the difference, the promise cannot be
   tested here ([0002](../../decisions/0002-tests-observe-only-public-interfaces.md)).
   Do not reach behind the interface; report the gap.
4. **Choose the stimulus, without a scenario if possible.** Ask first
   whether the rig can provoke the situation through thresholds, repeated
   transfers or cut connections. Only if the promise is about a course of
   values or a span of time does the test need `scenario-control`.
5. **Add the entry to the catalogue.** In
   [test-catalogue.md](../../references/test-catalogue.md), add a section
   with a new id and the promise as its heading, and below it the
   configurations, the stimulus and the expected observation, in the right
   group. State values, not "soon" or "correct". Take numbers from the
   items cited in [context.md](../../context.md), not from memory. Ids are
   never reused. If the promise is part of a product promise, add the id to
   the table at the top of the catalogue.
6. **Write the test** so that it does exactly what the entry says. It
   - uses the waiting times of
     [configurations.md](../../references/configurations.md) and has none of
     its own,
   - creates what it needs and leaves nothing behind,
   - does not branch on the configuration to check something different
     ([0001](../../decisions/0001-one-catalogue-for-real-and-simulated-devices.md)),
   - words its failure as "expected … observed …" in terms of the entry.
7. **See it fail.** Run the test against a simulated device with the
   stimulus changed so that the promise is broken, for example a threshold
   that is not crossed. A test that cannot fail guards nothing.
8. **Run it in `simulated`,** ten times in a row. One failure in ten is a
   failing test.
9. **Run it in `real`** if the catalogue entry says so; follow
   [test-rig-run-against-real-hardware](../test-rig-run-against-real-hardware/SKILL.md).
10. **Update the counts** of tests per configuration in
    [configurations.md](../../references/configurations.md) and in the
    example of [README.md](../../../README.md).
11. **Finish.** Run the generator and the checker of the project and
    review the files you changed.

## Checks

- The catalogue entry and the test say the same thing.
- The report of a `real` run lists the new test as passed or as skipped
  with a reason, never as missing.
- The test passes ten times in a row in `simulated`.
- The test failed when the promise was broken on purpose.

## Reference

- [test-catalogue.md](../../references/test-catalogue.md)
- [configurations.md](../../references/configurations.md)
- [test-report.md](../../references/test-report.md): how results are
  worded
