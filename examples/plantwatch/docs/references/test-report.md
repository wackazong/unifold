# test-report

Contract of `test-rig.test-report`: the file a run of the rig produces, and the exit status that goes with it. Readers are developers and the tools of a CI system that understand JUnit XML. The tests and the configurations are listed by [test-rig](../../test-rig/README.md). Notation: JUnit XML and the exit status of the run, as text.
Sources: the JUnit XML format as CI tools read it; the test catalogue of `test-rig`.

## Stability

- The id at the start of a `testcase` name never changes and is never reused. Tools that track a test over time match on the id.
- New properties and new tests may be added at any time. Readers ignore what they do not know.
- No token, no owner's data other than the rig's own test plants, and no value of a setting other than those listed under `properties` appears in the file.

## Parts

### run

Kind: command

```text
run(settings: configuration, selected groups, report path) -> report file + exit status
```

Pre: the settings name a configuration and a report path; device and API exist before a run.
Result: one report file per run, written always, also when the run could not start or was cut off by its time limit, at the report path of the settings; and an exit status: 0 when there is no failure, no error, and at least one test passed; 1 when there is at least one failure or error, or no test passed. Skipped tests do not change the exit status.
Errors: exit status 2 when the settings are incomplete; no test was attempted, and the report contains every selected test as in error.
Examples:

| Case | Input | Expected |
|---|---|---|
| one failure | group `alert` in `real`: ALERT-01 is skipped, ALERT-04 fails | the report below; exit status 1 |
| all pass | a group whose tests all pass | a report without `failure` and `error`; exit status 0 |
| no settings | no report path given | exit status 2; the report lists every selected test as in error |

### report

Kind: type

```xml
<testsuites name="end-to-end" tests="2" failures="1" errors="0" skipped="1" time="71.4">
  <testsuite name="alert" tests="2" failures="1" errors="0" skipped="1"
             time="71.4" timestamp="2026-10-06T09:15:02Z">
    <properties>
      <property name="configuration" value="real"/>
      <property name="sensor-id" value="00a1b2c3d4e5f607"/>
      <property name="protocol-version" value="1.0"/>
    </properties>
    <testcase name="ALERT-01 A plant that falls below a threshold gets one alert within 1 minute"
              classname="alert.real" time="0">
      <skipped message="needs scenario-control"/>
    </testcase>
    <testcase name="ALERT-04 A plant whose thresholds no reading can cross has no alert"
              classname="alert.real" time="71.4">
      <failure type="promise"
               message="expected: no alert for the plant; observed: 1 open alert, reason soil moisture below"/>
    </testcase>
  </testsuite>
</testsuites>
```

The example is shortened: a real report contains every test of the group and all properties. The file is JUnit XML in UTF-8, one per run.

| Element | Occurs | Meaning |
|---|---|---|
| `testsuites` | once, the root | the run |
| `testsuite` | once per group of the catalogue that was selected | the group: `link`, `relay` or `alert` |
| `properties` | once per `testsuite` | the conditions of the run, see below |
| `testcase` | once per test of the group | one test of the catalogue |
| `skipped` | inside a `testcase` that did not run | the test cannot run in this configuration |
| `failure` | inside a `testcase` | the test ran and a promise did not hold |
| `error` | inside a `testcase` | the test could not be carried out |
| `system-out` | inside a `testcase`, optional | what the rig did and saw at the public interfaces, at most 64 kB |

A `testcase` without `skipped`, `failure` or `error` has passed. A deviation of the device under test from the BLE profile that prevents a test from being carried out is a failure of that test, not an error.

| Element | Attribute | Content |
|---|---|---|
| `testsuites` | `name` | `end-to-end` |
| `testsuites`, `testsuite` | `tests`, `failures`, `errors`, `skipped` | counts |
| `testsuites`, `testsuite` | `time` | duration in seconds |
| `testsuite` | `name` | the group |
| `testsuite` | `timestamp` | start of the group, UTC, RFC 3339 with `Z` |
| `testcase` | `name` | the id of the test, a space, and its promise as the heading of the catalogue words it |
| `testcase` | `classname` | group and configuration, joined by a dot, for example `alert.simulated` |
| `testcase` | `time` | duration in seconds, 0 for a skipped test |
| `skipped` | `message` | the reason, for example `needs scenario-control` |
| `failure` | `message` | `expected`, then what the catalogue expects; `observed`, then what the rig saw |
| `failure` | `type` | `promise` |
| `error` | `message` | the cause |
| `error` | `type` | `environment`, `depends on` or `rig` |

| Property | Content |
|---|---|
| `configuration` | `simulated` or `real` |
| `sensor-id` | sensor id of the device under test |
| `protocol-version` | the version of the radio protocol the device states |
| `ble-profile-version` | the version of the BLE profile the rig implements |
| `reading-schema-version` | the version of the reading schema the rig uploads |
| `api-host` | host name of the public API under test, without path or token |
| `rig-version` | version of the rig |

| Result | Means | Example |
|---|---|---|
| failure | something under test broke a promise | a reading appears twice in the history |
| error, `environment` | a precondition outside the rig was not met | device not found, API not reachable, no reading in time |
| error, `depends on` | the test continues a test that did not pass | ALERT-02 after a failed ALERT-01 |
| error, `rig` | the rig itself failed | an unexpected internal fault |

### exit-status

Kind: type

```text
exit status: 0 | 1 | 2
```

| Status | Meaning |
|---|---|
| 0 | no failure, no error, and at least one test passed |
| 1 | at least one failure or error, or no test passed |
| 2 | the settings are incomplete; no test was attempted; the report contains every selected test as in error |

## Fake

Replays the examples: the report file above and its exit status, for the tools of a CI system that read the report. Faults it can inject: none.
