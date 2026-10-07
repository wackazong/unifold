# Context of ingest

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From cloud

| Source | What it says | What it means here |
|---|---|---|
| [cloud/0001 Services learn about readings through events, not calls](../../../doc/decisions/0001-services-learn-about-readings-through-events.md) | The service that accepts readings publishes one event per accepted reading on a durable bus and knows no receiver. | `ingest` is that service. It calls nobody and has no list of subscribers. |
| [cloud/0004 Every event consumer is idempotent](../../../doc/decisions/0004-every-event-consumer-is-idempotent.md) | Delivery is at least once. An event has an `id` derived from its content; consumers tolerate repeats. | `ingest` may publish an event again after a failure, with the same `id`. Its own recognition of duplicates need not be perfect. |
| [cloud: public API, uploads](../../../doc/references/public-api/uploads.md) | `POST /v1/sensors/{sensor_id}/batches` takes `{"readings": [...]}` and answers `200` with one result per reading: `new`, `duplicate`, or `rejected` with `malformed_reading`, `value_out_of_range`, `time_in_future` (more than 24 hours ahead) or `too_old` (more than 90 days). Unknown fields of a reading are kept. | The contract of `ingest-api`. `ingest` serves this operation exactly as defined. |
| [cloud: public API, general rules](../../../doc/references/public-api/index.md) | Error bodies have `code` and `message`; the codes include `invalid_request` (400), `payload_too_large` (413) and `unavailable` (503). A batch has at most 500 readings and 1 MB. | The errors and limits of `ingest-api`. |
| [cloud: events between services](../../../doc/references/events.md) | An event is a JSON object with `id`, `type`, `source`, `time`, `key` and `data`. A topic is named `<service>.<stream>.v<major>`. A publisher answers a request only after the bus has stored the event. | The envelope of `reading.accepted` and the names of the topics of `ingest`. |
| [cloud: calls between services](../../../doc/references/service-calls.md) | A service that serves an operation of the public API requires the header `X-Owner-Id` and does not verify tokens. Every service answers `GET /healthz` and listens on port 8080. | `ingest` requires the header, writes it to its log and makes no other use of it. |

## From plantwatch

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0002 Define the profile and the reading format once](../../../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md) | The format of a reading is defined in a unit of its own, with a version. A change within a major version keeps older counterparts working. | `ingest` does not define the format. It states the need `reading-format` and accepts readings with fields it does not know. |
| [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | A reading is identified by sensor id and sequence number and never changes. A receiver accepts a reading it already has and reports success. | The rule by which `ingest` recognises a duplicate, and the reason it reports `duplicate` as success. |
| [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | A reading arrives with a UTC time; a time that was estimated is flagged. | `ingest` checks the time against its own clock and passes the flag on in the event. |
| [plantwatch: measured quantities](../../../../doc/references/conventions.md) | Soil moisture 0 to 100 percent, light 0 to 100 000 lux, temperature -20 to 60 degrees Celsius. A value outside its range is invalid. A quantity that was not measured is absent, not zero. | The range checks of `ingest`, and the rule that an absent quantity is absent in the event. |
| [plantwatch: identifiers](../../../../doc/references/conventions.md) | A sensor id is 16 lower-case hex digits; a sequence number is an unsigned 32-bit integer. | The checks on the path and on each reading; the parts of an event `id`. |
| [plantwatch: time](../../../../doc/references/conventions.md) | A time is an RFC 3339 string in UTC with suffix `Z` and whole seconds. | The form of every time in an event. |
| [plantwatch: readings kept on a sensor stick](../../../../doc/references/product-parameters.md) | At least 2 880 readings. | A sensor stick that was out of reach for a month arrives as six or more full batches in a row. |
| [plantwatch: reading, batch](../../../../doc/references/glossary.md) | A reading is one set of measurements of one sensor stick taken at the same moment. A batch is a group of readings of one sensor stick that is transferred together. | One event per reading, never per value. One request per batch. |
