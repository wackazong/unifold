---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Keep a time anchor per boot of a sensor stick

## Context and Problem Statement

The client converts tick counts to UTC. The BLE profile defines the computation for readings of the sensor stick's current boot: a time reference taken at the fetch. A reading from an earlier boot has a tick count that says nothing about the present. Such readings occur whenever a sensor stick has restarted, for example after a change of its cell, before all readings were fetched. The BLE profile lets a central use a reference it has kept for that boot and otherwise asks for an estimate, within bounds. Does the client keep references, and how does it estimate?

## Considered Options

- Flag every reading of an earlier boot as estimated and place it directly before the current boot
- Remember, per sensor stick and boot, when that boot began; compute exact times for boots the client has met before and estimate only the rest
- Ask the consumer for the times of readings it stored earlier and derive the boot's beginning from them

## Decision Outcome

Chosen option: "remember when each boot began", because in the common case the phone has fetched from a boot before the sensor stick restarts, and then every remaining reading of that boot gets an exact time from a few bytes of stored state.

The remembered value is called an anchor. The rules of the conversion and the number of anchors kept are in
[fetch-session.md](../references/fetch-session.md).

A reading of a boot without an anchor gets the latest time it can have and is flagged as estimated.

### Consequences

- Good: only readings of a boot the phone never met are estimated.
- Good: the conversion needs nothing from the consumer.
- Bad: the client has persistent state besides the pairings. Losing it does no harm beyond more estimated times.
- Bad: an anchor carries the error of the phone's clock at the moment it was taken into every later fetch from that boot.
- Bad: an estimate can be too late by the time the sensor stick was without power, which nobody knows.
- Bad: a second phone that fetches from the same boot computes its own anchor, so two phones may assign times that differ by seconds.

## More Information

The sensor stick's tick counter drifts against the phone's clock. Over the 30 days a sensor stick keeps readings, a drift of 50 parts per million adds up to about two minutes. The client does not correct it.
