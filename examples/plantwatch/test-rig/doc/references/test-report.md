# Contract of `test-report`

The file a run of the rig produces, and the exit status that goes with it.
Readers are developers and the tools of a CI system that understand JUnit
XML. The tests are listed in the [test catalogue](test-catalogue.md), the
configurations in [configurations.md](configurations.md).

## The file

| Property | Value |
|---|---|
| Format | JUnit XML, UTF-8 |
| Number | One file per run |
| Location | The report path of the settings |
| Written | Always, also when the run could not start or was cut off by its time limit |

## Elements

| Element | Occurs | Meaning |
|---|---|---|
| `testsuites` | Once, the root | The run |
| `testsuite` | Once per group of the catalogue that was selected | The group: `link`, `relay` or `alert` |
| `properties` | Once per `testsuite` | The conditions of the run, see below |
| `testcase` | Once per test of the group | One test of the catalogue |
| `skipped` | Inside a `testcase` that did not run | The test cannot run in this configuration |
| `failure` | Inside a `testcase` | The test ran and a promise did not hold |
| `error` | Inside a `testcase` | The test could not be carried out |
| `system-out` | Inside a `testcase`, optional | What the rig did and saw at the public interfaces, at most 64 kB |

A `testcase` without `skipped`, `failure` or `error` has passed.

## Attributes

| Element | Attribute | Content |
|---|---|---|
| `testsuites` | `name` | `end-to-end` |
| `testsuites`, `testsuite` | `tests`, `failures`, `errors`, `skipped` | Counts |
| `testsuites`, `testsuite` | `time` | Duration in seconds |
| `testsuite` | `name` | The group |
| `testsuite` | `timestamp` | Start of the group, UTC, RFC 3339 with `Z` |
| `testcase` | `name` | The id of the test, a space, and its promise as the catalogue words it |
| `testcase` | `classname` | Group and configuration, joined by a dot, for example `alert.simulated` |
| `testcase` | `time` | Duration in seconds, 0 for a skipped test |
| `skipped` | `message` | The reason, for example `needs scenario-control` |
| `failure` | `message` | `expected`, then what the catalogue expects; `observed`, then what the rig saw |
| `failure` | `type` | `promise` |
| `error` | `message` | The cause |
| `error` | `type` | `environment`, `depends on` or `rig` |

## Properties

| Name | Content |
|---|---|
| `configuration` | `simulated` or `real` |
| `sensor-id` | Sensor id of the device under test |
| `protocol-version` | The version of the radio protocol the device states |
| `link-profile-version` | The version of `link-profile` the rig implements |
| `api-host` | Host name of the public API under test, without path or token |
| `rig-version` | Version of the rig |

## Failure and error

| Result | Means | Example |
|---|---|---|
| Failure | Something under test broke a promise | A reading appears twice in the history |
| Error, `environment` | A precondition outside the rig was not met | Device not found, API not reachable, no reading in time |
| Error, `depends on` | The test continues a test that did not pass | ALERT-02 after a failed ALERT-01 |
| Error, `rig` | The rig itself failed | An unexpected internal fault |

A deviation of the device under test from `link-profile` that prevents a
test from being carried out is a failure of that test, not an error.

## Example

```xml
<testsuites name="end-to-end" tests="2" failures="1" errors="0" skipped="1" time="71.4">
  <testsuite name="alert" tests="2" failures="1" errors="0" skipped="1"
             time="71.4" timestamp="2026-10-06T09:15:02Z">
    <properties>
      <property name="configuration" value="real"/>
      <property name="sensor-id" value="00a1b2c3d4e5f607"/>
      <property name="protocol-version" value="1.0"/>
    </properties>
    <testcase name="ALERT-01 A plant that falls below a threshold gets one alert, soon"
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

The example is shortened: a real report contains every test of the group
and all properties.

## Exit status

| Status | Meaning |
|---|---|
| 0 | No failure, no error, and at least one test passed |
| 1 | At least one failure or error, or no test passed |
| 2 | The settings are incomplete; no test was attempted. The report contains every selected test as in error. |

Skipped tests do not change the exit status.

## Stability

- The id at the start of a `testcase` name never changes and is never
  reused. Tools that track a test over time match on the id.
- New properties and new tests may be added at any time. Readers ignore
  what they do not know.
- No token, no owner's data other than the rig's own test plants, and
  no value of a setting other than those listed under "Properties" appears
  in the file.
