---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# A unit is a folder with a manifest

## Context and Problem Statement

An architecture that lives in a separate document goes stale, and a coding agent cannot take it in beside the code. The knowledge about a folder should sit in that folder, and the parts of the architecture should be the parts of the repository. What marks a part of the architecture, and where does its description live?

## Decision

- A unit is a folder that contains a file `unifold.yaml`, its manifest. Nothing else makes a folder a unit; the folder's name is the unit's name.
- Units follow the code layout. unifold adds no folders of its own except `docs/`. A unit should hold code that is built, run or deployed; a document is never a unit.
- The manifest states what the unit is responsible for, what it provides (capabilities), what it needs, how its children are connected (wiring) and the stories it holds (scenarios). The root manifest names the version of the standard.
- The folders that are never searched for units: dot folders, the `docs` of a unit, `node_modules`, `__pycache__`, virtual environments, Cargo build folders, symbolic links, folders under `ignore`, and what version control ignores.

## Consequences

- Good: a reader and an agent find everything about a folder in that folder, and the tree of folders is the architecture.
- Good: one unit can be declared while the rest of the repository stays untouched.
- Bad: a layout that does not match the architecture is described as it is; unifold does not ask for a restructuring.
