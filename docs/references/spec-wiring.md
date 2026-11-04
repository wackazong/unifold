# unifold 0.4: wiring and scenarios

Version 0.4. The second page of the standard, after [spec.md](spec.md), whose terms and keywords apply here.

## 3. Wiring

`wiring` is a mapping. The key is a need, or a capability of the unit; the value is its provider: "this is met by that". A reference is either a bare name, an entry of the unit itself, or `child.name`, an entry of a direct child. A reference is split at its last dot. `child` is the child's folder name, or its path relative to the unit (`a/utils.matcher`); the path MUST be used when two children have the same folder name.

| Key | Value | Meaning |
|---|---|---|
| `child.need` | `sibling.capability` | Another child provides for the need. |
| `child.need` | `own-need` | The need is passed up: whatever meets this unit's own need meets it. |
| `own-need` | `child.capability` | A child provides for a need of this unit, for example of its own code. The need is met inside this unit. |
| `own-capability` | `child.capability` | A child implements a capability of this unit. |
| any key above | `{name: provider, ...}` | Named alternatives, each in the form for that key. The first is the default. |

1. **One level.** Wiring names only entries of the unit itself and of its direct children. It MUST NOT name anything deeper.
2. **Complete.** Every need of every child MUST be connected by a line of the parent, unless it is `optional` or the child meets it inside. Nothing is connected without a line: a need of the parent with the same name does not meet a need of a child.
3. **Sides.** A bare key that names both a need and a capability of the unit is an error. A need that the unit meets inside is not a provider, a need that a child meets inside MUST NOT be wired again, and a child never provides for its own need.
4. **Alternatives.** A need has one provider at a time. The build or the deployment decides which alternative is in use; this standard does not describe configurations. Every alternative MUST meet all that the need expects.
5. **Direction.** A connection records a dependency, not the direction in which data flows. A subscriber needs the stream; the publisher provides it.
6. **Final provider.** Who finally provides for a need, or uses a capability, is found by following needs up and capabilities down.
7. **Contract.** Both sides of every connection MUST name a contract, and the same one. So the contract of a connection lies in the unit that wires it, or higher.

## 4. Scenarios

A scenario is a path through the software. It follows one story through the units, and it follows the states that the contracts declare. How a single connection is used is `## Use` of its contract ([contracts.md](contracts.md#use)).

```yaml
scenarios:
  open:
    summary: The host opens a session
    source: proto §5
    given:
      - transport.transport: idle
      - the device is switched on
    hops:
      - host -> session.open(): ok
      - session -> transport.send([00]): ok
      - transport/serial -> uart.write([1F 00]): 2 bytes written
    expect: one frame 1F 00 on the line
```

A scenario has `summary`, `hops` and `expect`; `source` is free text, and `given` is optional. A hop is one item `caller -> target.part(input): result`, which maps the call to its result. The input in parentheses is optional. The result is required and is text, quoted where YAML would read a number or a word such as `yes`: `ok`, an error case of the part spelled as its `Errors:` names it, a value, or `= <case>`, the name of an example of the part, which gives the hop that example's input and expected result. A unit is named by the path of its folder from the holding unit, segments separated by `/`, or by the names of the units on the way where plain folders lie between; a capability or need of the holding unit is named bare. A name that is both a unit below and a capability or need of the holding unit is an error. A hop is written in the direction of the call: a command or query from the consumer to the provider, an event or callback from the provider to the consumer. The result of an event or callback MAY be left out.

The hops stand in the order in which the calls start. The hops that follow a command or query and whose caller is its target, or a unit below its target, happen inside it, until a hop whose caller lies further out; its result returns after the hops inside it. An event is asynchronous: when a unit raises one, the call it was handling has returned, and so has every call that waited for that return and does nothing more afterwards; a unit that handles an event keeps running while it raises others; an event from a unit outside the open calls arrives during them. A callback runs inside the call that triggers it. Three items of `hops` are not hops: `parallel`, a list of two or more lists of hops that run at the same time, in any order; `repeat`, a mapping with `hops` and `until: <result>` or `times: <n>`, whose hops run again and again; and `<unit>.<scenario>`, or `<caller> -> <unit>.<scenario>`, which includes a scenario of a unit below, with its hops rewritten to the names of this level: a unit of the included scenario gets the path of the included unit in front, a need of the included unit becomes its provider at this level, and a capability of the included unit becomes its user at this level; where it has several users, the include names the caller. A scenario of a unit that has the name of a part of one of its connections is an error. A scenario SHOULD name only its own capabilities and needs and its direct children, and include the scenarios of the children for the rest.

1. A hop MUST resolve, by rule 6 of section 3, to one connection between its two ends, in the direction its part allows: for a command or query, from a need of the caller to a capability of the target, from a capability of the holding unit down to the target, or from a need of the caller up to a need of the holding unit; for an event or callback, the same with caller and target exchanged. In a unit without children, a hop between a capability and a need of the unit says that the capability's implementation uses the need.
2. The part MUST be a command, query, event or callback of that connection's contract, which is one document at every level. Where two connections between the same two units have the part, the hop names the capability: `target.capability.part`; without it the hop is an error.
3. A scenario SHOULD be held by the lowest unit that contains every unit it names. An included scenario MUST exist in the unit named, and every hop of it MUST resolve at this level too.
4. An item of `given` is a sentence, which no checker reads, or `connection: state`. The connection is named as a hop names its target: `unit.capability`, or a need of the holding unit. Its contract MUST have `## States`, and the state MUST be one of them.
5. A connection whose contract has `## States` starts in the state that `given` names, or else in the start state of the contract. Every hop over it MUST be allowed in its current state with its result, and leads to the next state that the table names ([contracts.md](contracts.md#states)). The hops of a `repeat` are followed twice, so that a round can follow a round, and the branches of a `parallel` one after the other.
6. A hop MUST agree with the examples of its part: a result `= <case>` names an example that exists, and a hop whose input is the `Input` of an example has that example's `Expected` as its result. A result that is not `ok` and is spelled like an error case, but not exactly, is reported.
