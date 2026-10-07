---
unit: <folder-name>
summary: <what the unit is, one line, no full stop>
kind: <service | library | app | firmware | tool | specification | ...>
status: planned
provides:
  <port-name>:
    kind: <library | http | events | cli | ui | file | protocol | ...>
    summary: <what the port offers, one line>
    contract: doc/references/<port-name>.md
needs:
  <need-name>:
    kind: <kind>
    summary: <what this unit expects from whoever provides it, one line>
wiring:
  <child>.<need>: <child>.<port>
---
<!-- Delete: 'youmedoc: "0.1"' belongs into the manifest of the root unit only.
     Delete 'provides', 'needs' or 'wiring' if empty. 'wiring' only if the unit has children. -->
# <folder-name>

<One paragraph: what this unit is and what it is for. Understandable without any other file.>

## Provides

### `<port-name>`

<What it offers. What a user can rely on. Limits. A short example.>
Contract: [<port-name>](doc/references/<port-name>.md).

## Needs

### `<need-name>`

<What this unit expects from whoever provides this. Never name the provider.>

## Out of scope

- <What this unit deliberately does not do.>

## More

- [AGENTS.md](AGENTS.md): why the unit is built this way
- [Context diagram](doc/diagrams/context.md)
- [Component diagram](doc/diagrams/component.md) <!-- only if the unit has children -->
