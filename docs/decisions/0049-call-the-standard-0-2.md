---
status: accepted
date: 2026-10-23
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Call the standard 0.2

## Context and Problem Statement

[0047](0047-remove-the-comparison-with-code.md) changes what a checker reports, and [0048](0048-write-every-connection-out-and-let-a-unit-wire-its-own-need.md) changes what a wiring line means: a bare key may name a need, and a need of a child no longer passes up by name. Version 0.1 was published days before, so projects that say `unifold: "0.1"` may exist.

## Considered Options

- Keep 0.1 and change its meaning
- Call it 0.2, and read 0.1 projects with their old meaning
- Call it 0.2, and stop reading 0.1

## Decision Outcome

Chosen option: "0.2, and read 0.1 with its old meaning", because a manifest must not change its meaning while its version string stays the same.

- The root manifest says `unifold: "0.2"`; `init` writes it, and the package of the tool is 0.2.0.
- In a project of version 0.1, a bare wiring key names a capability, a need of a child passes up to a need of the parent with the same name, and a need of the unit as a key is reported with a hint to move to 0.2.
- The schema is served at `/0.2/` and, for manifests that point there, at `/0.1/`.

### Consequences

- Good: a 0.1 project keeps working, and its findings do not change.
- Good: the version names what a manifest means.
- Bad: the tool carries two meanings of a wiring line.
- Bad: a project that moves to 0.2 adds a line for every need that it passed up by name.
