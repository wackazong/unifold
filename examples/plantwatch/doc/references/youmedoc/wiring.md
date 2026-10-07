# Wiring

A unit declares what it needs. It does not say who supplies it. The parent
unit decides that in the `wiring` map of its [manifest](manifest.md).

```yaml
wiring:
  <need>: <provider>
```

The need is the key. The provider is the value. Read each line as "this need
is met by that provider".

## Endpoints

Both sides are endpoints. An endpoint is either a port of a direct child,
written `child.port`, or a port of the unit itself, written as the bare port
name.

| Key (the need) | Value (the provider) | Meaning |
|---|---|---|
| `child.need` | `sibling.port` | A child's need is met by another child |
| `child.need` | `own-need` | A child's need is passed up: it is met by whatever meets this unit's own need |
| `own-port` | `child.port` | A port this unit provides is implemented by a child |

Seen from inside a unit, its own provided ports are things that need an
implementation, and its own needs are things that are available. That is why
an own provided port stands on the key side and an own need on the value side.

Not allowed:

- `own-port: own-need`. A unit that only passes something through has no
  reason to list it.
- A child that provides for its own need.
- An endpoint that reaches into a grandchild, such as `a.b.port`. If a parent
  needs something from deeper down, the child MUST provide it as a port of
  its own and delegate it inward.

## Alternatives

A need may have several possible providers. Write them as a list:

```yaml
wiring:
  test-rig.device-under-test: [device.ble-link, emulator.ble-link]
```

The list means: any one of these can meet the need; which one is active
depends on configuration. It does not mean that all are used at once. Diagrams
draw alternatives with dashed arrows.

## What the checker verifies

| Check | Result |
|---|---|
| Every endpoint names an existing child and an existing port on the correct side | error if not |
| Every need of every child is a key in the parent's wiring, unless it is `optional` | error if not |
| Every provided port of every child is the value of at least one line | warning: provided but not needed |
| Need and provider have the same `kind` | warning if they differ |
| An own need of a unit with children is passed to at least one child | info |
| An own provided port of a unit with children is delegated to a child | info |

The two info results are not faults. A unit with children may also have code
of its own that uses a need or implements a port.

The needs of the root unit have no parent. They are the external dependencies
of the project and are never wired.

## The arrow means "needs"

A wiring line records a dependency. It does not record the direction in which
data flows. A unit that subscribes to events *needs* the event stream; the
publisher *provides* it. A unit that calls an HTTP API *needs* it. Generated
diagrams draw every arrow from the need to the provider.

## Examples

### Libraries in one program

```yaml
unit: app
wiring:
  storage.clock: platform.time-api
  api.store: storage.kv-api
```

### Microservices

Services publish and subscribe through a message bus that another unit
operates. The bus is a need of both sides. The event stream itself is a port
of the publisher.

```yaml
unit: cloud
provides:
  public-api: {kind: http, summary: Upload readings and query plants}
needs:
  push-service: {kind: http, summary: Delivers a notification to a phone}
wiring:
  public-api: gateway.public-api          # delegated to a child
  gateway.ingest: ingest.ingest-api       # sibling to sibling
  alerts.readings: ingest.reading-events  # subscriber needs the publisher's stream
  ingest.bus: platform.event-bus
  alerts.bus: platform.event-bus
  alerts.push: push-service               # passed up to this unit's own need
```

### A product made of several components

A device, an emulator of the device, a test rig and a mobile app share one
protocol. The protocol definition is a unit. Everything that speaks the
protocol needs it. The test rig can run against the device or the emulator.

```yaml
unit: product
needs:
  soil-probe: {kind: hardware, summary: Capacitive soil moisture probe}
wiring:
  device.protocol-definition: protocol.ble-profile
  emulator.protocol-definition: protocol.ble-profile
  mobile.protocol-definition: protocol.ble-profile
  mobile.sensor-link: [device.ble-link, emulator.ble-link]
  test-rig.device-under-test: [device.ble-link, emulator.ble-link]
  device.soil-probe: soil-probe
```

## Code of the unit itself

A unit with children may also have code of its own. Two cases:

- The code only passes things through. Then the wiring says so:
  `own-port: child.port` or `child.need: own-need`.
- The code uses ports of the children, for example a main program that calls
  three libraries. The wiring has no endpoint for "the unit's own code", so
  the children's ports would look unused (`W3`). Put that code into a child
  unit, often named `app`, `main` or `server`, and wire it like any other
  child.

A few lines of start-up code that only create the children and hold no logic
may stay in the parent. `doc/architecture.md` says so.

## Shared definitions are units

When two siblings must agree on something, such as a wire format, a schema or
a set of types, neither of them owns it. Put it in a unit of its own, let that
unit provide it, and let both siblings need it. This keeps the rule that a
unit never refers to a sibling.

A definition that is used only by the children of one parent, and that has no
files, version or users of its own, may instead be a reference of the parent.
The children cite it in their `doc/context.md`.

## Using what a need provides

A unit refers to what it needs by the name of the need, for example "as
`link-profile` defines". It states its own expectation and does not copy the
provider's text. A reader who wants the provider's side looks up the need in
the parent's wiring and reads the provider's `README.md`. The parent is the
place where both sides are visible; whoever writes or reviews the wiring
checks that they match (`C13` in [rules-review.md](rules-review.md)).

## Limits

- One need has one provider, or a list of alternatives. A need that is met by
  many providers at the same time, such as a set of plug-ins, cannot be
  expressed. Model the collection as one port of a unit that owns it.
- Wiring is static. It says what may be connected, not what is connected at a
  given moment.
- The checker compares manifests with each other. It does not check that the
  code only uses what is wired.
