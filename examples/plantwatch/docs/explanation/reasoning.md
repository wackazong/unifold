# Reasoning of plantwatch

The long form of the why in [README.md](../../README.md). Which parts exist
and how they are wired is shown in the
[component diagram](../diagrams/component.md).

**Battery life decides the radio.** A sensor stick runs for a year on a coin
cell only if it sleeps almost always. That rules out Wi-Fi and leaves
Bluetooth Low Energy. BLE reaches a phone, not the internet, so a phone has to
carry the readings onward
([0001](../decisions/0001-the-phone-relays-between-sensor-and-server.md)).

**A relay that is often absent decides the data model.** The phone may be
away for days. Readings therefore wait on the sensor stick, travel in batches,
and may be sent twice when a transfer is interrupted. Every hop is allowed to
deliver a reading more than once, and every receiver recognises a reading it
already has
([0004](../decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md)).

**No clock on the sensor stick decides who assigns time.** A coin-cell device
without a network has no trustworthy wall clock. It counts ticks; the phone,
which knows the time, converts ticks to UTC when it fetches
([0005](../decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md)).

**Shared definitions get an owner.** The radio protocol and the reading format
are used by several parts and owned by none, so they have a unit of their own
([0002](../decisions/0002-define-the-profile-and-the-reading-format-once.md)).

## Trade-offs

| Chosen | Given up | Decision |
|---|---|---|
| The phone relays between sensor stick and server | A reading reaches the server only after a phone was near the sensor stick and online | [0001](../decisions/0001-the-phone-relays-between-sensor-and-server.md) |
| Every hop delivers at least once | Every receiver must recognise a reading it already has | [0004](../decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) |
| The sensor stick counts ticks, the phone assigns time | A time that could only be estimated is flagged, and such a reading changes no alert | [0005](../decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) |
| The profile and the reading format are a unit of their own | A change to either touches one more unit | [0002](../decisions/0002-define-the-profile-and-the-reading-format-once.md) |
