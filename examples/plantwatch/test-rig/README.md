# test-rig

`test-rig` checks the promises that no single part can check alone: a reading taken by a sensor stick arrives in the history once, and a plant that needs attention gets exactly one alert. It runs on a developer machine or a CI runner. It plays the central itself: it fetches readings from a device under test over BLE, uploads them to the public API under test, and observes the result through that API.

## Why

Some promises hold only if several separately built things agree: a reading arrives once, a plant that needs attention gets one alert. Each thing can pass its own tests while the chain is broken at a seam. The rig exists to test the seams, and it is a unit of its own because these promises belong to none of the things it tests. It changes when such a promise is added or changed, or when one of the public interfaces it uses changes.

Three choices shape it. It touches only public interfaces, so its tests survive any rewrite behind them ([0002](docs/decisions/0002-tests-observe-only-public-interfaces.md)). One catalogue runs against a real sensor stick and a simulated device, so a difference between the two is a finding in itself ([0001](docs/decisions/0001-one-catalogue-for-real-and-simulated-devices.md)). And it plays the central itself instead of driving a phone ([0003](docs/decisions/0003-the-rig-is-its-own-central.md)): runs are fast and repeatable, and nothing that happens on a phone is covered.

What must stay true: a test that cannot run is reported as skipped with a reason. It is never dropped and never counted as passed.

## Capabilities

### `test-report`

A report says what the rig observed at the public interfaces. It does not say why a test failed inside the device under test or behind the API. A run in `real` covers fewer promises than a run in `simulated`; the skipped tests show which.

## Needs

### `device-under-test`

Exactly one device in radio range of the machine that runs the rig, open for pairing when the rig looks for it and connected to nothing else during the run. The machine needs a BLE adapter that the rig may use alone.

### `scenario-control`

Without it the rig runs in the configuration `real`: it skips every test that needs a scenario and reports it as skipped, it waits in real time for the device to take a reading, and it checks only that values are valid, not which values they are.

### `cloud-api`

The rig uses a token of an owner that exists for testing only. It removes every plant of this owner at the start of a run, creates the plants it needs, and removes them at the end.

## Out of scope

- Tests of a single part. Each part tests itself.
- What happens on a phone: screens, background fetching, the arrival of a notification. The rig observes the alert, not the message about it.
- Load, endurance and energy measurements.
- Starting or deploying what it tests. Device and API exist before a run.

## Read next

1. [docs/references/test-catalogue.md](docs/references/test-catalogue.md): the promises under test
2. [docs/references/configurations.md](docs/references/configurations.md): `real` and `simulated`, settings, waiting times
3. [test-report.md of plantwatch](../docs/references/test-report.md): the contract of the report
4. [docs/references/glossary.md](docs/references/glossary.md): promise, stimulus, configuration, group
5. [Context diagram](docs/diagrams/context.md)
6. [docs/explanation/context.md](docs/explanation/context.md): what the rig inherits from above
7. [Decisions](docs/decisions/index.md)
