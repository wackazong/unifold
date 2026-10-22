# Configurations of a run

The two configurations the rig runs in, the settings that select them, and the waiting times. The tests are in the [test catalogue](test-catalogue.md), the terms in the [glossary](glossary.md). The reasons are in
[decision 0001](../decisions/0001-one-catalogue-for-real-and-simulated-devices.md).

## The two configurations

| | `real` | `simulated` |
|---|---|---|
| Device under test | A real sensor stick | A simulated device |
| `scenario-control` | Absent | Present |
| Sensor values | Whatever the sensor stick measures | Set by a scenario |
| Time on the device | Real; the rig waits | Simulated; the rig moves it forward |
| Sensor id | The one of the sensor stick | A new one for every scenario the rig loads |
| Tests that run | 9; the other 7 are reported as skipped | All 16 |
| Typical place | A machine next to the hardware, before a release | Developer machine, CI runner on every change |

The rig does not choose the configuration by a switch of its own. It is `simulated` exactly when the setting for `scenario-control` is present and the address answers. If the setting is present and the address does not answer, the run ends in error; the rig does not fall back to `real`.

## What the rig does without `scenario-control`

| Situation | Behaviour |
|---|---|
| A test runs in `simulated` only, according to the catalogue | Reported as skipped with the message "needs scenario-control" |
| A test needs a new reading | The rig waits in real time, up to one sampling interval plus 2 minutes; then the test ends in error "no reading in time" |
| A test compares values | The rig compares what it fetched with what the public API returns. It does not know what the values should be. |
| A test needs the device in its initial state | Not possible. The person who starts the run prepares the sensor stick; see the [skill](../skills/test-rig-run-against-real-hardware/SKILL.md). |
| The device holds readings from before the run | The rig fetches, uploads and confirms them like any others |

## Settings

Settings come from the environment of the run. None has a default that points at a real system.

| Setting | Content | Required |
|---|---|---|
| API address | Base address of the public API under test | Yes |
| Owner token | A token of the owner that exists for testing | Yes |
| Device | Sensor id of the device under test | No; without it the rig takes the only device in range that is open for pairing, and ends in error if there are several |
| Scenario control address | Address of `scenario-control` | No; its presence selects `simulated` |
| Report path | Where the report is written | No; default `test-report.xml` in the working directory |
| Groups | Which groups of the catalogue run | No; default all |

The token is never written to the report or to any output. The rig reads the sampling interval from the device under test.

## Waiting times

| Wait | `real` | `simulated` |
|---|---|---|
| Find the device under test | 30 seconds | 10 seconds |
| A new reading on the device | One sampling interval plus 2 minutes | Until `scenario-control` answers, at most 30 seconds |
| After creating or changing a plant, before the next upload | 60 seconds | The same |
| A reading in the history after an upload | 10 seconds, asked every second | The same |
| An alert after an upload | 60 seconds, asked every 2 seconds | The same |
| No alert after an upload | 60 seconds | The same |
| One request to the public API | 20 seconds | The same |
| The whole run | 3 hours | 30 minutes |

The waits that concern the public API are the times the rig expects of `cloud-api`.

A wait that runs out ends the test in error, with two exceptions: a reading that is missing from the history after 10 seconds and an alert that is missing after 60 seconds are failures, because these times are promises.

## Start and end of a run

| Moment | The rig |
|---|---|
| Start | Checks the settings and the token, removes every plant of the test owner. In `real`: finds and pairs the device under test and reads its identity. |
| Before each group and each test that names a scenario, `simulated` only | Loads the scenario with a sensor id the run has not used, then finds and pairs the device again |
| Before each group and each "fresh plant" | Removes the plant of the previous tests and creates a new one attached to the device |
| End, also after an error | Removes its plants, forgets the pairing, writes the report |

If the start fails, every test is reported as in error with the cause, and the report is still written.
