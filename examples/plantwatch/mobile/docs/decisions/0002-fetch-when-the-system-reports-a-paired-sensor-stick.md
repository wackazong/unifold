---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Fetch in the background when the system reports a paired sensor stick

## Context and Problem Statement

Readings reach the server only when the phone has fetched them. An owner who never opens the app must still get alerts. iOS and Android restrict what an app does while it is not on the screen; the facts are in [platform limits](../references/platform-limits.md). How does the app fetch without the owner's help?

## Decision Drivers

- Readings arrive without the owner opening the app
- No visible cost for the owner: no permanent notification, no battery drain
- The same behaviour, as far as possible, on both platforms

## Considered Options

- Fetch only while the app is open
- Scan periodically from a background task that the system schedules
- Keep a permanent foreground service that scans all the time
- Hand the system a standing request for each paired sensor stick and fetch when the system reports that one is present

## Decision Outcome

Chosen option: "a standing request per paired sensor stick", because it is the only option that both platforms support without a visible cost and that reacts when the phone actually comes near a sensor stick.

On iOS the request is a pending connection to a known peripheral. On Android it is a companion device association with presence observation. In both cases the system starts the app when the sensor stick advertises.

Opening the app always starts a fetch as well. In addition the app asks the system for scheduled background work and tries a fetch in every slot it gets. Together these cover the cases in which the system does not report a sensor stick, among them a phone that never leaves the range of its plants.

A background slot does only what cannot wait: fetch, store, confirm. Uploading follows if run time is left, otherwise at the next opportunity.

### Consequences

- Good: an owner who walks past the plants gets the readings onto the phone without doing anything.
- Good: the app uses no energy while no sensor stick is near.
- Bad: a slot can be as short as about 10 seconds. A long backlog needs several slots or an open app, so the fetch must be resumable.
- Bad: the mechanism differs per platform and must be written twice.
- Bad: a sensor stick that stays in range would be connected again the moment a fetch has ended, which costs its cell. The radio part has to hold back the next request until a new reading is due, and the systems offer no exact timer for that in the background.
- Bad: a force-quit app is not woken on iOS. The app cannot detect this beforehand; it can only show the owner how old the data is.
- Bad: the behaviour depends on system versions and on manufacturers' battery savers and has to be re-verified regularly.

## Pros and Cons of the Options

### Fetch only while the app is open

- Good: simple and identical on both platforms.
- Bad: no alert for an owner who does not open the app, which defeats the purpose of the product.

### Scan periodically from a scheduled background task

- Good: one mechanism for radio and upload.
- Bad: the system chooses the moment, often hours apart and seldom when the phone is near a plant.

### Permanent foreground service

- Good: reliable on Android.
- Bad: impossible on iOS; shows a permanent notification and costs battery on Android.
