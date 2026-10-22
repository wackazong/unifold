# test-rig

test-rig checks the promises that no single part can check alone: a reading taken by a sensor stick arrives in the history once, and a plant that needs attention gets exactly one alert. It runs on a developer machine or a CI runner. It plays the central itself: it fetches readings from a device under test over BLE, uploads them to the public API under test, and observes the result through that API.

## Why

Some promises hold only if several separately built things agree: a reading arrives once, a plant that needs attention gets one alert. Each thing can pass its own tests while the chain is broken at a seam. The rig exists to test the seams, and it is a unit of its own because these promises belong to none of the things it tests. It changes when such a promise is added or changed, or when one of the public interfaces it uses changes.

Three choices shape it. It touches only public interfaces, so its tests survive any rewrite behind them ([0002](docs/decisions/0002-tests-observe-only-public-interfaces.md)). One catalogue runs against a real sensor stick and a simulated device, so a difference between the two is a finding in itself
([0001](docs/decisions/0001-one-catalogue-for-real-and-simulated-devices.md)).
And it plays the central itself instead of driving a phone ([0003](docs/decisions/0003-the-rig-is-its-own-central.md)): runs are fast and repeatable, and nothing that happens on a phone is covered.

What must stay true: a test that cannot run is reported as skipped with a reason. It is never dropped and never counted as passed.

## Capabilities

### `test-report`

One JUnit XML file per run.

- Every test of the [catalogue](docs/references/test-catalogue.md) that belongs to the run appears in the report as passed, failed, in error or skipped. A test is never left out.
- A skipped test names the reason, for example that the configuration cannot control sensor values.
- A failed test names the promise, what was expected and what was observed.
- The report states the configuration of the run, `real` or `simulated`, the sensor id of the device under test and the versions involved.
- The exit status of the run is 0 exactly when no test failed or ended in error and at least one test passed.

Limits: a report says what the rig observed at the public interfaces. It does not say why a test failed inside the device under test or behind the API. A run in `real` covers fewer promises than a run in `simulated`; the report shows which.

Example: a run in `simulated` reports 16 passed tests. The same commit in `real` reports 9 passed and 7 skipped with the reason "needs scenario-control".

Contract: [test-report](docs/references/test-report.md).

## Needs

The rig defines none of these interfaces. It takes each as its provider defines it and states here what it relies on.

### `device-under-test`

Exactly one device in radio range of the machine that runs the rig, real or simulated, that behaves as the BLE profile defines for a sensor stick. The rig relies on that it

- can be found by the rig as by any central and is open for pairing when the rig looks for it,
- is connected to nothing else during the run,
- states its sensor id, its sampling interval and how many readings it keeps,
- takes one reading per sampling interval of its own time and serves the stored ones with tick counts, and
- deletes readings only up to the sequence number the rig confirms or, when its memory is full, the oldest ones, and reports that it did.

The machine that runs the rig needs a BLE adapter that the rig may use alone.

### `scenario-control`

Optional. A way to script the device under test instead of waiting for the world. Where it exists, the rig relies on that it

- loads a scenario: values for soil moisture, light and temperature over simulated time, the sensor id of the simulated device, and optionally a restart of the device,
- puts the device into its initial state whenever a scenario is loaded: no reading from before, not paired, open for pairing,
- moves simulated time forward to a stated point and answers when the device has taken every reading that is due by then, and
- makes the device report, for a moment at which the scenario states a value, exactly that value at the resolution of its quantity.

Without it the rig runs in the configuration `real`: it skips every test that needs a scenario and reports it as skipped, it waits in real time for the device to take a reading, and it checks only that values are valid, not which values they are.

### `cloud-api`

The public API under test, reachable from the machine that runs the rig, with a token of an owner that exists for testing only. The rig relies on that the API

- lets this owner create and remove plants with thresholds and bind a sensor id to a plant,
- accepts batches of readings and says for each reading whether it is new, known already or refused, and why,
- returns the history of a plant and its alerts, open and closed, and says for each alert whether its notification has been handed on,
- shows an accepted reading in the history within 10 seconds and an alert within 60 seconds after the upload, and applies a changed threshold to readings uploaded 60 seconds or more after the change, and
- answers errors with a code and a message.

The rig removes every plant of this owner at the start of a run, creates the plants it needs, and removes them at the end.

## Out of scope

- Tests of a single part. Each part tests itself.
- What happens on a phone: screens, background fetching, the arrival of a notification. The rig observes the alert, not the message about it.
- Load, endurance and energy measurements.
- Starting or deploying what it tests. Device and API exist before a run.

## Read next

1. [docs/references/test-catalogue.md](docs/references/test-catalogue.md): the promises under test
2. [docs/references/configurations.md](docs/references/configurations.md):
   `real` and `simulated`, settings, waiting times
3. [docs/references/test-report.md](docs/references/test-report.md): the contract of the report
4. [docs/references/glossary.md](docs/references/glossary.md): promise, stimulus, configuration, group
5. [Context diagram](docs/diagrams/context.md)
6. [docs/explanation/context.md](docs/explanation/context.md): what the rig inherits from above
7. [Decisions](docs/decisions/index.md)
