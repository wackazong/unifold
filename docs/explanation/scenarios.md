# Scenarios and contracts in practice

How scenarios and the contracts of connections work in a map. [wiring.md](wiring.md) explains the wiring itself.

## Scenarios

A scenario tells one story as the steps between units, in the manifest of a unit under `scenarios`; the [standard](../references/spec-scenarios.md#4-scenarios) defines the form and shows one. A path along a single connection is a scenario too, held by the unit that wires the connection. How the connection is used in general is `## Use` of its contract, in words.

A scenario stays at the level of the design: which unit uses which connection, in which order. It does not model what happens inside a call, what runs at the same time or how often a step repeats; a note after the hop says it in words where a reader needs it. That keeps the stories short enough to read and to review, and it leaves the detail to the contracts and their examples, which the tests prove. What the checker does with a scenario is what matters most for the map: every hop must run along a connection that the wiring declares, so a story that needs a connection nobody declared is an error, found before anyone writes code.

A hop is written in the direction of its part. For an operation the consumer calls: `session -> transport.send`. For an event the provider raises it and the consumer receives it: `uart -> transport.bytes-arrived`. Who depends on whom is in the wiring; the hop only says in which direction the step goes.

| Hop, for an operation | Resolves through | The part is looked up in |
|---|---|---|
| `unit -> other-unit.part` | A need of the caller, followed up and down until the target provides for it, at whatever level | the contract of that need |
| `capability -> unit.part` | The capability of the holding unit, followed down to the target that implements it | the contract of that capability |
| `unit -> need.part` | A need of the caller, passed up until it reaches that need of the holding unit | the contract of that need |
| `capability -> need.part`, in a unit without children | Nothing: the capability's implementation uses the need | the contract of that need |

For an event, read the table with caller and target exchanged: `other-unit -> unit.part` resolves through a need of the target. A call that goes against the dependency, such as a plug-in that the core asks, is a connection of its own: the core needs the plug-in, and the plug-in provides it.

An included scenario of a child, `<child>.<scenario>`, lets a story be told once per level: each level names its own children and includes their scenarios for the rest. The explorer draws the whole story, each include as a shaded block, and folded, each include as one step.

The contract of a connection is one document at every level, so the part is found wherever the hop is written. A story may cross levels, and its diagram is drawn end to end. Every wiring line should appear in a hop of some scenario: a connection that no story needs should not exist.

## Contracts of a connection

A connection carries information in some form: a wire format, a schema, a trait, a command line. The contract of the connection is the reference that defines that form, with examples, and both sides name it. It is not a protocol name: `http` says how the sides talk, the contract says what they say. And it is not a schema file such as `openapi.yaml` or a `.proto`, even where code is generated from one: such a file stays with the code that uses it.

A manifest never points into a sibling, so the contract of a connection between two children lives in the references of the unit that wires them, or higher: `docs/references/clock.md` of the parent, named as `../docs/references/clock.md` by both. A protocol that several parts implement, such as a radio profile served by a device and by its emulator, is such a document, not a unit: a unit holds code. A definition from outside the project, such as the API of a vendor, gets a reference of the root as well, which links the definition by its URL.

A capability that a parent passes through (`public-api: gateway.public-api`) appears in two manifests, each describing it at its own level, and names the same document at both: a reference of the parent, or of a unit above it. A parent that only passes a capability through adds nothing of its own to the summary.

## One contract, three readers

The provider reads the contract as what it must guarantee: every part with its signature, preconditions, result and errors, and the examples as its first tests. A consumer reads it as what it may rely on, and takes from `## Fake` the stand-in its own tests use. A reviewer reads it as the one place where a change to the connection shows: when the two sides disagree, one of them disagrees with this file.
