# Context of test-rig

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## Decisions

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0001 The phone relays](../../doc/decisions/0001-the-phone-relays-between-sensor-and-server.md) | A sensor stick talks only to a central, normally a phone, which carries the readings to the server. | To test the whole path the rig takes the place of the phone: it fetches over BLE and uploads. See [0003](decisions/0003-the-rig-is-its-own-central.md). |
| [plantwatch/0002 Profile and reading format defined once](../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md) | The BLE profile and the reading format are defined in one place; every user states them as a need. Changes within a major version keep older counterparts working. | The rig has the need `link-profile` and builds its central from it alone. It uploads in the format the public API documents. |
| [plantwatch/0003 Two independent implementations of the profile](../../doc/decisions/0003-the-emulator-implements-the-profile-independently.md) | The simulated sensor stick is written from the profile alone and shares nothing with the real one. A difference in behaviour points to a gap in the profile or a fault in one of them. | The rig runs one catalogue against both and states the configuration in every result, so that such differences show. See [0001](decisions/0001-one-catalogue-for-real-and-simulated-devices.md). |
| [plantwatch/0004 Immutable readings](../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | A reading is identified by sensor id and sequence number and never changes. Every hop may deliver it more than once; every receiver recognises it. | The tests that fetch twice and upload twice, and the comparison of a fetched reading with the history by this pair. |
| [plantwatch/0005 Ticks and UTC](../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | A reading carries a boot counter and seconds since that boot. The central converts to UTC at the fetch. Times of earlier boots that cannot be computed are estimated and marked. | As the central, the rig converts. The tests for restarts and for the estimated flag. |

## References

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch: README, `test-report`](../../README.md) | The project provides the result of the automated end-to-end tests as a JUnit XML file. A run exercises the path from a sensor value to an alert and can run against a real or a simulated sensor stick. | The rig's port `test-report` is this result. |
| [Conventions: measured quantities](../../doc/references/conventions.md) | Soil moisture 0 to 100 percent, light 0 to 100 000 lux, temperature -20 to 60 °C. A value outside its range is rejected by the first receiver. | What "a valid value" means in a test, and the limits the rig uses for thresholds that every reading, or no reading, crosses. |
| [Conventions: delivery](../../doc/references/conventions.md) | Every transfer may deliver an item more than once; the receiver accepts it and reports success; a sender deletes only after confirmation. | The promises of the groups `link` and `relay` in the [catalogue](references/test-catalogue.md). |
| [Conventions: HTTP ports](../../doc/references/conventions.md) | Errors have a JSON body with `code` and `message`. A repeated successful request succeeds again. | What the rig checks when the public API refuses an invalid reading. |
| [Conventions: time](../../doc/references/conventions.md) | Every time outside the sensor stick is UTC in RFC 3339 form with `Z`. An estimated time carries a flag. | The form of times in the report and in comparisons with the history. |
| [Product parameters](../../doc/references/product-parameters.md) | Sampling interval 15 minutes by default. A sensor stick keeps at least 2 880 readings and overwrites the oldest when full. Under 1 minute from upload to notification. Radio protocol version 1. | The expected values in the catalogue and the waiting times in [configurations.md](references/configurations.md). |
| [Glossary](../../doc/references/glossary.md) | Scenario: a scripted course of sensor values over simulated time. Central: the side that connects to a sensor stick. Alert: opens once, stays open while the reason lasts, closes. Notification: one message per alert. Batch: readings of one sensor stick transferred together. | The rig is a central. It observes alerts; "one notification" is tested as "one alert". |
