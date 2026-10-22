# Context of sync

What this unit inherits from the levels above. This is the only file of the unit that links upward. Each item is restated so that the unit can be understood when the link is not available.

## From mobile

### [mobile/0001 The local store is the only source for the screens](../../../docs/decisions/0001-the-local-store-is-the-only-source-for-the-screens.md)
<!-- unifold:cites sha=3670810d -->

Says: screens read only from a store on the phone. Fetched readings and server data flow into it; the owner's changes go there first, then to the server.

Here: sync owns this store. Every query of `plant-data` answers from it, and every command writes to it before anything is sent.

### [mobile/0002 Fetch in the background when the system reports a paired sensor stick](../../../docs/decisions/0002-fetch-when-the-system-reports-a-paired-sensor-stick.md)
<!-- unifold:cites sha=4c2eb2bd -->

Says: a background slot can be as short as about 10 seconds. It does fetch, store, confirm; uploading follows if run time is left, otherwise later.

Here: storing a batch comes first and is fast. An upload may be cut off at any moment and is repeatable ([exchange.md](../references/exchange.md)).

### [mobile/0003 A reading gets its UTC time before it is stored](../../../docs/decisions/0003-a-reading-gets-its-time-before-it-is-stored.md)
<!-- unifold:cites sha=935abb64 -->

Says: a reading arrives with a UTC time and an estimated flag; both never change. The tick count stays in it; nothing behind the fetch computes with it.

Here: sync stores, uploads and returns time, flag and tick count as received. Of a reading that arrives twice it keeps the one stored first.

### [mobile: data model](../../../docs/references/data-model.md)
<!-- unifold:cites sha=87485fb7 -->

Says, as far as sync implements it:

- Reading: sensor id, sequence number, tick count, the three quantities, UTC time, estimated flag. Nobody changes it on the phone.
- Plant: id chosen on the phone, name of 1 to 60 characters, a lower and an upper limit per quantity, at most one sensor stick, and a change state `in step`, `waiting` or `refused`.
- Alert: comes from the server only. The app does not compare readings with thresholds.
- Session: the phone acts for one owner, known by a token. The server creates the owner at the first exchange; a further phone joins with a token from the first. The phone leaves only after the server has confirmed every reading on it.
- Two ages: time since the newest reading of a plant, and time since the last exchange that succeeded.

Here: the store holds these things and `plant-data` returns them under these names. sync computes no alert. "Leave" waits for the upload.

### [mobile: glossary](../../../docs/references/glossary.md)
<!-- unifold:cites sha=61301927 -->

Says: an exchange is one round with the server: the phone sends what waits on it, then takes plants, alerts and history. The store is what the app keeps.

Here: sync runs every exchange and owns the store. Its own terms are in its
[glossary](../references/glossary.md).

## From plantwatch

### [plantwatch: reading schema](../../../../docs/references/reading-schema.md)
<!-- unifold:cites sha=888e575a -->

Says: a reading has a sensor id, a sequence number, a tick count, a time with a flag for an estimate, and soil moisture, light and temperature, each optional. Sensor id and sequence number identify it. It has a JSON form and a binary form, version 1.0; a minor version only adds optional fields.

Here: the local store and the upload use the field names of the JSON form, major version 1 and no other.

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)
<!-- unifold:cites sha=cdc44cc5 -->

Says: sensor id and sequence number identify a reading; it never changes. A receiver accepts a reading it already has.

Here: the store keeps one reading per pair. Uploads may repeat.

### [plantwatch: conventions, delivery](../../../../docs/references/conventions.md#delivery)
<!-- unifold:cites sha=2fec0e46 -->

Says: a receiver accepts an item it already has and reports success. A sender deletes an item only after the receiver has confirmed it.

Here: sync acknowledges a batch it has seen before. It removes a reading only after the server has confirmed it.

### [plantwatch: conventions, HTTP ports](../../../../docs/references/conventions.md#http-ports)
<!-- unifold:cites sha=d68b7fc9 -->

Says: JSON bodies; an error has `code` and `message`; a request that repeats an earlier successful request succeeds again.

Here: what sync expects of `cloud-api` beyond its operations.

### [plantwatch: conventions, measured quantities](../../../../docs/references/conventions.md#measured-quantities)
<!-- unifold:cites sha=c9226f2c -->

Says: soil moisture 0 to 100 percent, light 0 to 100 000 lux, temperature -20 to 60 °C.

Here: a command with a limit outside the range of its quantity fails.

### [plantwatch: product parameters](../../../../docs/references/product-parameters.md)
<!-- unifold:cites sha=b11fccd4 -->

Says: 90 days of history on the phone, up to 50 plants per owner and 20 sensor sticks per phone, sampling interval from 5 to 60 minutes.

Here: retention and size of the store: at most 20 × 90 days × 288 readings a day
([local-store.md](../references/local-store.md)).

### [plantwatch: glossary](../../../../docs/references/glossary.md)
<!-- unifold:cites sha=082ae761 -->

Says: a batch is a group of readings of one sensor stick that is transferred together.

Here: an upload request carries one batch in this sense.
