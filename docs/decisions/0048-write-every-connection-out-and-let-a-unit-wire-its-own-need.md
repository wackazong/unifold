---
status: accepted
date: 2026-10-23
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Write every connection out, and let a unit wire its own need to a child

## Context and Problem Statement

Without the comparison with code ([0047](0047-remove-the-comparison-with-code.md)), rule `W3` reports a capability of a child that only code of the parent itself uses, for example a main program that calls its libraries. The parent needs a way to say what its own code uses. At the same time, implicit pass-up ([0024](0024-pass-needs-up-by-name-and-draw-shared-connections-once.md), kept by [0032](0032-write-every-unit-out-in-the-wiring.md)) connected a need of a child to a need of the parent with the same name, without a line. Once a parent has needs for its own code, an equal name would join the parent's own need and a child's need, although they are two different needs.

## Considered Options

- A new key `uses`, a list of child capabilities that the unit's own code uses
- A reserved wiring key that stands for the unit's own code (`self.clock`)
- A need of the unit, declared like any need and wired in the unit's own wiring to a child
- For pass-up: keep it, except into a need that the unit meets itself; or remove it

## Decision Outcome

Chosen option: "a need of the unit, wired to a child, and no implicit connection", because it needs no new key and no new word, and because a need is exactly what the parent's code has.

- A wiring key may be a need of the unit itself: `clock: platform.clock`. A child meets that need inside the unit. The unit above does not wire it, and at the root it is not a need of the project.
- Such a need is the unit's own. It never meets a need of a child, and a need of a child is not passed up to it.
- Nothing connects by an equal name. Every need of every child is met by a line of the parent: to a capability of a sibling, or passed up to a need of the parent (`child.clock: clock`).
- A bare key that names both a capability and a need of the unit is an error.
- A project of version 0.1 keeps its meaning ([0049](0049-call-the-standard-0-2.md)).
- This amends 0032: its "keep implicit pass-up by name" no longer stands; the rest, no wildcard and every unit written out, stands. It amends [0002](0002-declare-ports-and-wire-them-in-the-parent.md): a unit wires its children, and needs of its own that a child meets.

### Consequences

- Good: the wiring lists every connection; no need is connected by accident, and the risk "equal names connect" is gone.
- Good: what the parent's own code uses is in the map, in `show`, `impact` and the diagrams.
- Bad: more lines. Every pass-up is a line, so a need used deep in the tree costs a line at every level.
- Bad: a unit that has a capability and a need of the same name cannot use a bare key for either; it renames one.
