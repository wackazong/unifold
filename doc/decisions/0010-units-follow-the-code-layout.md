---
status: proposed
date: 2026-10-06
---
# Units follow the code layout

## Context and Problem Statement

Architecture descriptions often use building blocks that do not match the
folders of the code. The description and the code then drift apart, and a
reader cannot find the code that belongs to a box.

## Considered Options

- Abstract building blocks that are mapped to folders in a table
- The unit is a folder of the real code layout, and nothing else

## Decision Outcome

Chosen option: "the unit is the folder", because the mapping cannot go
stale when there is none, and because a difference between the intended
structure and the folder tree is treated as a fault of the folder tree.

The rule covers more than modules of one program. A service, a firmware
image, an emulator, a test rig or a mobile app is a unit when it has a
folder and an interface.

### Consequences

- Good: every box in a diagram is a folder a reader can open.
- Good: documents can be created before code, as the planned layout.
- Bad: a unit has exactly one parent. Things used across the tree need a
  common ancestor that wires them.
- Bad: views that do not follow the tree, such as deployment or runtime
  sequences, are outside the declared structure and are drawn by hand.
- Bad: a repository with a poor folder structure gets poor diagrams until
  the folders change.
