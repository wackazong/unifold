# Context of sync

What this unit takes over from the units above, and what each item means here.

## From mobile

### [mobile/0001 The local store is the only source for the screens](../../../docs/decisions/0001-the-local-store-is-the-only-source-for-the-screens.md)

Screens read only from a store on the phone. Fetched readings and server data flow into it; the owner's changes go there first, then to the server.

`sync` owns this store. Every query of `plant-data` answers from it, and every command writes to it before anything is sent.

### [mobile/0002 Fetch in the background when the system reports a paired sensor stick](../../../docs/decisions/0002-fetch-when-the-system-reports-a-paired-sensor-stick.md)

A background slot can be as short as about 10 seconds. A slot fetches, stores and confirms; uploading follows if run time is left, and otherwise later.

Storing a batch comes first and is fast. An upload may be cut off at any moment and is repeatable ([exchange.md](../references/exchange.md)).

### [mobile/0003 A reading gets its UTC time before it is stored](../../../docs/decisions/0003-a-reading-gets-its-time-before-it-is-stored.md)

A reading arrives with a UTC time and an estimated flag, and both never change. The tick count stays in it; nothing behind the fetch computes with it.

`sync` stores, uploads and returns time, flag and tick count as received. Of a reading that arrives twice, `sync` keeps the one stored first.

### [mobile: data model](../../../docs/references/data-model.md)

The data model defines the following, as far as `sync` implements it:

- A reading has a sensor id, a sequence number, a tick count, the three quantities, a UTC time and an estimated flag. Nobody changes it on the phone.
- A plant has an id chosen on the phone, a name of 1 to 60 characters, a lower and an upper limit per quantity, at most one sensor stick, and a change state `in step`, `waiting` or `refused`.
- An alert comes from the server only. The app does not compare readings with thresholds.
- In a session, the phone acts for one owner, known by a token. The server creates the owner at the first exchange; a further phone joins with a token from the first. The phone leaves an active session only after the server has confirmed every reading on it; leaving a lost session removes unconfirmed readings too.
- There are two ages: the time since the newest reading of a plant, and the time since the last exchange that succeeded.

The store holds these things, and `plant-data` returns them under these names. `sync` computes no alert, and "leave" in an active session waits for the upload.

### [mobile: glossary](../../../docs/references/glossary.md)

An exchange is one round with the server: the phone sends what waits on it, then takes plants, alerts and history. The store is what the app keeps.

`sync` runs every exchange and owns the store. Its own terms are in its [glossary](../references/glossary.md).

## From plantwatch

### [plantwatch: reading schema](../../../../docs/references/reading-schema.md)

A reading has a sensor id, a sequence number, a tick count, a time with a flag for an estimate, and soil moisture, light and temperature, each optional. Sensor id and sequence number identify it. It has a JSON form and a binary form, version 1.0; a minor version only adds optional fields.

The local store and the upload use the field names of the JSON form, major version 1 and no other.

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

Sensor id and sequence number identify a reading; it never changes. A receiver accepts a reading it already has. The store therefore keeps one reading per pair, and uploads may repeat.

### [plantwatch: conventions, delivery](../../../../docs/references/conventions.md#delivery)

A receiver accepts an item it already has and reports success. A sender deletes an item only after the receiver has confirmed it.

`sync` acknowledges a batch it has seen before. It removes a reading only after the server has confirmed it, or when the phone leaves a lost session ([0006](../../../docs/decisions/0006-leave-a-lost-session-without-uploading.md)).

### [plantwatch: conventions, HTTP ports](../../../../docs/references/conventions.md#http-ports)

Bodies are JSON, and an error has `code` and `message`. A request that repeats an earlier successful request succeeds again. This is what `sync` expects of `cloud-api` beyond its operations.

### [plantwatch: conventions, measured quantities](../../../../docs/references/conventions.md#measured-quantities)

Soil moisture ranges from 0 to 100 percent, light from 0 to 100 000 lux, and temperature from -20 to 60 °C. A command with a limit outside the range of its quantity fails.

### [plantwatch: product parameters](../../../../docs/references/product-parameters.md)

The phone keeps 90 days of history, and the limits are up to 50 plants per owner and 20 sensor sticks per phone. The sampling interval ranges from 5 to 60 minutes.

These parameters set the retention and size of the store, which holds at most 20 × 90 days × 288 readings a day ([local-store.md](../references/local-store.md)).

### [plantwatch: glossary](../../../../docs/references/glossary.md)

A batch is a group of readings of one sensor stick that is transferred together. An upload request carries one batch in this sense.
