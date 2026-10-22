# Context of ingest

What this unit inherits from the levels above. This is the only file of the unit that links upward. Each item is restated so that the unit can be understood when the link is not available.

## From cloud

### [cloud/0001 Services learn about readings through events, not calls](../../../../docs/decisions/0001-services-learn-about-readings-through-events.md)
<!-- unifold:cites sha=47d0b62c -->

Says: the service that accepts readings publishes one event per accepted reading on a durable bus and knows no receiver.

Here: `ingest` is that service. It calls nobody and has no list of subscribers.

### [cloud/0004 Every event consumer is idempotent](../../../../docs/decisions/0004-every-event-consumer-is-idempotent.md)
<!-- unifold:cites sha=02a8c4c1 -->

Says: delivery is at least once. An event has an `id` derived from what it describes, and consumers tolerate repeats.

Here: `ingest` may publish an event again after a failure, with the same `id`. Its own recognition of duplicates need not be perfect.

### [cloud: public API, uploads](../../../../../docs/references/public-api/uploads.md)
<!-- unifold:cites sha=cfd7e862 -->

Says, as the contract that this unit implements:

- `POST /v1/sensors/{sensor_id}/batches` takes `{"readings": [...]}`, each element one reading in the form that the reading schema defines.
- The answer is `200` with one result per reading, in the order of the request: `new`, `duplicate`, or `rejected` with a `code` and a `message`.
- The codes of a rejection are `malformed_reading`, `value_out_of_range`, `time_in_future` (more than 24 hours ahead of the server's clock) and `too_old` (more than 90 days in the past).
- `400` and `413` mean that no reading was looked at. An empty batch is valid. Fields of a reading that the server does not know are kept.
- A duplicate is recognised by sensor id and sequence number alone.

Here: the contract of `ingest-api`. `ingest` serves this operation exactly as defined; [ingest API](../../../../docs/references/ingest-api.md) adds the order of the checks and the failures.

### [cloud: public API, general rules](../../../../../docs/references/public-api/index.md)
<!-- unifold:cites sha=d259494b -->

Says: errors are `{"code", "message"}`: `invalid_request` (400), `payload_too_large` (413), `unavailable` (503). A batch: 500 readings, 1 MB.

Here: the errors and the limits of `ingest-api`.

### [cloud: events between services](../../../../docs/references/events.md)
<!-- unifold:cites sha=b3af8439 -->

Says, as the definition that this unit implements: an event is a JSON object with `id`, `type`, `source`, `time`, `key` and `data`, at most 16 kB long. A topic is named `<service>.<stream>.v<major>`. A publisher answers a request only after the bus has stored the event. The contract of an event capability states key, order and delivery.

Here: the envelope of `reading.accepted`, the names of the two topics of `ingest`, and the reason why an upload is answered last.

### [cloud: calls between services](../../../../docs/references/service-calls.md)
<!-- unifold:cites sha=7282b622 -->

Says: a service that serves a public operation requires `X-Owner-Id` and verifies no token. It answers `GET /healthz`. A caller waits 5 seconds.

Here: `ingest` requires the header, writes it to its log and makes no other use of it. It answers within 4 seconds, so that no caller gives up first.

## From plantwatch

### [plantwatch: reading schema](../../../../../docs/references/reading-schema.md)
<!-- unifold:cites sha=888e575a -->

Says: a reading has a sensor id, a sequence number, a tick count, a time with a flag for an estimate, and soil moisture, light and temperature, each optional. Sensor id and sequence number identify it. It has a JSON form and a binary form, version 1.0; a minor version only adds optional fields.

Here: every element of a batch is checked against the JSON form, major version 1; unknown fields pass through in `data.reading`.

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)
<!-- unifold:cites sha=cdc44cc5 -->

Says: sensor id and sequence number identify a reading, and it never changes. A receiver accepts a reading it already has and reports success.

Here: the rule by which `ingest` recognises a duplicate, and the reason it reports `duplicate` as success and never compares contents.

### [plantwatch: conventions, measured quantities](../../../../../docs/references/conventions.md#measured-quantities)
<!-- unifold:cites sha=c9226f2c -->

Says: soil moisture 0 to 100 percent, light 0 to 100 000 lux, temperature -20 to 60 °C. A value out of range is invalid; an unmeasured one is absent.

Here: the range checks of `ingest`, and the rule that a quantity that was not measured is absent in the event.

### [plantwatch: conventions, identifiers and time](../../../../../docs/references/conventions.md)
<!-- unifold:cites sha=27c608e6 -->

Says: a sensor id is 16 lower-case hex digits, a sequence number an unsigned 32-bit integer. A time is UTC, RFC 3339 with `Z` and whole seconds.

Here: the checks on the path and on each reading, the parts of an event `id`, and the form of every time in an event.

### [plantwatch: glossary](../../../../../docs/references/glossary.md)
<!-- unifold:cites sha=082ae761 -->

Says: a reading is one set of measurements of one sensor stick taken at the same moment. A batch is a group of readings of one sensor stick.

Here: one event per reading, never per value. One request per batch.
