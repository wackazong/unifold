# Wiring in practice

The rules of wiring are in the [standard](../references/unifold/spec.md), section 3. This chapter
shows how to use them: what to declare, how to name it, and the patterns
that come up in real repositories.

## Reading a line

```yaml
wiring:
  billing.clock: platform.clock
```

"The need `clock` of `billing` is met by the capability `clock` of
`platform`." The key is the side that needs, the value the side that
provides. The unit holding the line is the one place where both sides are
visible. `billing` itself never says who supplies its clock.

Seen from inside a unit, its own capabilities need an implementation, and
its own needs are available. That is why an own capability stands on the
key side and an own need on the value side.

## What is a need and what is not

Declare a need when another unit of the project provides the thing, when a
stand-in can replace it, or when it is an external system that the project
depends on by contract.

Do not declare a need for what every unit of that sort has anyway: the
language runtime, the standard library, the operating system, packages that
the build tool fetches from a registry, logging.

## Names

- Name a need after what is needed, in the words of the unit that has it:
  `clock`, `cart-store`, `matcher`. Not after who provides it today.
- Name a capability after what it offers, not after a technology.
- A first map tends to name capabilities and needs after packages, because
  that is what the build files show ([requirements](requirements.md)). Rename
  them to roles as soon as you know better; the comparison with code works
  per pair of units, not by name.
- In YAML, write a summary that contains `: ` or a comma inside `{...}` in
  quotes. The short form `name: summary text` on a line of its own avoids
  most of these cases.

## Passing a need up

A need that no sibling can meet goes to the parent, and from there upward
until a unit can meet it or the root states it as a need of the project.

```yaml
# services/unifold.yaml
summary: The backend services
needs:
  clock: A time source
# no wiring line: the need `clock` of every child is passed up by name
```

If the unit declares a need with the same name as a child's need, the two
are connected without a line. `unifold show` marks such a connection as
"(passed up by name)". Write an explicit line when the names differ
(`alerts.push: push-service`) or when one child should get a different
provider. An explicit line always wins.

## Several children, one provider

When several children need the same thing from one provider, every child
gets its own line; there is no wildcard:

```yaml
wiring:
  cart.api-definition: protocol.schema
  checkout.api-definition: protocol.schema
  shipping.api-definition: protocol.schema
```

The repetition is the point: the wiring lists every connection inside the
unit, and adding a child cannot change one without a change to a manifest.
Where the children use one name for what is the same for everybody,
declaring that need in the parent costs no line at all: every child passes
it up by name, and a diagram lists a need that three or more children pass
up below the picture, under "Shared connections, not drawn".

## Alternatives and stand-ins

```yaml
wiring:
  test-rig.device-under-test:
    real: device.ble-link
    simulated: emulator.ble-link
```

A stand-in, such as an emulator, a fake or an in-memory store, is a
provider like any other. The first alternative is the default. Use the
same names for all needs that switch together.

unifold does not say which alternative a build or deployment uses. That
stays in the build or deployment files. An alternative that does less than
the need expects is not an alternative; it is another capability.

When alternatives implement one shared definition, each provider says so:

```yaml
# regex/unifold.yaml
capabilities:
  matcher:
    summary: Regular expression search
    conforms-to: matcher-trait
needs:
  matcher-trait: The interface every matcher implements
```

## Adapters

If a need and its provider state different kinds, for example `library`
and `http`, the checker reports it. Usually a part is missing: an adapter,
which is a unit that needs the one and provides the other. Do not change
the kind of the need to make the finding go away.

## Shared definitions are units

When two siblings must agree on a wire format or a schema, neither owns it.
Put it in a unit of its own that provides it, and let both need it. Then a
`contract` in any unit MAY simply point at the one shared file, for example
`contract: ../../protos/demo.proto`. Copies of a definition per unit drift
apart without anybody noticing.

## A capability implemented by a child

```yaml
capabilities:
  public-api: Upload readings and query plants
wiring:
  public-api: gateway.public-api
```

The capability then appears in two manifests. Each describes it at its own
level. A parent that only passes a capability through adds nothing of its
own to the summary and keeps no second contract.

## Code of the unit itself

A unit with children MAY have code of its own, for example a main program
that calls three libraries. That code may use anything below the unit, and
the comparison with code accepts it without a wiring line. A capability of a
child that only this code uses is reported as unused, unless an observed
dependency shows the use ([rules](../references/unifold/rules.md)).

The other direction needs a line. When a child depends on code of the unit
above it, the child declares a need, and the parent names that code as the
provider: a plain folder (`./folder`), or `./` for the unit itself.

```yaml
wiring:
  plugin.host-api: ./        # the code of this unit itself
```

The checker lists such lines as information: they mark code that has no
manifest yet. If that code is more than start-up code, give it a folder
and a manifest of its own and wire it like any other child. unifold does
not ask you to move code.

## Optional parts and test-only dependencies

- A need behind a feature flag is `optional: true`. It MAY be wired anyway.
- A dependency that only tests use, such as a Cargo dev-dependency or an
  import in a test file, needs no need and no connection. The tool lists
  it with a kind of its own that ends in `-dev` (`cargo-dev`), and it
  counts as observed: if you do declare and wire it, there is no warning.
  In a list of your own, give such an entry a `kind` that ends in `-dev`.

## Services and external systems

For a set of services in one repository:

- Each service folder is a unit. A folder such as `src/` that only groups
  them stays plain.
- A database or a queue with no folder of its own is either a need of the
  root (somebody outside operates it) or a capability of the unit whose
  files define it, such as a deployment folder.
- Calls between services are not in any build file. Give the checker a
  list of observed calls, taken for example from service addresses in the
  deployment files or from client stubs ([tool](../references/unifold/tool.md)).
- With a flat set of services, all wiring is in one manifest, and every new
  call between two services changes it. That manifest is the map of the
  system; expect it to be the file with the most changes.
