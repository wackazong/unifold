---
status: superseded by 0032
date: 2026-10-07
---
# Pass needs up by name and draw shared connections once

## Context and Problem Statement

[0018](0018-allow-one-wiring-line-for-several-children.md) allowed one
line for several children and required an explicit line for every need
that a unit passes to its parent. In the large example 21 of 65 wiring
lines only passed a need up under the same name. In the trial on a set of
services, ten arrows to one shared definition and seven to telemetry hid
the sixteen arrows that showed who calls whom.

## Considered Options

- Keep explicit lines everywhere
- Resolve an unwired need through all ancestors without declarations
- Implicit pass-up by name, one level at a time: a child's need without a
  line is connected to the parent's own need of the same name, if the
  parent declares one
- For diagrams: one arrow per connection, or list connections made by a
  `"*.need"` line once below the picture

## Decision Outcome

Chosen options: "implicit pass-up by name" and "list shared connections
once", because both remove repetition without hiding a dependency: every
unit on the way still declares the need in its own manifest.

- An explicit line wins over a `"*.need"` line, which wins over the
  implicit rule. Only a need with no provider by any of the three is
  unconnected.
- `show` marks such a connection as passed up by name.

### Consequences

- Good: a pass-up costs one declaration per level and no wiring line.
- Good: diagrams of systems with a shared definition stay readable.
- Bad: equal names now have meaning. A child's need that happens to have
  the name of an unrelated need of the parent is connected silently.
- Bad: a connection can exist without a line to point at in a review.
- Bad: a shared connection is less visible in the picture than a drawn
  arrow; a reader must look below it.
