# Context of mobile

What this unit takes over from the units above, and what each item means here.

## From plantwatch

### [plantwatch/0008 Define the BLE profile and the reading format as references of plantwatch](../../../docs/decisions/0008-define-the-profile-and-the-reading-format-as-references-of-plantwatch.md)

The BLE profile and the reading schema are references of plantwatch. Every connection that carries the profile names it as its contract; a reading travels inside the profile and the public API, and whoever reads or writes readings cites the schema. Both keep a version; a change within a major version keeps older counterparts working.

`sensor-link` names the profile as its contract, and the app implements the central side of major version 1. The app stores and uploads readings in the form of the schema, cited below.

### [plantwatch: reading schema](../../../docs/references/reading-schema.md)

A reading has a sensor id, a sequence number, a tick count, a time with a flag for an estimate, and soil moisture, light and temperature, each optional. Sensor id and sequence number identify it. It has a JSON form and a binary form, version 1.0; a minor version only adds optional fields.

The app stores and uploads readings in the JSON form and gives a reading its `taken_at` from the tick count before it is stored.

### [plantwatch: app UI](../../../docs/references/app-ui.md)

Per plant, the app shows the latest reading and 90 days of history, and it shows plants with an open alert first, with the reason. The app works offline, and a tap on a notification opens the plant it is about.

The capability `app-ui` of this unit is that promise. The app shows and reacts to notifications; that there is only one per alert is not its doing.

### [plantwatch/0001 The phone relays between sensor stick and server](../../../docs/decisions/0001-the-phone-relays-between-sensor-and-server.md)

A sensor stick talks only to a phone. The phone app carries the readings to the server. The app is therefore the only way for a reading to leave a sensor stick, so it fetches in the background ([0002](../decisions/0002-fetch-when-the-system-reports-a-paired-sensor-stick.md)).

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

Sensor id and sequence number identify a reading; it never changes. Every hop may deliver it more than once; every receiver recognises it. The app stores a reading under this pair, keeps the copy it stored first, and repeats a transfer after any failure.

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../docs/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

A reading carries a tick count. The phone converts it to UTC when it fetches; a time it cannot compute is estimated and marked. The app assigns the time of every reading ([0003](../decisions/0003-a-reading-gets-its-time-before-it-is-stored.md)), and the phone's clock is the time source of all history.

### [plantwatch/0006 The server side alone decides whether a plant needs attention](../../../docs/decisions/0006-the-server-side-alone-decides-what-needs-attention.md)

Only the server side compares readings with thresholds. Every other part shows or carries what it decided. The app computes no alert. A fetched reading below a threshold shows in the history and becomes an alert only when the server says so.

### [plantwatch: conventions, measured quantities](../../../docs/references/conventions.md#measured-quantities)

Soil moisture ranges from 0 to 100 percent, light from 0 to 100 000 lux, and temperature from -20 to 60 °C. The first receiver rejects a value outside its range.

The app is the first receiver of a reading and refuses invalid ones at the radio. The [data model](../references/data-model.md) uses these units.

### [plantwatch: conventions, identifiers and time](../../../docs/references/conventions.md)

A sensor id has 16 lower-case hex digits, and a plant, an owner and an alert each have a UUID. Outside the sensor stick, a time is in UTC, written in RFC 3339 with `Z` and in whole seconds.

The [data model](../references/data-model.md) uses these forms. The app converts to local time only on the screens.

### [plantwatch: conventions, delivery](../../../docs/references/conventions.md#delivery)

A transfer may deliver an item more than once and the receiver reports success. A sender deletes an item only after the receiver confirmed. Both ends of the app therefore follow the order "store, then confirm, then delete" ([invariants](invariants.md)).

### [plantwatch: product parameters](../../../docs/references/product-parameters.md)

The limits are up to 20 sensor sticks per phone, 50 plants per owner and 90 days of history on the phone. A sensor stick keeps 2 880 readings, and the radio protocol is version 1.

These are the limits of `app-ui`. One fetch may bring 2 880 readings from one sensor stick. The app supports major version 1.

### [plantwatch: glossary](../../../docs/references/glossary.md)

An alert is the state "this plant needs attention for this reason". A notification is one message per alert, and a central connects to a sensor stick.

The app uses the project's terms unchanged and adds its own in its [glossary](../references/glossary.md). The phone is the central.
