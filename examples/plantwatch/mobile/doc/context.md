# Context of mobile

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## Decisions

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0001 The phone relays](../../doc/decisions/0001-the-phone-relays-between-sensor-and-server.md) | A sensor stick talks only to a phone. The phone app carries readings to the server. | The app is the only way for a reading to leave a sensor stick. It must fetch in the background, see [0002](decisions/0002-fetch-when-the-system-reports-a-paired-sensor-stick.md). |
| [plantwatch/0002 Profile and reading format defined once](../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md) | The BLE profile and the reading format are defined in one place. Every user states them as a need. Changes within a major version keep older counterparts working. | The app has the needs `link-profile` and `reading-format` and describes neither itself. It works with every sensor stick and server of major version 1. |
| [plantwatch/0004 Immutable readings](../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | A reading is identified by sensor id and sequence number and never changes. Every hop may deliver it more than once; every receiver recognises it. | The app stores a reading under this pair, accepts it a second time without storing it again, and repeats a transfer after any failure. |
| [plantwatch/0005 Ticks and UTC](../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | The sensor stick stamps a reading with a tick count. The phone converts it to UTC when it fetches. A time that cannot be computed is estimated and marked. | The app assigns the time of every reading, see [0003](decisions/0003-a-reading-gets-its-time-before-it-is-stored.md). The phone's clock is the time source of all history. |

## References

| Source | What it says | What it means here |
|---|---|---|
| [Conventions: measured quantities](../../doc/references/conventions.md) | Soil moisture in percent 0 to 100, light in lux 0 to 100 000, temperature in °C -20 to 60. A value outside its range is rejected by the first receiver. An unmeasured quantity is absent. | The app is the first receiver of a reading. It refuses invalid readings at the radio and shows an absent quantity as absent. |
| [Conventions: identifiers](../../doc/references/conventions.md) | Sensor id: 16 hex digits. Sequence number: unsigned 32 bit. Plant, owner, alert: UUID. | The [data model](references/data-model.md) uses these forms. |
| [Conventions: time](../../doc/references/conventions.md) | Outside the sensor stick every time is UTC, written as RFC 3339 with `Z` and whole seconds. An estimated time carries a flag. | The app stores UTC and converts to local time only on the screens. |
| [Conventions: delivery](../../doc/references/conventions.md) | A transfer may deliver an item more than once. The receiver accepts it and reports success. The sender deletes only after confirmation. | The order "store, then confirm, then delete" holds at both ends of the app, see [architecture](architecture.md). |
| [Conventions: HTTP ports](../../doc/references/conventions.md) | JSON bodies, lower-case field names with underscores, errors with `code` and `message`, repeated requests succeed again. | This is what the app expects of `cloud-api`. |
| [Product parameters](../../doc/references/product-parameters.md) | Up to 20 sensor sticks per phone, 50 plants per owner, 90 days of history on the phone. A sensor stick keeps 2 880 readings, 30 days at the default sampling interval of 15 minutes. Radio protocol version 1. | These are the limits of `app-ui`. One fetch may bring 2 880 readings from one sensor stick. |
| [Glossary](../../doc/references/glossary.md) | Defines plant, owner, sensor stick, sensor id, reading, sequence number, tick count, central, pairing, threshold, alert, notification, batch. | The app uses these terms unchanged. The phone is the central. An alert is a state the server decides; a notification is one message per alert. |
