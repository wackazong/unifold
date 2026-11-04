# Context of ble-client

What this unit takes over from the units above, and what each item means here.

## From mobile

### [mobile/0002 Fetch in the background when the system reports a paired sensor stick](../../../docs/decisions/0002-fetch-when-the-system-reports-a-paired-sensor-stick.md)

The app leaves a standing request per paired sensor stick with the system and fetches when woken. A slot only fetches, stores and confirms.

The client owns the standing requests. It sets one at pairing, holds it back after a fetch so that a sensor stick in range is not connected again at once, and removes it at unpairing.

### [mobile/0003 A reading gets its UTC time before it is stored](../../../docs/decisions/0003-a-reading-gets-its-time-before-it-is-stored.md)

The part that fetches converts tick counts to UTC. Every reading that leaves it has a time and an estimated flag, and the tick count stays in it. The client does this conversion and hands the tick count on unchanged ([0002](../decisions/0002-keep-a-time-anchor-per-boot.md)).

### [mobile/0004 One codebase for both platforms](../../../docs/decisions/0004-one-codebase-for-both-platforms.md)

The app is written once. Code per platform is allowed in the radio part only, behind one interface that is the same for both platforms. This unit is that radio part. It holds an iOS and an Android implementation of one internal interface.

### [mobile: platform limits](../../../docs/references/platform-limits.md)

iOS wakes the app through a pending connection, and Android wakes it through a companion device association. The design budget is 10 seconds per wake-up.

The sizes, timeouts and triggers in [fetch-session.md](../references/fetch-session.md) follow from these limits. The values are unverified design assumptions, as their source says.

### [mobile: data model](../../../docs/references/data-model.md)

A reading has sensor id, sequence number, tick count, soil moisture, light, temperature, a UTC time and an estimated flag. A paired sensor stick has sensor id, time of pairing, time of the last complete fetch and the protocol version it states.

The client delivers readings and lists paired sensor sticks with exactly these fields.

### [mobile: glossary](../../../docs/references/glossary.md)

A fetch takes the stored readings of one sensor stick onto the phone and changes nothing there; the app confirms them once stored. A background slot is the run time after a wake-up.

The client carries out every fetch. Its own terms are in its [glossary](../references/glossary.md).

## From plantwatch

### [plantwatch/0004 Readings are immutable and identified by sensor id and sequence number](../../../../docs/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)

Sensor id and sequence number identify a reading. Every hop may deliver it more than once, and nobody changes it. The client may deliver a reading twice and says so in its contract. It never alters a value.

### [plantwatch/0005 The sensor stick counts ticks and the phone assigns UTC time](../../../../docs/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)

A reading carries a boot counter and the seconds since that boot. A time of an earlier boot that cannot be computed is estimated and marked. The client performs this conversion, as [fetch-session.md](../references/fetch-session.md) describes.

### [plantwatch: conventions](../../../../docs/references/conventions.md)

The first receiver rejects a value outside 0 to 100 percent, 0 to 100 000 lux or -20 to 60 °C. A sender deletes only what was confirmed.

The client is the first receiver, so it drops such a reading. It confirms to a sensor stick only after its consumer's acknowledgement.

### [plantwatch: product parameters](../../../../docs/references/product-parameters.md)

A phone can have up to 20 sensor sticks. A sensor stick keeps at least 2 880 readings and overwrites the oldest when full. The radio protocol is version 1.

Pairing refuses the 21st sensor stick. A fetch may bring 2 880 readings, and sequence numbers may have a gap.

### [plantwatch: glossary](../../../../docs/references/glossary.md)

The central connects to a sensor stick. Pairing binds a sensor stick to a phone and to a plant. A batch is readings of one sensor stick.

The client is the central. Its `pairing` capability does the phone half of pairing, and the client delivers in batches.
