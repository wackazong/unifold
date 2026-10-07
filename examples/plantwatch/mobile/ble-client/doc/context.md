# Context of ble-client

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From mobile

### [mobile/0002 Fetch in the background when the system reports a paired sensor stick](../../doc/decisions/0002-fetch-when-the-system-reports-a-paired-sensor-stick.md)

Says: the app leaves a standing request per paired sensor stick with the
system and fetches when woken. A slot does only fetch, store, confirm.

Here: the client owns the standing requests. It sets one at pairing, holds
it back after a fetch so that a sensor stick in range is not connected
again at once, and removes it at unpairing.

### [mobile/0003 A reading gets its UTC time before it is stored](../../doc/decisions/0003-a-reading-gets-its-time-before-it-is-stored.md)

Says: the part that fetches converts tick counts to UTC. Every reading that
leaves it has a time and an estimated flag; the tick count stays in it.

Here: the client converts and hands the tick count on unchanged
([0002](decisions/0002-keep-a-time-anchor-per-boot.md)).

### [mobile/0004 One codebase for both platforms](../../doc/decisions/0004-one-codebase-for-both-platforms.md)

Says: the app is written once. Code per platform is allowed in the radio
part only, behind one interface that is the same for both platforms.

Here: this unit is that radio part. It holds an iOS and an Android
implementation of one internal interface.

### [mobile: platform limits](../../doc/references/platform-limits.md)

Says: iOS wakes the app through a pending connection, Android through a
companion device association. Design budget: 10 seconds per wake-up.

Here: the sizes, timeouts and triggers in
[fetch-session.md](references/fetch-session.md). The values are unverified
design assumptions, as their source says.

### [mobile: data model](../../doc/references/data-model.md)

Says: a reading has sensor id, sequence number, tick count, soil moisture,
light, temperature, a UTC time and an estimated flag. A paired sensor stick
has sensor id, time of pairing, time of the last complete fetch and the
protocol version it states.

Here: the client delivers readings and lists paired sensor sticks with
exactly these fields.

### [mobile: glossary](../../doc/references/glossary.md)

Says: a fetch takes the stored readings of one sensor stick onto the phone
and confirms them. A background slot is the run time after a wake-up.

Here: the client carries out every fetch. Its own terms are in its
[glossary](references/glossary.md).

## From plantwatch

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

Says: sensor id and sequence number identify a reading. Every hop may
deliver it more than once. Nobody changes it.

Here: the client may deliver a reading twice and says so in its contract.
It never alters a value.

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

Says: a reading carries a boot counter and the seconds since that boot. A
time of an earlier boot that cannot be computed is estimated and marked.

Here: the conversion the client performs, in
[fetch-session.md](references/fetch-session.md).

### [plantwatch: conventions](../../../doc/references/conventions.md)

Says: the first receiver rejects a value outside 0 to 100 percent, 0 to
100 000 lux or -20 to 60 °C. A sender deletes only what was confirmed.

Here: the client is the first receiver; it drops such a reading. It
confirms to a sensor stick only after its consumer's acknowledgement.

### [plantwatch: product parameters](../../../doc/references/product-parameters.md)

Says: up to 20 sensor sticks per phone. A sensor stick keeps at least 2 880
readings and overwrites the oldest when full. Radio protocol version 1.

Here: pairing refuses the 21st sensor stick. A fetch may bring 2 880
readings, and sequence numbers may have a gap.

### [plantwatch: glossary](../../../doc/references/glossary.md)

Says: the central connects to a sensor stick. Pairing binds a sensor stick
to a phone and to a plant. A batch is readings of one sensor stick.

Here: the client is the central. Its `pairing` port does the phone half of
pairing. It delivers in batches.
