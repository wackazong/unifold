---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Needs never name a provider; the unit above wires

## Context and Problem Statement

When a module names the module it depends on, both are coupled, and neither can be understood or replaced alone. Build files record dependencies as names of packages. How does a unit say what it depends on without knowing who supplies it?

## Decision

- A unit declares **needs**: what it requires, never who supplies it. It declares **capabilities**: what it provides, never who uses it.
- The nearest unit above connects every need of its children to a provider in its `wiring`, one line each: a capability of a sibling, or a need of its own, through which the need is passed up. A unit may also meet a need of its own code with a capability of a child, and implement a capability of its own with one of a child.
- Every need of a child is wired, or marked `optional`, or met inside the child. Nothing connects by an equal name.
- A wiring line names only entries of the unit and of its direct children; a reference is split at its last dot, and a child in a plain folder is named by its folder name or path.
- Named alternatives give a need several providers; the first is the default. The build or deployment chooses.
- A need or capability that only passes through may be an empty entry: it takes summary and contract from the one line that wires it.

## Consequences

- Good: a unit can be read, tested with a fake, and replaced without opening its neighbours.
- Good: the map is complete by construction; a missing line is an error, not an oversight.
- Bad: a need used deep in the tree costs a line at every level on the way up.
