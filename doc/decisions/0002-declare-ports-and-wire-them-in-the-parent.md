---
status: proposed
date: 2026-10-06
---
# Declare ports in the unit and wire them in the parent

## Context and Problem Statement

A unit must be understandable on its own, and a parent must not know the
insides of its children. Dependencies between siblings have to be recorded
somewhere, in a form a tool can check and draw.

## Considered Options

- Each unit names the units it depends on
- Each unit declares named needs and provided ports; the parent connects
  them in a `wiring` map with the need as key and the provider as value
- A central file that lists all dependencies of the project

## Decision Outcome

Chosen option: "needs and provided ports, wired in the parent", because the
unit then never names a sibling, and the parent holds exactly the knowledge
that belongs to it: how its children fit together.

The map form `need: provider` was chosen over a list of arrows because a need
has one provider, a map makes a second line for the same need impossible, and
"is every need a key?" is a simple completeness check.

### Consequences

- Good: unmet needs and unused ports are found before code exists.
- Good: all three diagrams can be generated from the manifests.
- Good: a unit can be moved; only wiring lines move with it.
- Bad: something shared by siblings, such as a protocol definition, must be
  a unit of its own, otherwise siblings would refer to each other.
- Bad: one need has one provider or a list of alternatives. A set of
  simultaneous providers cannot be expressed.
- Bad: the manifest repeats, in coarse form, what the code's own interface
  files say. The `contract` field links the two; nothing checks that they
  agree.
