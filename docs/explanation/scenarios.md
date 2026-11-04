# Scenarios and contracts in practice

How scenarios and the contracts of connections work in a map. [wiring.md](wiring.md) explains the wiring itself.

## Scenarios

A scenario is a path through the software. A scenario tells one story as the chain of calls it causes, in the manifest of a unit under `scenarios`. Each hop is `caller -> target.part(input): result`. A unit is named by its path from the holding unit; a capability or need of the holding unit is named bare:

```yaml
scenarios:
  open:
    summary: The host opens a session
    source: proto §5
    given:
      - transport.transport: idle
    hops:
      - host -> session.open(): ok
      - session -> transport.send([00]): ok
      - transport/serial -> uart.write([1F 00]): 2 bytes written
    expect: one frame 1F 00 on the line
```

A path along a single connection is a scenario too, held by the unit that wires the connection. How the connection is used in general is `## Use` of its contract, in words. Every scenario follows the `## States` of the contracts it uses: `given` sets the state a connection starts in, every hop must be allowed in the current state, and the checker follows each connection from hop to hop ([contracts.md](../references/contracts.md#states)). A path that a connection does not allow is an error of the map, found before anyone writes code.

A hop is written as the call happens at runtime. For a command or a query the consumer calls: `session -> transport.send([00])`. For an event or a callback the provider calls: `uart -> transport/serial.bytes-arrived([1F])`, or a plug-in's `transliterate` that the core calls. Who depends on whom is in the wiring; the hop only says who calls.

| Hop, for a command or query | Resolves through | The part is looked up in |
|---|---|---|
| `unit -> other-unit.part` | A need of the caller, followed up and down until the target provides for it, at whatever level | the contract of that need |
| `capability -> unit.part` | The capability of the holding unit, followed down to the target that implements it | the contract of that capability |
| `unit -> need.part` | A need of the caller, passed up until it reaches that need of the holding unit | the contract of that need |
| `capability -> need.part`, in a unit without children | Nothing: the capability's implementation uses the need | the contract of that need |

For an event or a callback, read the table with caller and target exchanged: `other-unit -> unit.part` resolves through a need of the target. Three more items may stand among the hops. `parallel` holds two or more lists of hops that run at the same time. `repeat` holds hops that run until a result, or a number of times:

```yaml
    hops:
      - session -> transport.receive(OPEN_TIMEOUT_MS): timeout
      - repeat:
          until: timeout
          hops:
            - transport/serial -> uart.read(64, 50): "[]"
      - parallel:
          - - ingest -> plants.reading-accepted(r)
          - - ingest -> alerts.reading-accepted(r)
```

And `<child>.<scenario>`, or `<caller> -> <child>.<scenario>` where the child's capability has several users at this level, includes a scenario of a child: its hops are rewritten to the names of this level, a child's own capability becomes its user, and a child's need becomes whatever this unit wires it to. A story is then told once per level: each level names its own children and includes their scenarios for the rest. `unifold scenario` shows one level, with each include as one step; `--expand` draws the whole. An event is asynchronous: the call that raised it has returned before the subscribers run, so the upload is answered before history and evaluation see the reading. An event from a unit outside the open calls, such as a sensor stick that advertises while the app searches, arrives during them.

The contract of a connection is one document at every level, so the part is found wherever the hop is written. A name that is both a unit below and a capability or need of the holding unit is an error that asks for a rename. Where two connections between the same two units have the part, the hop names the capability: `plant-lookup.thresholds.lookup`. A scenario belongs to the lowest unit that contains every unit it names; a hop to a need of the root belongs to the root. A story may cross levels, and its diagram is drawn end to end. Every wiring line should appear in a hop of some scenario: a connection that no story needs should not exist.

## Contracts of a connection

A connection carries information in some form: a wire format, a schema, a trait, a command line. The contract of the connection is the reference that defines that form, with examples, and both sides name it. It is not a protocol name: `http` says how the sides talk, the contract says what they say. And it is not a schema file such as `openapi.yaml` or a `.proto`, even where code is generated from one: such a file stays with the code that uses it. The checker reports a connection whose two sides name different documents, or none.

A manifest never points into a sibling, so the contract of a connection between two children lives in the references of the unit that wires them, or higher: `docs/references/clock.md` of the parent, named as `../docs/references/clock.md` by both. A protocol that several parts implement, such as a radio profile served by a device and by its emulator, is such a document, not a unit: a unit holds code. A definition from outside the project, such as the API of a vendor, gets a reference of the root as well, which links the definition by its URL.

A capability that a parent passes through (`public-api: gateway.public-api`) appears in two manifests, each describing it at its own level, and names the same document at both: a reference of the parent, or of a unit above it. A parent that only passes a capability through adds nothing of its own to the summary. A format that travels inside another contract, such as a reading inside an upload, is a part of the contract that carries it, or a reference of its own where several contracts share it ([placement.md](../references/placement.md#what-belongs-where)).

## One contract, three readers

The provider reads the contract as what it must guarantee: every part with its signature, preconditions, result and errors, and the examples as its first tests. A consumer reads it as what it may rely on, and takes from `## Fake` the stand-in its own tests use. A reviewer reads it as the one place where a change to the connection shows: when the two sides disagree, one of them disagrees with this file.

A contract is a reference: it states the connection as it is and nothing else. When the connection changes, the change rewrites the parts it touches. The contract gives no reasons; a part may link the decision that settled it. It holds no notes about the work, such as what is still open or what a step added. It does not describe how the provider works inside; that is an explanation of the provider.
