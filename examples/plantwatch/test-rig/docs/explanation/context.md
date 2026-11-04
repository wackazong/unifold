# Context of test-rig

What this unit takes over from the units above, and what each item means here.

## From plantwatch

### [plantwatch/0008 Define the BLE profile and the reading format as references of plantwatch](../../../docs/decisions/0008-define-the-profile-and-the-reading-format-as-references-of-plantwatch.md)

The BLE profile and the reading schema are references of plantwatch. Every connection that carries the profile names it as its contract; a reading travels inside the profile and the public API, and whoever reads or writes readings cites the schema. Both keep a version; a change within a major version keeps older counterparts working.

`device-under-test` and `cloud-api` name the profile and the API as their contracts. The rig builds its central from the profile and its uploads from the schema, cited below, and from nothing else.

### [plantwatch: reading schema](../../../docs/references/reading-schema.md)

A reading has a sensor id, a sequence number, a tick count, a time with a flag for an estimate, and soil moisture, light and temperature, each optional. Sensor id and sequence number identify it. It has a JSON form and a binary form, version 1.0; a minor version only adds optional fields.

The rig builds the readings it uploads in the JSON form and compares the readings it fetched with what the API returns.

### [plantwatch: test report](../../../docs/references/test-report.md)

The project provides the result of the automated end-to-end tests as a JUnit XML file. A run goes against a real or a simulated sensor stick. The rig's capability `test-report` is this result.

### [plantwatch: app UI](../../../docs/references/app-ui.md)

Per plant, the app shows the latest reading and 90 days of history, and it shows plants with an open alert first, with the reason. The app works offline, and a tap on a notification opens the plant it is about.

The [test catalogue](../references/test-catalogue.md) tests this promise as far as the public API shows it. The catalogue says which parts of it the rig can observe and which it cannot.

### [plantwatch/0001 The phone relays between sensor stick and server](../../../docs/decisions/0001-the-phone-relays-between-sensor-and-server.md)

A sensor stick talks only to a phone, which carries the readings to the server. To test the whole path, the rig takes the place of the phone: it fetches over BLE and uploads ([0003](../decisions/0003-the-rig-is-its-own-central.md)).

### [plantwatch/0003 The emulator implements the profile independently of the firmware](../../../docs/decisions/0003-the-emulator-implements-the-profile-independently.md)

The simulated sensor stick is written from the profile alone. A difference in behaviour shows a gap in the profile or a fault in one of them.

One catalogue runs in the configurations `real` and `simulated`, and every result states which ([0001](../decisions/0001-one-catalogue-for-real-and-simulated-devices.md)).

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

Sensor id and sequence number identify a reading; it never changes. Every hop may deliver it more than once; every receiver recognises it.

Some tests therefore fetch twice and upload twice, and the rig compares a fetched reading with the history by this pair.

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../docs/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

A reading carries a boot counter and seconds since that boot, and the central converts to UTC. A time the central cannot compute is estimated and marked.

As the central, the rig converts. LINK-07 and RELAY-05 test restarts and the estimated flag.

### [plantwatch: conventions, measured quantities](../../../docs/references/conventions.md#measured-quantities)

Soil moisture ranges from 0 to 100 percent, light from 0 to 100 000 lux, and temperature from -20 to 60 °C. The first receiver rejects a value outside its range.

These ranges determine what "a valid value" means in a test, and the limits the rig sets so that every reading, or no reading, crosses a threshold.

### [plantwatch: conventions, delivery](../../../docs/references/conventions.md#delivery)

A transfer may deliver an item more than once; the receiver accepts it and reports success. A sender deletes only after confirmation. The promises of the groups `link` and `relay` follow from this convention.

### [plantwatch: product parameters](../../../docs/references/product-parameters.md)

The sampling interval is 5 to 60 minutes, with a default of 15. A sensor stick keeps at least 2 880 readings, the time from upload to notification is under 1 minute, and the protocol is version 1.

The catalogue takes its expected values from these parameters, and [configurations.md](../references/configurations.md) takes its waiting times from them.

### [plantwatch: glossary](../../../docs/references/glossary.md)

A scenario is a scripted course of sensor values over simulated time. An alert opens once and closes, and a notification is one message per alert.

The rig observes alerts, so "one notification" is tested as "one alert whose notification was handed on". The rig's own terms are in its [glossary](../references/glossary.md).
