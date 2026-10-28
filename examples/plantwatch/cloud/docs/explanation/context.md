# Context of cloud

What this unit inherits from the units above. This is the only file of the unit that links upward. Each item is restated so that the unit can be understood when the link is not available.

## From plantwatch

### [plantwatch/0008 Define the BLE profile and the reading format as references of plantwatch](../../../docs/decisions/0008-define-the-profile-and-the-reading-format-as-references-of-plantwatch.md)
<!-- unifold:cites sha=eb9de36f -->

Says: the BLE profile and the reading schema are references of plantwatch. Every connection that carries the profile names it as its contract; a reading travels inside the profile and the public API, and whoever reads or writes readings cites the schema. Both keep a version; a change within a major version keeps older counterparts working.

Here: `public-api` names the API as its contract; a reading inside an upload has the form of the schema, cited below. `cloud` keeps fields it does not know.

### [plantwatch: reading schema](../../../docs/references/reading-schema.md)
<!-- unifold:cites sha=047250bf -->

Says: a reading has a sensor id, a sequence number, a tick count, a time with a flag for an estimate, and soil moisture, light and temperature, each optional. Sensor id and sequence number identify it. It has a JSON form and a binary form, version 1.0; a minor version only adds optional fields.

Here: uploads and histories carry readings in the JSON form, major version 1. Fields the server does not know are kept.

### [plantwatch/0001 The phone relays between sensor stick and server](../../../docs/decisions/0001-the-phone-relays-between-sensor-and-server.md)
<!-- unifold:cites sha=3ad88d69 -->

Says: readings reach the server only when a phone was near the sensor stick and is online. The sensor stick holds no secrets.

Here: readings arrive late and in batches. `cloud` judges them by the time they carry, keeps the upload path free of other dependencies, and cannot check that an upload comes from the owner of the sensor stick.

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)
<!-- unifold:cites sha=cdc44cc5 -->

Says: every hop delivers at least once. Sensor id and sequence number identify a reading; it never changes, and a receiver accepts one it has.

Here: an upload reports a duplicate as success and no operation changes a reading. The same rule holds between the services, see [0004](../decisions/0004-every-event-consumer-is-idempotent.md).

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../docs/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)
<!-- unifold:cites sha=ad1b9b71 -->

Says: the phone computes the UTC time of each reading. A time that could only be estimated is flagged.

Here: `cloud` trusts the time a reading carries and keeps the flag. A reading with an estimated time enters history and changes no alert.

### [plantwatch/0006 The server side alone decides whether a plant needs attention](../../../docs/decisions/0006-the-server-side-alone-decides-what-needs-attention.md)
<!-- unifold:cites sha=1298b1e1 -->

Says: the server side judges every reading. Every other part shows or carries what the server side decided.

Here: `cloud` is that server side. An alert exists when `public-api` returns it, and a threshold takes effect once it has reached `cloud`.

### [plantwatch: conventions, measured quantities](../../../docs/references/conventions.md#measured-quantities)
<!-- unifold:cites sha=c9226f2c -->

Says: soil moisture 0 to 100 percent, light 0 to 100 000 lux, temperature -20 to 60 °C. A value out of range is invalid; an unmeasured one is absent.

Here: `cloud` rejects a reading with a value out of range. Thresholds and aggregates use the same quantities and units, named `soil_moisture`, `light` and `temperature`.

### [plantwatch: conventions, identifiers and time](../../../docs/references/conventions.md)
<!-- unifold:cites sha=27c608e6 -->

Says: a sensor id is 16 lower-case hex digits; plant, owner and alert have a lower-case UUID. A time is UTC, RFC 3339 with `Z` and whole seconds.

Here: the public API, the events and the stored data use these forms and reject others.

### [plantwatch: conventions, delivery and HTTP ports](../../../docs/references/conventions.md)
<!-- unifold:cites sha=27c608e6 -->

Says: a transfer may deliver an item twice, and the receiver reports success. HTTP bodies are JSON; an error has the fields `code` and `message`.

Here: holds for the public API, for the calls between services and for the events between them.

### [plantwatch: product parameters](../../../docs/references/product-parameters.md)
<!-- unifold:cites sha=b11fccd4 -->

Says: upload to notification takes under 1 minute. History is kept 2 years on the server and 90 days on the phone. An owner has up to 50 plants.

Here: readings are evaluated as they arrive. History and closed alerts are kept for 2 years. A reading older than 90 days is rejected, and raw readings are kept that long. 50 plants per owner is a limit of the public API.

### [plantwatch: glossary](../../../docs/references/glossary.md)
<!-- unifold:cites sha=082ae761 -->

Says: a reading is one set of measurements of one sensor stick; a batch is a group of them. An alert is the state "this plant needs attention".

Here: `cloud` uses plant, owner, sensor stick, attached, reading, batch, threshold, alert and notification as defined there. The terms it adds are in its own [glossary](../references/glossary.md).
