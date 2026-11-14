# Wiring in practice

The rules of wiring are in the [standard](../references/spec-wiring.md), section 3. This chapter shows how to use them: what to declare, how to name it, and the patterns of real repositories. [scenarios.md](scenarios.md) shows how scenarios and contracts work in a map.

## Reading a line

```yaml
wiring:
  billing.clock: platform.clock
```

"The need `clock` of `billing` is met by the capability `clock` of `platform`." The key is the side that needs, the value the side that provides. The unit holding the line is the one place where both sides are visible. `billing` itself never says who supplies its clock.

## What is a need and what is not

Declare a need when another unit of the project provides the thing, when a stand-in can replace it, or when it is an external system that the project depends on by contract.

Do not declare a need for what every unit of that sort has anyway: the language runtime, the standard library, the operating system, packages that the build tool fetches from a registry, logging.

At the root, a capability is an interface that code outside the project is written against or that a person uses, such as a library API, an HTTP API, a command line or a UI, and a need is something outside that the project's code uses, such as a device, a service or the platform. A project that nobody programs against or uses directly, such as a controller that reads sensors and switches a relay, has needs and no capability. Its scenarios start where a unit reacts to a need, as the scenario `start-and-first-reading` of `device` in [plantwatch](../../examples/plantwatch/README.md) wakes its sampling with `hal -> sampling.alarm`, and what it does is observed through the fakes of its needs.

## Names

- Name a need after what is needed, in the words of the unit that has it: `clock`, `cart-store`, `matcher`. Not after who provides it today.
- Name a capability after what it provides, not after a technology.
- A first map tends to name capabilities and needs after packages, because that is what the build files show. Rename them to roles as soon as you know better.

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

When a need is met in another form than the one the unit expects, for example over HTTP instead of as a library call, a part is usually missing: an adapter, a unit that needs the one form and provides the other. The two forms are two contracts, so the checker reports the connection whose sides name different contracts. Do not change the contract of the need to make the finding go away.

## Kinds of units

`kind` on a unit is optional free text. Three values carry rules, which the [standard](../references/spec-wiring.md#kinds-of-units) states; this is what they mean:

| Kind | Meaning |
|---|---|
| `logic` | A pure calculation. No input or output, no memory between calls. Takes time and randomness as parameters. |
| `stateful` | Keeps state, such as a session or a state machine. |
| `adapter` | The one unit that talks to one external system, a need of the root. |

A unit that states no kind is not judged. The mark `platform: true` keeps a service of the host out of the rule for adapters: its fake is one that tests control, such as a clock that tests move forward. A unit with children may carry a kind too; it says what the box is to its parent's wiring. A `logic` composite has only `logic` children; a composite that holds state anywhere is `stateful`; one that exists to wrap one external system is an `adapter`.

What the kinds give: a logic unit can be tested without any fake, so its tests are the cheapest and its examples the most trustworthy; an adapter is the only place where an external protocol lives, so an integration harness puts fakes at the needs of the root and nowhere else; a stateful unit is where state machines live, so its `runtime.md` is where a reviewer looks for them.

## A unit with code of its own

A unit with children may have code of its own, for example a main program that calls its libraries. What that code uses from a child is a need of the unit, wired in the unit's own wiring to the child's capability, `clock: platform.clock`; the standard gives the form, `own-need: child.capability`. The unit above does not wire such a need, and at the root it is not a need of the project. A child's need of the same name still needs its own line, and it cannot be passed up to it.

The other direction is not modelled. When a child uses code of the unit above it, that code gets a folder with a manifest and a capability, and the child's need is wired to it like any other connection. A connection always joins two units; there is no line that names a folder.

## Optional needs

A need behind a feature flag is `optional: true`. It may be wired anyway. What only tests use, such as a fake or a test helper, is no need: declare a need for what the unit's code requires when it runs.

## Services and external systems

For a set of services in one repository:

- Each service folder is a unit. A folder such as `src/` that only groups them stays plain.
- A database or a queue with no folder of its own is either a need of the root (somebody outside operates it) or a capability of the unit whose files define it, such as a deployment folder. A stream of events that rides on the queue has a contract of its own, `Carried by:` the queue's contract.
- Configuration is a need, with the settings as the parts of its contract ([placement.md](../references/placement.md#what-belongs-where)). `runs-as` in the manifest says which units are processes, jobs or libraries.
- A call from one service to another is a need of the caller, wired to a capability of the callee. The contract is the API both sides name.
- With a flat set of services, all wiring is in one manifest, and every new call between two services changes it. That manifest is the map of the system; expect it to be the file with the most changes.
