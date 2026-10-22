---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Define the BLE profile and the reading format as references of plantwatch

## Context and Problem Statement

Decision 0002 put the BLE profile and the reading format into a unit of their own, `protocol`, and every part that used one stated it as a need. The unit held documents and no code. Nothing in code could depend on it, so its seven connections could never be confirmed against the code, and every part that implemented the profile carried two needs for one relationship: the sensor stick, and the description of the sensor stick. The standard now says that a unit holds code and that both sides of a connection name the same contract. Where do the two definitions live?

## Considered Options

- Keep the unit and accept that its connections are not comparable with code
- The firmware owns the profile; the emulator, the app and the rig point at its documents
- Both definitions are references of plantwatch, the unit that wires the parts; every connection that carries the profile names it as contract

## Decision Outcome

Chosen option: "references of plantwatch", because the parts that implement the profile are children of plantwatch and a manifest never points into a sibling, so the one place that all of them can name is the unit above them.

- `docs/references/ble-profile/` is the contract of `device.ble-link`, `emulator.ble-link`, `mobile.sensor-link` and `test-rig.device-under-test`, and of `link.ble-link` and `ble-client.sensor-link` below them.
- `docs/references/reading-schema.md` is not a contract of its own: a reading travels inside the profile and inside the public API. The units that read or write readings cite it in their context files.
- The decisions and the skill of the former unit are decisions and a skill of plantwatch. Its glossary and its rules for changing a definition are merged into the root's.
- Both definitions keep their version. A change within a major version keeps older counterparts working, as 0002 said.

### Consequences

- Good: a change to the profile is a change to the root, and `unifold capability . ble-link` lists every implementer.
- Good: the component diagram shows the data paths and nothing else.
- Bad: the definition that the firmware implements lives above the firmware. A reader of `device` reaches it through the manifest.
- Bad: the reading format has no connection that names it, so drift between a writer and a reader of readings is found by the stamps in the context files, not by the checker.
