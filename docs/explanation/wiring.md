# Wiring in practice

The rules of wiring are in the [standard](../references/spec.md), section 3. This chapter shows how to use them: what to declare, how to name it, and the patterns of real repositories.

## Reading a line

```yaml
wiring:
  billing.clock: platform.clock
```

"The need `clock` of `billing` is met by the capability `clock` of `platform`." The key is the side that needs, the value the side that provides. The unit holding the line is the one place where both sides are visible. `billing` itself never says who supplies its clock.

## What is a need and what is not

Declare a need when another unit of the project provides the thing, when a stand-in can replace it, or when it is an external system that the project depends on by contract.

Do not declare a need for what every unit of that sort has anyway: the language runtime, the standard library, the operating system, packages that the build tool fetches from a registry, logging.

## Names

- Name a need after what is needed, in the words of the unit that has it: `clock`, `cart-store`, `matcher`. Not after who provides it today.
- Name a capability after what it provides, not after a technology.
- A first map tends to name capabilities and needs after packages, because that is what the build files show. Rename them to roles as soon as you know better.
- In YAML, write a summary that contains `:` or a comma inside `{...}` in quotes. The short form `name: summary text` on a line of its own avoids most of these cases.

## Passing a need up

A need that no sibling can meet goes to the parent, and from there upward until a unit meets it or the root states it as a need of the project. Each step is one line, `child.need: need`, and the names may differ: `alerts.push: push-service`. Nothing connects by an equal name; the check reports the missing line.

## Several children, one provider

When several children need the same thing from one provider, every child gets its own line; there is no wildcard:

```yaml
wiring:
  cart.clock: platform.clock
  checkout.clock: platform.clock
  shipping.clock: platform.clock
```

The repetition is the point: the wiring lists every connection inside the unit, and adding a child cannot change one without a change to a manifest. Where three or more children pass a need up to the same need of the parent, the diagram lists them once below the picture, under "Shared connections, not drawn".

## Alternatives and stand-ins

```yaml
wiring:
  test-rig.device-under-test:
    real: device.ble-link
    simulated: emulator.ble-link
```

A stand-in, such as an emulator, a fake or an in-memory store, is a provider like any other. The first alternative is the default. Use the same names for all needs that switch together.

unifold does not say which alternative a build or deployment uses. That stays in the build or deployment files. An alternative that does less than the need expects is not an alternative; it is another capability.

Alternatives implement one definition, so every alternative names the same contract as the need:

```yaml
# search/unifold.yaml
needs:
  matcher:
    summary: Finds a pattern in text
    contract: ../docs/references/matcher.md
# regex/unifold.yaml
capabilities:
  matcher:
    summary: Regular expression search
    contract: ../docs/references/matcher.md
```

## Adapters

If a need and its provider state different kinds, for example `library` and `http`, the checker reports it. Usually a part is missing: an adapter, which is a unit that needs the one and provides the other. Do not change the kind of the need to make the finding go away.

## Kinds of units

`kind` on a unit is free text, and three values carry rules:

| Kind | Meaning | Rule |
|---|---|---|
| `logic` | A pure calculation. No input or output, no memory between calls. Takes time and randomness as parameters. | Logic throughout: every child is a `logic` unit, the final provider of each need is a `logic` unit, and no need reaches a need of the root. |
| `stateful` | Keeps state, such as a session or a state machine. | May need anything. |
| `adapter` | The one unit that talks to one external system, a need of the root. | The final provider of none of its needs is an `adapter`. |

A need of the root is finally reached only by adapters, unless it is marked `platform: true`. That mark is for a service of the host such as time or randomness, which is not an external system and whose contract describes a controllable fake, such as a clock that tests move forward. A unit that states no kind is not judged by this rule. A unit with children carries a kind too; it says what the box is to its parent's wiring. A `logic` composite has only `logic` children; a composite that holds state anywhere is `stateful`; one that exists to wrap one external system is an `adapter`. The root needs no kind but may state one.

What the kinds give: a logic unit can be tested without any fake, so its tests are the cheapest and its examples the most trustworthy; an adapter is the only place where an external protocol lives, so an integration harness puts fakes at the needs of the root and nowhere else; a stateful unit is where state machines live, so its `runtime.md` is where a reviewer looks for them. Any other value is allowed; the checker says so once, as information, and applies no rule.

## Scenarios

A scenario tells one story as the chain of calls it causes, in the manifest of a unit under `scenarios`. Each hop is `caller -> target.part`. A unit is named by its path from the holding unit; a capability or need of the holding unit is named bare:

```yaml
scenarios:
  open:
    summary: The host opens a session
    source: proto §5
    hops:
      - host -> session.open
      - session -> transport.send
      - transport/serial -> uart.write
    expect: one frame 1F 00 on the line
```

| Hop | Resolves through | The part is looked up in |
|---|---|---|
| `unit -> other-unit.part` | A need of the caller, followed up and down until the target provides for it, at whatever level | the contract of that need |
| `capability -> unit.part` | The capability of the holding unit, followed down to the target that implements it | the contract of that capability |
| `unit -> need.part` | A need of the caller, passed up until it reaches that need of the holding unit | the contract of that need |
| `capability -> need.part`, in a unit without children | Nothing: the capability's implementation uses the need | the contract of that need |

The contract of a connection is one document at every level, so the part is found wherever the hop is written. A name is looked up as a descendant first, then as a capability or need of the holding unit; a name that is both is an error that asks for a rename, as are two connections between the same two units whose contracts both have the part. A scenario belongs to the lowest unit that contains every unit it names; a hop to a need of the root belongs to the root. A story may cross levels, and its diagram is drawn end to end. Every wiring line should appear in a hop of some scenario: a connection that no story needs should not exist.

## Contracts of a connection

A connection carries information in some form: a wire format, a schema, a trait, a command line. The contract of the connection is the reference that defines that form, with examples, and both sides name it. It is not the kind: `http` says how the sides talk, the contract says what they say. And it is not a schema file such as `openapi.yaml` or a `.proto`, even where code is generated from one: such a file stays with the code that uses it. The checker reports a connection whose two sides name different documents, or none.

A manifest never points into a sibling, so the contract of a connection between two children lives in the references of the unit that wires them, or higher: `docs/references/clock.md` of the parent, named as `../docs/references/clock.md` by both. A protocol that several parts implement, such as a radio profile served by a device and by its emulator, is such a document, not a unit: a unit holds code. A definition from outside the project, such as the API of a vendor, gets a reference of the root as well, which links the definition by its URL.

A capability that a parent passes through (`public-api: gateway.public-api`) appears in two manifests, each describing it at its own level, and names the same document at both: a reference of the parent, or of a unit above it. A parent that only passes a capability through adds nothing of its own to the summary. A format that travels inside another contract, such as a reading inside an upload, is not a contract of its own: it is a reference that the context files of its users cite.

## A unit with code of its own

A unit with children MAY have code of its own, for example a main program that calls its libraries. What that code uses from a child is a need of the unit, wired in the unit's own wiring to the child's capability, `clock: platform.clock`; the standard shows the example. The unit above does not wire such a need, and at the root it is not a need of the project. A child's need of the same name still needs its own line, and it cannot be passed up to it.

The other direction is not modelled. When a child uses code of the unit above it, that code gets a folder with a manifest and a capability, and the child's need is wired to it like any other connection. A connection always joins two units; there is no line that names a folder.

## Optional needs

A need behind a feature flag is `optional: true`. It MAY be wired anyway. What only tests use, such as a fake or a test helper, is no need: declare a need for what the unit's code requires when it runs.

## Services and external systems

For a set of services in one repository:

- Each service folder is a unit. A folder such as `src/` that only groups them stays plain.
- A database or a queue with no folder of its own is either a need of the root (somebody outside operates it) or a capability of the unit whose files define it, such as a deployment folder.
- A call from one service to another is a need of the caller, wired to a capability of the callee. The contract is the API both sides name.
- With a flat set of services, all wiring is in one manifest, and every new call between two services changes it. That manifest is the map of the system; expect it to be the file with the most changes.
