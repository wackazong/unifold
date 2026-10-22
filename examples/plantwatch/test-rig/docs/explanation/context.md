# Context of test-rig

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From plantwatch

### [plantwatch: README, `test-report`](../../../README.md#test-report)
<!-- unifold:cites sha=54edcda4 -->

Says: the project provides the result of the automated end-to-end tests as
a JUnit XML file. A run goes against a real or a simulated sensor stick.

Here: the rig's capability `test-report` is this result.

### [plantwatch: README, `app-ui`](../../../README.md#app-ui)
<!-- unifold:cites sha=55715f0d -->

Says: per plant the app shows the latest reading, the history and what the
plant needs; it works offline; a plant in need produces one notification.

Here: the project names the [test catalogue](../references/test-catalogue.md)
as what verifies this promise. The catalogue says which parts of it the
rig can observe and which it cannot.

### [plantwatch/0001 The phone relays between sensor stick and server](../../../docs/decisions/0001-the-phone-relays-between-sensor-and-server.md)
<!-- unifold:cites sha=6d7a73aa -->

Says: a sensor stick talks only to a phone, which carries the readings to
the server.

Here: to test the whole path the rig takes the place of the phone: it
fetches over BLE and uploads
([0003](../decisions/0003-the-rig-is-its-own-central.md)).

### [plantwatch/0002 Define the BLE profile and the reading format once, in a unit of their own](../../../docs/decisions/0002-define-the-profile-and-the-reading-format-once.md)
<!-- unifold:cites sha=a6b6b86f -->

Says: both definitions have one home and a version; every user states them
as a need. A change within a major version keeps older counterparts working.

Here: the needs `link-profile` and `reading-format`. The rig builds its
central from the first and its uploads from the second, and from nothing
else.

### [plantwatch/0003 The emulator implements the profile independently of the firmware](../../../docs/decisions/0003-the-emulator-implements-the-profile-independently.md)
<!-- unifold:cites sha=395c9767 -->

Says: the simulated sensor stick is written from the profile alone. A
difference in behaviour shows a gap in the profile or a fault in one of them.

Here: one catalogue runs in the configurations `real` and `simulated`, and
every result states which
([0001](../decisions/0001-one-catalogue-for-real-and-simulated-devices.md)).

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)
<!-- unifold:cites sha=dc18eb33 -->

Says: sensor id and sequence number identify a reading; it never changes.
Every hop may deliver it more than once; every receiver recognises it.

Here: the tests that fetch twice and upload twice, and the comparison of a
fetched reading with the history by this pair.

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../docs/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)
<!-- unifold:cites sha=c591e041 -->

Says: a reading carries a boot counter and seconds since that boot; the
central converts to UTC. A time it cannot compute is estimated and marked.

Here: as the central, the rig converts. LINK-07 and RELAY-05 test restarts
and the estimated flag.

### [plantwatch: conventions, measured quantities](../../../docs/references/conventions.md#measured-quantities)
<!-- unifold:cites sha=c9226f2c -->

Says: soil moisture 0 to 100 percent, light 0 to 100 000 lux, temperature
-20 to 60 °C. The first receiver rejects a value outside its range.

Here: what "a valid value" means in a test, and the limits the rig sets so
that every reading, or no reading, crosses a threshold.

### [plantwatch: conventions, delivery](../../../docs/references/conventions.md#delivery)
<!-- unifold:cites sha=2fec0e46 -->

Says: a transfer may deliver an item more than once; the receiver accepts
it and reports success. A sender deletes only after confirmation.

Here: the promises of the groups `link` and `relay`.

### [plantwatch: product parameters](../../../docs/references/product-parameters.md)
<!-- unifold:cites sha=b11fccd4 -->

Says: sampling interval 5 to 60 minutes, default 15; a sensor stick keeps at
least 2 880 readings; upload to notification under 1 minute; protocol version 1.

Here: the expected values in the catalogue and the waiting times in
[configurations.md](../references/configurations.md).

### [plantwatch: glossary](../../../docs/references/glossary.md)
<!-- unifold:cites sha=f8573e05 -->

Says: a scenario is a scripted course of sensor values over simulated time.
An alert opens once and closes; a notification is one message per alert.

Here: the rig observes alerts; "one notification" is tested as "one alert
whose notification was handed on". The rig's own terms are in its
[glossary](../references/glossary.md).
