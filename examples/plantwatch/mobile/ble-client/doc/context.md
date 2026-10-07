# Context of ble-client

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From mobile

| Source | What it says | What it means here |
|---|---|---|
| [mobile/0002 Fetch when the system reports a paired sensor stick](../../doc/decisions/0002-fetch-when-the-system-reports-a-paired-sensor-stick.md) | The app hands the operating system a standing request per paired sensor stick and fetches when the system reports one, and also in slots of scheduled background work. A background slot does only fetch, store, confirm. A sensor stick that stays in range must not be connected again at once. | The client owns the standing requests: it sets one at pairing, holds it back after a fetch, and removes it at unpairing. A fetch must make progress within one short slot. |
| [mobile/0003 A reading gets its time before it is stored](../../doc/decisions/0003-a-reading-gets-its-time-before-it-is-stored.md) | The part that fetches converts tick counts to UTC. Every reading that leaves it has a time and an estimated flag. The tick count stays in the reading; nothing else computes with it. | The client converts. It hands the tick count on unchanged. See [0002](decisions/0002-keep-a-time-anchor-per-boot.md). |
| [mobile/0004 One codebase for both platforms](../../doc/decisions/0004-one-codebase-for-both-platforms.md) | The app is written once. Code per platform is allowed in the radio part only, behind one common interface. | This unit is that radio part. It contains an iOS and an Android implementation of the same internal interface. |
| [mobile: platform limits](../../doc/references/platform-limits.md) | iOS wakes the app through a pending connection, Android through a companion device association. The design budget is 10 seconds per wake-up. Scheduled background work runs when the system chooses. A search needs the app on the screen. | The sizes, timeouts and triggers in [fetch-session.md](references/fetch-session.md) follow from these. |
| [mobile: data model](../../doc/references/data-model.md) | A reading has sensor id, sequence number, tick count, soil moisture, light, temperature, a UTC time and an estimated flag. A paired sensor stick has sensor id, time of pairing, last fetch and protocol version. | The client delivers readings and reports paired sensor sticks with exactly these fields. |

## From plantwatch

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0004 Immutable readings](../../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | A reading is identified by sensor id and sequence number. Every hop may deliver it more than once. | The client may deliver a reading twice and says so in its contract. It never alters a value. |
| [plantwatch/0005 Ticks and UTC](../../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | A reading carries a boot counter and the seconds since that boot. The phone reads the current tick count at the fetch and computes UTC. Times of earlier boots that cannot be computed are estimated and marked. | This is the conversion the client performs. |
| [Conventions: measured quantities](../../../doc/references/conventions.md) | Soil moisture 0 to 100 percent, light 0 to 100 000 lux, temperature -20 to 60 °C. The first receiver rejects a value outside its range. An unmeasured quantity is absent. | The client is the first receiver. It drops a reading with an invalid value and still confirms it. |
| [Conventions: delivery](../../../doc/references/conventions.md) | The sender deletes an item only after the receiver has confirmed it. | The client confirms to the sensor stick only after its consumer's acknowledgement. |
| [Conventions: identifiers](../../../doc/references/conventions.md) | Sensor id: 8 bytes as 16 lower-case hex digits. Sequence number: unsigned 32 bit. | The form of both in the provided ports. |
| [Product parameters](../../../doc/references/product-parameters.md) | Up to 20 sensor sticks per phone. A sensor stick keeps at least 2 880 readings and overwrites the oldest when full. Radio protocol version 1. | Pairing refuses the 21st sensor stick. A fetch may bring 2 880 readings; sequence numbers may have a gap where readings were overwritten. |
| [Glossary](../../../doc/references/glossary.md) | Central: the side that connects to a sensor stick. Pairing: binding a sensor stick to a phone and to a plant. Batch: readings of one sensor stick transferred together. Tick count: boot counter and seconds since that boot. | The client is the central. Its `pairing` port does the phone half of pairing. It delivers in batches. |
