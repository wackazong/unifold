# <folder-name>

<One paragraph: what this unit is and what it is for, and for whom. Understandable
without any other file.>

## Why

<Why this unit exists and what makes it change. Why it is cut this way: the forces,
the main trade-off, what must stay true. At most 20 lines that are not blank. No list
of children, capabilities or connections: `unifold show` prints those. The long form
is docs/explanation/reasoning.md.>

## Capabilities

### `<capability-name>`

<What it offers. What a user can rely on, each guarantee in a form a test could check:
a value, a limit, an order. A short example.>
Contract: [<capability-name>](docs/references/<capability-name>.md).

## Needs

### `<need-name>`

<What this unit expects from whoever provides this, in this unit's words. Never name
the provider. For an optional need: what the unit does without it.>

## Out of scope

- <What this unit deliberately does not do.>

## Commands

<!-- Optional: the few commands to build, test and run this unit. -->

## Read next

<!-- Optional: a few links into docs/ whose order matters. Delete the section otherwise. -->
