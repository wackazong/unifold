<!-- Delete this comment. The manifest of the unit is in unit.yaml next to this file
     (see unit.template.yaml). It may instead be YAML front matter at the top of this file. -->
# <folder-name>

<One paragraph: what this unit is and what it is for. Understandable without any other file.>

## Provides

### `<port-name>`

<What it offers. What a user can rely on, each guarantee checkable: a value, a limit,
an order. Limits. A short example.>
Contract: [<port-name>](doc/references/<port-name>.md).

## Needs

### `<need-name>`

<What this unit expects from whoever provides this, in this unit's words. Never name
the provider. For an optional need: what the unit does without it.>

## Out of scope

- <What this unit deliberately does not do.>

## More

- [AGENTS.md](AGENTS.md): why the unit is built this way
- [doc/context.md](doc/context.md): what it inherits from above
- [Context diagram](doc/diagrams/context.md): the unit and its neighbours
- [Component diagram](doc/diagrams/component.md) <!-- only if the unit has children -->
- [Decisions](doc/decisions/index.md) <!-- only if the unit has decisions -->
