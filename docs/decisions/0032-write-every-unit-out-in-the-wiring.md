---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Write every unit out in the wiring

## Context and Problem Statement

[0018](0018-allow-one-wiring-line-for-several-children.md) introduced the key `"*.need"` for all direct children that have a need of that name, and [0024](0024-pass-needs-up-by-name-and-draw-shared-connections-once.md) kept it beside implicit pass-up by name. Two forms then saved the same lines, and the star turned the wiring of a unit from a list of its connections into a pattern that a reader has to resolve against the set of children. It also made the manifest change meaning when a child is added: a new folder is wired by a line that nobody touched, and no review sees it. In the example and in the trial on a set of services, every star line stood for a need that the parent could just as well declare itself.

## Considered Options

- Keep the star for direct children
- Keep the star and drop implicit pass-up by name
- Write every unit out: no wildcard in a key or a value, and keep implicit pass-up by name for what is the same for everybody

## Decision Outcome

Chosen option: "write every unit out", because the wiring of a unit should name every connection inside it, and because implicit pass-up already covers the case the star was for without hiding which units are connected.

- A key is `child.need` or a port of the unit. A `*` in a key or a value is an error (`W1`), as is a wildcard in any other form.
- A need that several children have, from one provider, costs one line per child. Where the children use the same name, the parent MAY declare the need itself instead; every child then passes it up by name and no line is needed.
- Diagrams keep listing connections once below the picture, under "Shared connections, not drawn", for a need that three or more children pass up by name. `unifold init` drafts one line per need and collapses nothing.

### Consequences

- Good: the wiring lists what is connected; adding a child cannot change a connection without a change to a manifest.
- Good: one form less to learn, and no quoted keys in YAML.
- Bad: a provider used by many siblings takes a line per sibling, unless the need is declared in the parent and passed up.
- Bad: the diagrams of the example projects get more arrows where a star line used to be collapsed below the picture.
