# Context of cloud

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## Decisions

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0001 The phone relays between sensor stick and server](../../doc/decisions/0001-the-phone-relays-between-sensor-and-server.md) | Readings reach the server only when a phone has been near the sensor stick and has a network connection. The sensor stick holds no secrets. | Readings arrive late and in batches. `cloud` accepts old readings and judges them by the time they carry. An upload must succeed whenever a client is online. `cloud` cannot check that an upload comes from the owner of the sensor stick. |
| [plantwatch/0002 Define the profile and the reading format once](../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md) | The format of a reading is defined in a unit of its own and carries a version. A change within a major version keeps older counterparts working. | `cloud` does not define the fields of a reading. It states the need `reading-format`, accepts major version 1 and keeps fields it does not know. |
| [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | Every hop delivers at least once. A reading is identified by sensor id and sequence number and never changes. A receiver accepts a reading it already has. | An upload reports a duplicate as success. No operation changes a reading. The same rule holds between the services, see [0004](decisions/0004-every-event-consumer-is-idempotent.md). |
| [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | A reading arrives with a UTC time that the phone computed. Some times are estimated and flagged. | `cloud` trusts the time of a reading and keeps the flag. A reading with an estimated time enters history and does not change an alert. |

## Conventions

| Source | What it says | What it means here |
|---|---|---|
| [Measured quantities](../../doc/references/conventions.md) | Soil moisture 0 to 100 percent, light 0 to 100 000 lux, temperature -20 to 60 degrees Celsius. A value outside its range is invalid. A quantity that was not measured is absent. | `cloud` rejects a reading with a value out of range. Thresholds and aggregates use the same quantities and units, named `soil_moisture`, `light` and `temperature`. |
| [Identifiers](../../doc/references/conventions.md) | A sensor id is 16 lower-case hex digits, a sequence number an unsigned 32-bit integer; plant, owner and alert have a UUID in lower-case text form. | The public API and the events use these forms and reject others. |
| [Time](../../doc/references/conventions.md) | Every time is UTC, written as an RFC 3339 string with suffix `Z` and whole seconds. | All times in the public API, in events and in stored data have this form. |
| [Delivery](../../doc/references/conventions.md) | A transfer may deliver an item more than once; the receiver accepts it and reports success; the sender deletes only after confirmation. | Holds for uploads and for events between services. |
| [HTTP ports](../../doc/references/conventions.md) | Bodies are JSON in UTF-8, field names are lower-case with underscores, an error has `code` and `message`, a repeated request succeeds again. | The public API and the calls between services follow this. |

## Product parameters

| Source | What it says | What it means here |
|---|---|---|
| [Time from upload to notification](../../doc/references/product-parameters.md) | Under 1 minute. | Readings are evaluated as they arrive, not by a periodic job. |
| [History kept on the server](../../doc/references/product-parameters.md) | 2 years per plant. | Bounds storage; sets the retention of history and of closed alerts. |
| [History kept on the phone](../../doc/references/product-parameters.md) | 90 days per plant. | A client can hold a reading up to 90 days old. `cloud` rejects older ones and keeps full resolution for the same window. |
| [Plants per owner](../../doc/references/product-parameters.md) | Up to 50. | A limit of the public API; bounds list sizes. |
| [Sampling interval](../../doc/references/product-parameters.md) | 5 to 60 minutes, 15 by default. | At most 288 readings per sensor stick and day. |
| [Readings kept on a sensor stick](../../doc/references/product-parameters.md) | At least 2 880. | A client may upload thousands of readings of one sensor stick at once, in several batches. |

## Terms

| Source | What it says | What it means here |
|---|---|---|
| [Reading](../../doc/references/glossary.md) | One set of measurements taken at the same moment by one sensor stick, with a sequence number and a time. Never a single value. | The item that is uploaded, announced and stored. |
| [Batch](../../doc/references/glossary.md) | A group of readings of one sensor stick that is transferred together. | The body of one upload. |
| [Owner](../../doc/references/glossary.md) | The user a plant belongs to. A plant has one owner. | The identity a token stands for. Every query is limited to one owner. |
| [Threshold](../../doc/references/glossary.md) | A limit for one measured quantity of a plant, below or above which the plant needs attention. | Stored per plant; a lower and an upper one per quantity. |
| [Alert](../../doc/references/glossary.md) | The state "this plant needs attention for this reason". It opens once, stays open while the reason lasts, and closes. | A stored object with a life cycle, one per plant, quantity and threshold. |
| [Notification](../../doc/references/glossary.md) | A message to the owner about an alert that has opened. One per alert. | `cloud` hands one notification per alert to the push service. |
