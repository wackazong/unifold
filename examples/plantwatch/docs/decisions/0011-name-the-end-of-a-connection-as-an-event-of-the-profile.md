---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Name the end of a connection as an event of the profile

## Context and Problem Statement

The [BLE profile](../references/ble-profile/index.md) describes how a connection ends: the central disconnects, the sensor stick disconnects after 30 seconds without a request or after 10 minutes, or the radio link breaks after the supervision timeout of 4 seconds. No part of the profile stands for this end. Its states therefore could only lead back to `disconnected` through `advertising`, which the sensor stick sends after the end, not as its cause. A central that followed that table would wait up to a second for advertising to notice that its connection is gone, although its Bluetooth stack tells it at once. How does the profile name the end of a connection?

## Considered Options

- Advertising while connected leads to `disconnected`
- An event part `disconnected`, raised when the connection ends by either side or by the radio link
- The error of the next request on a connection that has ended

## Decision Outcome

Chosen option: "an event part `disconnected`", because it names what a central's Bluetooth stack reports at the moment it happens, and it covers every cause the profile already lists. The profile changes no behaviour of a sensor stick: it already initiates "a disconnect" and advertises again within 1 second.

### Consequences

- Good: the states of the profile name the cause of each transition, and the fake of the profile raises the same event that a test of a central waits for.
- Bad: the profile has a part that no characteristic carries. It comes from the Bluetooth stack of the central, not from a GATT attribute.

## More Information

The contract [`ble-profile`](../references/ble-profile/index.md) and its part [`disconnected`](../references/ble-profile/disconnected.md) state the result.
