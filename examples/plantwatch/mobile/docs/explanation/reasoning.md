# Reasoning of mobile

The long form of the why in [README.md](../../README.md). Which parts exist and how they are wired is shown in the
[component diagram](../diagrams/component.md).

**Three rhythms, three parts.** Radio contact, network contact and the owner's attention come and go independently. A design in which one of them waits for another fails in daily use: a screen that waits for the radio freezes when the sensor stick is out of range, and a fetch that waits for the network loses its short background slot. Each rhythm therefore has a part of its own, and the parts meet only at a store on the phone
([0001](../decisions/0001-the-local-store-is-the-only-source-for-the-screens.md)).

**The operating system decides when the app runs.** In the background the app runs only when the system wakes it, and only for a short time ([platform limits](../references/platform-limits.md)). The app therefore lets the system watch for paired sensor sticks and does the minimum in each slot: fetch, store, confirm
([0002](../decisions/0002-fetch-when-the-system-reports-a-paired-sensor-stick.md)).
Uploading is separate work that may happen in the same slot or hours later.

**Time is settled at the door.** Tick counts mean something only together with the moment of the fetch. The part that fetches turns them into UTC. The tick count travels on inside the reading, and nothing behind the fetch computes with it
([0003](../decisions/0003-a-reading-gets-its-time-before-it-is-stored.md)).

**Platform differences stay in one corner.** Background wake-up and BLE are the only things that iOS and Android do in truly different ways. Everything else is written once
([0004](../decisions/0004-one-codebase-for-both-platforms.md)).

**A notification is a pointer, not data.** Registering the phone for notifications belongs to the screens, because the owner grants the permission on a screen and a tap leads into the navigation. A notification names a plant; what the screen then shows comes from the store like everything else.

## Trade-offs

| Chosen | Given up | Decision |
|---|---|---|
| The screens read from a store on the phone and from nothing else | The phone holds a copy of server data, and the two can differ for days. The app shows the age of what it holds instead of hiding the difference. | [0001](../decisions/0001-the-local-store-is-the-only-source-for-the-screens.md) |
| One part per rhythm, meeting only at the store | A reading passes through two hand-overs inside the app. Each one follows the rule "store, then confirm" and may repeat. | [0001](../decisions/0001-the-local-store-is-the-only-source-for-the-screens.md) |
| The system watches for paired sensor sticks | A slot can be as short as about 10 seconds, so a fetch must be resumable; the mechanism is written once per platform | [0002](../decisions/0002-fetch-when-the-system-reports-a-paired-sensor-stick.md) |
