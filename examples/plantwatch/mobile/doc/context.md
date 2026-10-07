# Context of mobile

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From plantwatch

### [plantwatch: README, `app-ui`](../../README.md)

Says: per plant the app shows the latest reading, the history and what the
plant needs; it works offline; a plant in need produces one notification.

Here: the port `app-ui` of this unit is that promise. The app shows and
reacts to notifications; that there is only one per alert is not its doing.

### [plantwatch/0001 The phone relays between sensor stick and server](../../doc/decisions/0001-the-phone-relays-between-sensor-and-server.md)

Says: a sensor stick talks only to a phone. The phone app carries the
readings to the server.

Here: the app is the only way for a reading to leave a sensor stick, so it
fetches in the background
([0002](decisions/0002-fetch-when-the-system-reports-a-paired-sensor-stick.md)).

### [plantwatch/0002 Define the BLE profile and the reading format once, in a unit of their own](../../doc/decisions/0002-define-the-profile-and-the-reading-format-once.md)

Says: both definitions have one home and a version; every user states them
as a need. A change within a major version keeps older counterparts working.

Here: the needs `link-profile` and `reading-format`. The app describes
neither and works with every counterpart of major version 1.

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

Says: sensor id and sequence number identify a reading; it never changes.
Every hop may deliver it more than once; every receiver recognises it.

Here: the app stores a reading under this pair, keeps the copy it stored
first, and repeats a transfer after any failure.

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

Says: a reading carries a tick count. The phone converts it to UTC when it
fetches; a time it cannot compute is estimated and marked.

Here: the app assigns the time of every reading
([0003](decisions/0003-a-reading-gets-its-time-before-it-is-stored.md)).
The phone's clock is the time source of all history.

### [plantwatch/0006 The server side alone decides whether a plant needs attention](../../doc/decisions/0006-the-server-side-alone-decides-what-needs-attention.md)

Says: only the server side compares readings with thresholds. Every other
part shows or carries what it decided.

Here: the app computes no alert. A fetched reading below a threshold shows
in the history and becomes an alert only when the server says so.

### [plantwatch: conventions, measured quantities](../../doc/references/conventions.md)

Says: soil moisture 0 to 100 percent, light 0 to 100 000 lux, temperature
-20 to 60 °C. The first receiver rejects a value outside its range.

Here: the app is the first receiver of a reading and refuses invalid ones
at the radio. The [data model](references/data-model.md) uses these units.

### [plantwatch: conventions, identifiers and time](../../doc/references/conventions.md)

Says: sensor id 16 lower-case hex digits; plant, owner and alert a UUID.
Outside the sensor stick a time is UTC, RFC 3339 with `Z`, whole seconds.

Here: the forms in the [data model](references/data-model.md). The app
converts to local time only on the screens.

### [plantwatch: conventions, delivery](../../doc/references/conventions.md)

Says: a transfer may deliver an item more than once and the receiver
reports success. A sender deletes an item only after the receiver confirmed.

Here: the order "store, then confirm, then delete" at both ends of the app
([architecture](architecture.md)).

### [plantwatch: product parameters](../../doc/references/product-parameters.md)

Says: up to 20 sensor sticks per phone, 50 plants per owner, 90 days of history
on the phone; a sensor stick keeps 2 880 readings; radio protocol version 1.

Here: the limits of `app-ui`. One fetch may bring 2 880 readings from one
sensor stick. The app supports major version 1.

### [plantwatch: glossary](../../doc/references/glossary.md)

Says: an alert is the state "this plant needs attention for this reason";
a notification is one message per alert; a central connects to a sensor stick.

Here: the app uses the project's terms unchanged and adds its own in its
[glossary](references/glossary.md). The phone is the central.
