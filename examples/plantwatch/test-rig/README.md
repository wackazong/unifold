---
unit: test-rig
summary: Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware
kind: test
status: planned
provides:
  test-report:
    kind: file
    summary: JUnit XML report of an end-to-end test run
    contract: doc/references/test-report.md
needs:
  device-under-test:
    kind: protocol
    summary: Something that speaks the sensor stick's BLE protocol, real or simulated
  scenario-control:
    kind: http
    summary: Lets a test set sensor values and advance time; exists only with a simulated device
    optional: true
  cloud-api:
    kind: http
    summary: The public API, to check that readings arrive and alerts are raised
  link-profile:
    kind: specification
    summary: The definition of the BLE services, to drive the device under test
  reading-format:
    kind: specification
    summary: The format of a reading, to build the batches the tests upload
---
# test-rig

test-rig checks the promises that no single part can check alone: a
reading taken by a sensor stick arrives in the history once, and a plant
that needs attention gets exactly one alert. It runs on a developer machine
or a CI runner. It plays the central itself: it fetches readings from a
device under test over BLE, uploads them to the public API under test, and
observes the result through that API.

## Provides

### `test-report`

One JUnit XML file per run.

- Every test of the [catalogue](doc/references/test-catalogue.md) that
  belongs to the run appears in the report as passed, failed, in error or
  skipped. A test is never left out.
- A skipped test names the reason, for example that the configuration
  cannot control sensor values.
- A failed test names the promise, what was expected and what was observed.
- The report states the configuration of the run: whether the device under
  test was real or simulated, its sensor id and the versions involved.
- The exit status of the run is 0 exactly when no test failed or ended in
  error and at least one test passed.

Limits: a report says what the rig observed at the public interfaces. It
does not say why a test failed inside the device under test or behind the
API. A run against a real sensor stick covers fewer promises than a run
against a simulated one; the report shows which.

Example: a run against a simulated device reports 16 passed tests. The
same commit against a real sensor stick reports 9 passed and 7 skipped with
the reason "needs scenario-control".

Contract: [test-report](doc/references/test-report.md).

## Needs

### `device-under-test`

Exactly one device in radio range of the machine that runs the rig, real
or simulated, that behaves as `link-profile` defines for a sensor stick.
The rig expects that it

- can be found by the rig as by any central and is open for pairing when
  the run starts,
- is connected to nothing else during the run,
- states its sensor id, its sampling interval and how many readings it
  keeps,
- takes readings by itself and serves the stored ones with tick counts,
- deletes readings only up to the sequence number the rig confirms.

The machine that runs the rig needs a BLE adapter that the rig may use
alone.

### `scenario-control`

Optional. A way to script the device under test instead of waiting for the
world. Where it exists, the rig expects that it

- loads a scenario: a course of values for soil moisture, light and
  temperature over simulated time, which states the sensor id of the
  simulated device and may contain a restart of the device,
- puts the device into its initial state whenever a scenario is loaded: no
  stored readings, not paired, open for pairing, and
- moves simulated time forward to a stated point and answers when the
  device has taken every reading that is due by then.

Without it the rig runs in the configuration `real`: it skips every test
that needs a scenario and reports it as skipped, it waits in real time for
the device to take a reading, and it checks only that values are valid, not
which values they are.

### `cloud-api`

The public API under test, reachable from the machine that runs the rig,
with a token of an owner that exists for testing only. The rig expects that
the API

- lets this owner create and remove plants with thresholds and bind a
  sensor id to a plant,
- accepts batches of readings and says for each reading whether it is new,
  known already or refused, and why,
- returns the history of a plant and its alerts, open and closed, and says
  for each alert whether its notification has been handed on,
- states how long it may take until a reading shows in the history, until
  an alert shows, and until a changed threshold applies, and
- answers errors with a code and a message.

The rig removes every plant of this owner at the start of a run, creates
the plants it needs, and removes them at the end.

### `link-profile`

The definition of the BLE services, characteristics and procedures of a
sensor stick, with a version. The rig implements the central side from
this definition alone and reports every deviation of the device under test
from it as a failed test.

### `reading-format`

The definition of the fields, units and identity of a reading, with a
version. The rig builds the batches it uploads from this definition and
compares the readings it fetches from the device under test with what the
public API returns.

## Out of scope

- Tests of a single part. Each part tests itself.
- What happens on a phone: screens, background fetching, the arrival of a
  notification. The rig observes the alert, not the message about it.
- Load, endurance and energy measurements.
- Starting or deploying what it tests. Device and API exist before a run.

## More

- [AGENTS.md](AGENTS.md): why the rig is built this way
- [Context diagram](doc/diagrams/context.md)
- [doc/context.md](doc/context.md): what the rig inherits from above
- [Test catalogue](doc/references/test-catalogue.md): the promises under
  test
- [Configurations](doc/references/configurations.md): `simulated` and
  `real`, and the settings of a run
- [Decisions](doc/decisions/index.md)
