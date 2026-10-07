# Test catalogue

The end-to-end promises the rig tests. Each test has an id that is never
reused and stays when the wording changes, the promise it verifies, a
stimulus, the expected observation, and the configurations it runs in:
`real`, `simulated` or both ([configurations.md](configurations.md)). The
numbers come from the items cited in [context.md](../context.md); the terms
are in the [glossary](glossary.md).

## The product promise behind the tests

The catalogue is named as what verifies the product's `app-ui`
([context.md](../context.md)). The rig observes the public API, not a
phone, so it verifies that promise as far as it shows there.

| Part of the promise | Verified by | Observed as |
|---|---|---|
| The latest reading and the history of each plant | LINK-01 to LINK-07, RELAY-01 to RELAY-05 | Every reading a device took is in the history once, with its values, time and flag |
| Whether a plant needs water or a warmer place | ALERT-01 to ALERT-04 | An open alert with quantity and limit, or none |
| One notification, not a series | ALERT-01, ALERT-03 | One open alert whose notification is reported as handed on, and no second alert |
| Whether a plant needs more light | Not verified | See "What the catalogue does not cover" |
| What a screen shows, and that it works offline | Not verified | Nothing on a phone is observed |

## Group `link`: the device under test alone

### LINK-01 A device states who it is

- Runs in: `real`, `simulated`
- Stimulus: connect and read the identity.
- Expect: a sensor id of 16 lower-case hex digits, protocol major version
  1, a sampling interval of 5 to 60 minutes, room for at least 2 880
  readings.

### LINK-02 Stored readings are served in order

- Runs in: `real`, `simulated`
- Stimulus: wait until the device holds at least 2 readings; fetch without
  confirming.
- Expect: sequence numbers strictly ascending; every value inside its range
  or absent; tick counts not descending within a boot.

### LINK-03 A confirmed reading is not served again, an unconfirmed one is

- Runs in: `real`, `simulated`
- Stimulus: fetch; confirm up to the second-newest reading; disconnect;
  fetch again.
- Expect: the second fetch starts with the newest reading of the first
  fetch and contains nothing older.

### LINK-04 An interrupted fetch loses nothing

- Runs in: `real`, `simulated`
- Stimulus: start a fetch; cut the connection after the first reading;
  fetch again.
- Expect: the second fetch contains every reading of the first attempt,
  with the same values and tick counts.

### LINK-05 A device keeps 30 days of readings

- Runs in: `simulated`
- Stimulus: scenario with constant values at the default sampling interval;
  advance by 2 879 sampling intervals; fetch.
- Expect: 2 880 readings, beginning with the first reading the device took;
  sequence numbers strictly ascending; tick counts 900 seconds apart.

### LINK-06 A full device overwrites the oldest reading

- Runs in: `simulated`
- Stimulus: continue LINK-05 without confirming; advance 1 more day; fetch.
- Expect: at least as many readings as the device says it keeps, ending at
  the newest; tick counts 900 seconds apart; the oldest tick count is later
  than that of the first reading of LINK-05.

### LINK-07 A restart loses no reading and reuses no sequence number

- Runs in: `simulated`
- Stimulus: scenario with a restart after 4 readings and 4 more readings
  after it; fetch.
- Expect: 8 readings; sequence numbers ascending across the restart; the
  boot counter of the last 4 is higher than that of the first 4.

## Group `relay`: from the device to the history

### RELAY-01 A fetched reading arrives in the history, once

- Runs in: `real`, `simulated`
- Stimulus: fetch, upload, confirm; ask for the history of the plant.
- Expect: every uploaded reading appears exactly once within 10 seconds,
  found by sensor id and sequence number, with the values and time the rig
  uploaded.

### RELAY-02 Values and intervals survive the whole path

- Runs in: `simulated`
- Stimulus: scenario that states a value of all three quantities for every
  sampling moment of 2 hours; advance 2 hours; fetch, upload; ask for the
  history.
- Expect: 9 readings with exactly the stated values; times of neighbouring
  readings 900 seconds apart, within 1 second.

### RELAY-03 A batch that is uploaded twice is stored once

- Runs in: `real`, `simulated`
- Stimulus: upload the batch of RELAY-01 again.
- Expect: the API reports every reading as known already; the history is
  unchanged.

### RELAY-04 An invalid reading is refused

- Runs in: `real`, `simulated`
- Stimulus: upload one reading with a soil moisture of 120 percent and an
  unused sequence number.
- Expect: the API reports this reading as refused, with a code and a
  message; 10 seconds later the reading is not in the history.

### RELAY-05 An estimated time keeps its flag

- Runs in: `simulated`
- Stimulus: scenario as in LINK-07; fetch only after the restart, so that
  the rig has to estimate the times of the first 4 readings; upload; ask
  for the history.
- Expect: the first 4 readings carry the flag, the last 4 do not.

## Group `alert`: from the history to the alert

### ALERT-01 A plant that falls below a threshold gets one alert within 1 minute

- Runs in: `simulated`
- Stimulus: plant with a lower limit of 30 percent for soil moisture;
  scenario with 40 percent at minutes 0 to 45, 20 percent at minutes 60 to
  180, 60 percent at minutes 195 to 240 and 20 percent from minute 255;
  fetch and upload at minutes 45, 120 and 180.
- Expect: no alert 60 seconds after the first upload. Within 60 seconds
  after the second: one open alert for the plant, soil moisture below the
  limit, its notification reported as handed on. After the third: the same
  alert and no other.

### ALERT-02 Recovery closes the alert, and a new fall opens a new one

- Runs in: `simulated`
- Stimulus: continue ALERT-01; fetch and upload at minutes 240 and 300.
- Expect: within 60 seconds after the first upload the alert is closed.
  Within 60 seconds after the second: one open alert with a new id. In
  total 2 alerts for the plant.

### ALERT-03 A plant whose threshold every reading crosses has one alert

- Runs in: `real`, `simulated`
- Stimulus: fresh plant with a lower limit of 60 °C for temperature and no
  other limit; upload fetched readings twice, at least one new reading each
  time.
- Expect: within 60 seconds after the first upload, one open alert,
  temperature below the limit, its notification reported as handed on.
  After the second: the same alert, still open, and no other.

### ALERT-04 A plant whose thresholds no reading can cross has no alert

- Runs in: `real`, `simulated`
- Stimulus: fresh plant with all three lower limits at the lower end of
  their ranges; upload at least one new reading.
- Expect: no alert for the plant, open or closed, 60 seconds after the
  upload.

## Order and dependencies

- The groups run in the order `link`, `relay`, `alert`; within a group the
  tests run in the order of their ids. What the rig sets up before a group
  and for a "fresh plant" is in [configurations.md](configurations.md).
- A test that says "continue" or "as in" depends on the named test. If that
  test did not pass, the dependent test ends in error with the reason
  "depends on" and the id.
- In `real`, the tests of the group `link` leave at least one unconfirmed
  reading on the device, so that RELAY-01 starts without waiting.

## What the catalogue does not cover

| Not covered | Why |
|---|---|
| Anything on a phone: screens, offline use, the arrival of a notification | The rig observes the public API, not a phone |
| Courses of values in `real` | Without `scenario-control` the rig cannot set values or move time |
| Limits for soil moisture in `real` | ALERT-03 uses temperature because a real reading is below 60 °C with certainty |
| Alerts about light | They depend on the light of a whole day; left out of version 1 of the catalogue |
| Upper limits | Version 1 of the catalogue tests lower limits |
| More than 31 simulated days, more than one device under test | Run time; one BLE adapter |
