---
name: test-rig-run-against-real-hardware
description: Run the end-to-end tests of the test rig against a real sensor stick instead of a simulated device, and read the result correctly. Use it before a release, after a real sensor stick has changed, or when a simulated run and reality seem to disagree.
---
# Run the tests against real hardware

A run in the configuration `real` waits for readings in real time and
covers only the tests the
[catalogue](../../references/test-catalogue.md) marks `real`; the
durations are in [configurations.md](../../references/configurations.md).
It consumes the readings of the sensor stick it runs against.
The procedure makes sure the right sensor stick is used and that the
skipped tests are not mistaken for passed ones.

## Steps

1. **Take a sensor stick that is set aside for testing.** The run confirms
   its readings, and the sensor stick deletes them. Never use one that
   belongs to somebody's plant.
2. **Prepare the machine.** It needs a BLE adapter that nothing else uses.
   Put the sensor stick within one metre. Keep other sensor sticks that are
   open for pairing out of range, or name the sensor id in the settings.
3. **Prepare the API.** Point the settings at a public API that is meant
   for testing, with a token of the test owner. The run removes every
   plant of that owner. Do not run against a system with real owners.
4. **Open the sensor stick for pairing directly before the run.** A sensor
   stick accepts a new central only for a limited time after it has
   started, as `link-profile` defines. Take the cell out, put it back in,
   and start the run within two minutes. Leave the probe in air or in dry
   soil; the tests do not depend on the values.
5. **Leave the scenario control address unset.** Its absence is what
   selects `real`
   ([configurations.md](../../references/configurations.md)). If it is set
   and points at a simulated device, the rig will script that device while
   fetching from the real one, and the results mean nothing.
6. **Start the run** with all groups. Do not move the sensor stick or the
   machine during the run.
7. **Read the report,** not only the exit status
   ([test-report.md](../../references/test-report.md)):
   - `configuration` must be `real` and `sensor-id` the one you prepared.
   - Exactly the tests marked `simulated` only in the
     [catalogue](../../references/test-catalogue.md) are skipped, each with
     "needs scenario-control". Any other skipped test is a fault.
   - An error of type `environment` at the start usually means that the
     sensor stick was no longer open for pairing. Repeat step 4.
   - An error of type `environment` with "no reading in time" means that
     the sensor stick stopped taking readings or went out of range.
8. **Compare with a simulated run of the same commit.** A test that passes
   there and fails here, or the reverse, points at a difference between the
   two devices or at a gap in `link-profile`. Report it as such; do not
   adapt the test to make both agree.
9. **Clean up.** Check that the run has removed its plants. After a run
   that was cut off, nothing has to be done by hand: the next run removes
   the test owner's plants at its start and pairs again.

## Checks

- The report states `real` and the expected sensor id.
- Every test marked `real` in the catalogue ran; every other test is
  skipped with the reason "needs scenario-control".
- Differences to the simulated run are in your report to the human.

## Reference

- [configurations.md](../../references/configurations.md): settings and
  waiting times
- [test-catalogue.md](../../references/test-catalogue.md): which tests run
  where
- [test-report.md](../../references/test-report.md): how to read the result
