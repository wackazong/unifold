# Test catalogue

The end-to-end promises the rig tests: what it does, what it expects to
observe, and in which configurations the test runs. The configurations and
waiting times are in [configurations.md](configurations.md). The numbers and
rules behind the expectations are cited in [context.md](../context.md).

An id is never reused. A test whose promise changes keeps its id.

## Group `link`: the device under test alone

| Id | Promise | Stimulus | Expected observation | Runs in |
|---|---|---|---|---|
| LINK-01 | A device states who it is | Connect and read identity | A sensor id of 16 lower-case hex digits, protocol major version 1, a sampling interval of 5 to 60 minutes, room for at least 2 880 readings | `simulated`, `real` |
| LINK-02 | Stored readings are served in order | Wait until the device holds at least 2 readings; fetch without confirming | Sequence numbers strictly ascending; every value inside its range or absent; tick counts not descending within a boot | `simulated`, `real` |
| LINK-03 | A confirmed reading is not served again, an unconfirmed one is | Fetch; confirm up to the second-newest reading; disconnect; fetch again | The second fetch starts with the newest reading of the first fetch and contains nothing older | `simulated`, `real` |
| LINK-04 | An interrupted fetch loses nothing | Start a fetch; cut the connection after the first reading; fetch again | The second fetch contains every reading of the first attempt, with the same values and tick counts | `simulated`, `real` |
| LINK-05 | A device keeps 30 days of readings | Scenario with constant values at the default sampling interval; advance by 2 879 sampling intervals, just under 30 days; fetch | 2 880 readings, beginning with the first reading the device took; sequence numbers strictly ascending, tick counts one sampling interval apart | `simulated` |
| LINK-06 | A full device overwrites the oldest reading | Continue LINK-05 without confirming; advance 1 more day; fetch | At least as many readings as the device says it keeps, without a gap in the tick counts, ending at the newest reading; the oldest tick count is later than that of the first reading of LINK-05 | `simulated` |
| LINK-07 | A restart loses no reading and reuses no sequence number | Scenario with a restart after 4 readings and 4 more readings after it; fetch | 8 readings; sequence numbers ascending across the restart; the boot counter of the last 4 is higher than that of the first 4 | `simulated` |

## Group `relay`: from the device to the history

| Id | Promise | Stimulus | Expected observation | Runs in |
|---|---|---|---|---|
| RELAY-01 | A fetched reading arrives in the history, once | Fetch, upload, confirm; ask for the history of the plant | Every uploaded reading appears exactly once, found by sensor id and sequence number, with the values and time the rig uploaded | `simulated`, `real` |
| RELAY-02 | Values and intervals survive the whole path | Scenario with a known course of all three quantities; advance 2 hours; fetch, upload; ask for the history | The values of the scenario, at the resolution of each quantity; times of neighbouring readings one sampling interval apart, within 1 second | `simulated` |
| RELAY-03 | A batch that is uploaded twice is stored once | Upload the batch of RELAY-01 again | The API reports every reading as known already; the history is unchanged | `simulated`, `real` |
| RELAY-04 | An invalid reading is refused | Upload one reading with a soil moisture of 120 percent and an unused sequence number | The API reports this reading as refused, with a code and a message; the reading is not in the history | `simulated`, `real` |
| RELAY-05 | An estimated time keeps its flag | Scenario as in LINK-07; fetch only after the restart, so that the rig has to estimate the times of the first 4 readings; upload; ask for the history | The first 4 readings carry the flag, the last 4 do not | `simulated` |

## Group `alert`: from the history to the alert

| Id | Promise | Stimulus | Expected observation | Runs in |
|---|---|---|---|---|
| ALERT-01 | A plant that falls below a threshold gets one alert, soon | Scenario in which soil moisture falls from above to below the plant's limit and stays there for 2 hours; fetch and upload after each simulated hour | Within 60 seconds after the first upload that contains a reading below the limit: one open alert for the plant with the reason "soil moisture below", and its notification reported as handed on. After the second upload: still exactly one alert. | `simulated` |
| ALERT-02 | Recovery closes the alert, and a new fall opens a new one | Continue ALERT-01: soil moisture rises to twice the limit, later falls below the limit again; upload after each change | After the rise: the alert is closed. After the second fall: one open alert with a new id. In total 2 alerts for the plant. | `simulated` |
| ALERT-03 | A plant whose threshold every reading crosses has exactly one alert | Fresh plant with a temperature limit of 60 °C and the other thresholds switched off; upload fetched readings twice, at least one new reading each time | After the first upload: one open alert with the reason "temperature below". After the second: the same alert, still open, no other. | `simulated`, `real` |
| ALERT-04 | A plant whose thresholds no reading can cross has no alert | Fresh plant with all three limits at the lower end of their ranges; upload at least one new reading | No alert for the plant, open or closed, 60 seconds after the upload | `simulated`, `real` |

## Order and dependencies

- The groups run in the order `link`, `relay`, `alert`. Within a group the
  tests run in the order of their ids.
- Before each group, and where a test says "fresh plant", the rig removes
  the plant of the previous tests and creates a new one bound to the device
  under test. In `simulated` it also loads a scenario before each group and
  before each test that names one; this puts the device into its initial
  state under a sensor id the run has not used yet.
- A test that says "continue" depends on the named test. If that test did
  not pass, the dependent test ends in error with the reason "depends on"
  and the id.
- In `real`, the tests of the group `link` leave at least one unconfirmed
  reading on the device, so that RELAY-01 starts without waiting.

## What the catalogue does not cover

| Not covered | Why |
|---|---|
| The message that tells the owner about an alert | The rig observes the public API, not a phone |
| Courses of values on real hardware | Without `scenario-control` the rig cannot set values or move time |
| Thresholds for light and for soil moisture on real hardware | ALERT-03 uses temperature because a real reading is below 60 °C with certainty |
| Alerts about light | They depend on the light of a whole day; left out of version 1 of the catalogue |
| Upper limits | Version 1 of the catalogue tests lower limits |
| Behaviour over more than 31 simulated days | Run time |
| More than one device under test at a time | One BLE adapter, one device |
