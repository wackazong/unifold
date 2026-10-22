---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# One codebase for both platforms

## Context and Problem Statement

The app must exist for iOS and for Android. Most of it is the same on both: a store, an exchange with a server, a handful of screens. One part is not: BLE and the background wake-up work differently on each platform ([platform limits](../references/platform-limits.md)). How many codebases does the app have?

## Decision Drivers

- A small team maintains the app
- Background fetching needs the platforms' own interfaces, without compromise
- Both platforms get the same features at the same time

## Considered Options

- Two native apps, one in Swift and one in Kotlin
- A shared core library with two native user interfaces
- One codebase in a cross-platform toolkit, with native code only where the platforms differ

## Decision Outcome

Chosen option: "one codebase in a cross-platform toolkit", because the screens, the store and the exchange with the server are the larger part of the work and gain nothing from being written twice.

The toolkit is Flutter. Code that exists once per platform is allowed in the radio part only: the BLE calls and the background wake-up. It is reached through one interface that is the same for both platforms.

### Consequences

- Good: one implementation of the screens, the store and the exchange with the server; one set of tests for them.
- Good: both platforms are released together.
- Bad: the radio part is written twice after all, and it is the part that is hardest to test.
- Bad: when the system wakes the app in the background, the toolkit's runtime must start before any shared code runs. This start-up time comes out of the short background slot and has to be measured on real phones.
- Bad: the app depends on the toolkit keeping up with new system versions.

## Pros and Cons of the Options

### Two native apps

- Good: direct access to every platform interface; shortest start-up in the background.
- Bad: every screen and every rule of the store exists twice and drifts.

### Shared core library with native user interfaces

- Good: the store and the exchange with the server exist once.
- Bad: the screens exist twice, and the border between the core and the two user interfaces is a third thing to maintain.
