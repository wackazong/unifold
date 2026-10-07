# Wiring

A unit declares what it needs. It does not say who supplies it. The parent
unit decides that in the `wiring` map of its [manifest](manifest.md).

```yaml
wiring:
  <need>: <provider>
```

The need is the key. The provider is the value. Read each line as "this need
is met by that provider". The parent is the composition root of its children.

## Endpoints

An endpoint is a port of a direct child, written `child.port`, or a port of
the unit itself, written as the bare port name.

| Key (the need) | Value (the provider) | Meaning |
|---|---|---|
| `child.need` | `sibling.port` | A child's need is met by another child |
| `child.need` | `own-need` | A child's need is passed up: it is met by whatever meets this unit's own need |
| `own-port` | `child.port` | A port this unit provides is implemented by a child |
| `child.need` | `./folder` | A child's need is met by code in a plain folder of this unit that is not a unit yet |

Seen from inside a unit, its own provided ports are things that need an
implementation, and its own needs are things that are available. That is why
an own provided port stands on the key side and an own need on the value side.

Not allowed:

- `own-port: own-need`. A unit that only passes something through has no
  reason to list it.
- A child that provides for its own need.
- An endpoint that reaches into a grandchild, such as `a.b.port`. If a parent
  needs something from deeper down, the child provides it as a port of its
  own and delegates it inward.

## Alternatives

A need may have several possible providers, for example real hardware and an
emulator, or a database and an in-memory stand-in. Give each a name:

```yaml
wiring:
  test-rig.device-under-test:
    real: device.ble-link
    simulated: emulator.ble-link
```

Exactly one alternative is active in a given configuration. The first is the
default. Use the same names for all needs that switch together. Every
alternative MUST meet everything the need expects, by itself and in its
default configuration; a stand-in that does less is a different port. Where
the alternatives implement one shared definition, each says so with
`conforms-to` ([manifest.md](manifest.md)). Diagrams draw the default solid
and the others dashed.

## One line for several children

When several children have a need of the same name and the same provider,
one line wires them all. The key must be quoted in YAML:

```yaml
wiring:
  "*.event-bus": platform.event-bus     # every child that needs event-bus
  "*.clock": clock                      # passed up to this unit's own need
```

A line for a single child takes precedence. The star stands for direct
children only; a need deeper in the tree is still declared and passed up by
every unit in between, because a unit's manifest must show everything the
unit depends on.

## Plain-folder providers

`./folder` names a folder inside the unit that is not a unit. It lets a
project adopt youmedoc one folder at a time: the first unit can be wired
before the code it depends on has been described. The checker reports each
such line as an info (`W8`). It is a to-do, not a permanent state.

## What the checker verifies

| Check | Result |
|---|---|
| Every endpoint names an existing child and an existing port on the correct side | error `W1` |
| Every need of every child is a key in the parent's wiring, unless it is `optional` | error `W2` |
| Every provided port of every child is the value of at least one line | warning `W3`: provided but not needed |
| Need and provider have the same `kind` | warning `W4` |
| Children do not need each other in a cycle | warning `W7` |
| An own need of a unit with children is passed to a child; an own port is delegated | info `W5`, `W6` |

The needs of the root unit have no parent. They are the external dependencies
of the project and are never wired.

`W4` usually shows a missing adapter: a unit that needs the one kind and
provides the other ([principles.md](principles.md)). Do not fix it by
changing the kind of the need.

## The arrow means "needs"

A wiring line records a dependency, not the direction in which data flows. A
unit that subscribes to events *needs* the event stream; the publisher
*provides* it. Generated diagrams draw every arrow from the need to the
provider.

## Example: microservices

```yaml
unit: cloud
provides:
  public-api: {kind: http, summary: Upload readings and query plants}
needs:
  push-service: {kind: http, summary: Delivers a notification to a phone}
wiring:
  public-api: gateway.public-api          # delegated to a child
  gateway.uploads: ingest.ingest-api      # sibling to sibling
  alerts.readings: ingest.reading-events  # subscriber needs the publisher's stream
  ingest.bus: platform.event-bus
  alerts.bus: platform.event-bus
  alerts.push: push-service               # passed up to this unit's own need
```

## Example: a product made of several components

A device, an emulator, a test rig and a mobile app share one protocol. The
protocol definition is a unit. Everything that speaks the protocol needs it.

```yaml
unit: product
needs:
  soil-probe: {kind: hardware, summary: Capacitive soil moisture probe}
wiring:
  device.protocol-definition: protocol.ble-profile
  emulator.protocol-definition: protocol.ble-profile
  mobile.protocol-definition: protocol.ble-profile
  mobile.sensor-link: {real: device.ble-link, simulated: emulator.ble-link}
  device.soil-probe: soil-probe
```

## Code of the unit itself

A unit with children may also have code of its own.

- Code that only passes things through is expressed by the wiring:
  `own-port: child.port` or `child.need: own-need`.
- Code that uses ports of the children, such as a main program that calls
  three libraries, has no endpoint in the wiring, so the children's ports
  would look unused (`W3`). Put that code into a child unit, often named
  `app` or `main`, and wire it like any other child.
- A few lines of start-up code that only create the children and hold no
  logic may stay in the parent. `doc/architecture.md` says so.

## Shared definitions are units

When two siblings must agree on something, such as a wire format or a schema,
neither of them owns it. Put it in a unit of its own, let that unit provide
it, and let both siblings need it.

A definition that is used only by the children of one parent, and that has no
files, version or users of its own, may instead be a reference of the parent.
The children cite it in their `doc/context.md`.

## Using what a need provides

A unit refers to what it needs by the name of the need, for example "as
`link-profile` defines". It either states its own expectation, in a contract
of the need if precision matters, or says that it takes the provider's
definition as it is. In the second case it may use the provider's
identifiers, such as paths and field names, attributed to the need. The
parent is the place where both sides are visible; whoever writes or reviews
the wiring checks that they match (`C13` in
[rules-review.md](rules-review.md)). The generated context file of a
provider lists the contracts of the needs it serves.

## Limits

- A need has one provider at a time. A set of simultaneous providers, such as
  plug-ins, is modelled as one port of a unit that owns the collection.
- A need that is used deep in the tree is declared at every level it passes
  through. That is explicit and costs a line per level. Keep such chains
  short, and do not declare as needs what
  [manifest.md](manifest.md) says is not one.
- The checker compares manifests with each other. It does not check that the
  code only uses what is wired.
