# unifold 0.4: scenarios

Version 0.4. The third page of the standard, after [spec.md](spec.md) and [spec-wiring.md](spec-wiring.md); the terms and keywords of the first page apply here.

## 4. Scenarios

A scenario follows one story through the units: which unit calls which, over which connection, in which order. It does not model what happens inside a call; how a single connection is used, and the states a consumer can see, are in its contract ([contracts.md](contracts.md#use)).

```yaml
scenarios:
  open-a-session:
    summary: The host opens a session
    source: proto §5
    given:
      - the device is switched on
    hops:
      - host -> session.open
      - session -> transport.send: the payload 01, OPEN
      - transport -> uart.write: 1F 01 01 12
    expect: one frame 1F 01 01 12 on the line
```

A scenario MUST have `summary`, `hops` and `expect`. `source` is free text. `given` is optional; it MUST be a list of sentences, which no checker reads. The holding unit of a scenario is the unit whose manifest declares it. The name of a scenario MUST NOT be the name of a part of a connection of its holding unit.

### Hops

A hop is one item `caller -> target.part`, optionally followed by `: ` and a note.

- **Names.** A unit is named by the path of its folder from the holding unit, segments separated by `/`, or by the names of the units on the way where plain folders lie between. A capability or need of the holding unit is named bare. A name MUST NOT be both a unit below and a capability or need of the holding unit.
- **Direction.** A hop is written in the direction of its part: an operation from the consumer to the provider, an event from the provider to the consumer.
- **Note.** The note is free text that no checker reads, such as what is passed or what comes back. A note that contains `: ` or ` #`, or starts with `[` or `{`, is quoted, because YAML would read it otherwise.
- **Order.** The hops stand in the order in which a reader follows the story. A scenario says nothing about what runs at the same time or how often a step repeats; a note says it where it matters.

### Included scenarios

An item `<unit>.<scenario>`, or `<caller> -> <unit>.<scenario>`, includes a scenario of a unit below, with its hops rewritten to the names of this level: a unit gets the path of the included unit in front, a need of the included unit becomes its provider at this level, and a capability of the included unit becomes its user at this level. Where the capability has several users, the include names the caller.

A scenario SHOULD name only its own capabilities and needs and its direct children, and include the scenarios of the children for the rest.

### Rules

1. A hop MUST resolve, by rule 6 of [section 3](spec-wiring.md#3-wiring), to one connection between its two ends, in the direction its part allows: for an operation, from a need of the caller to a capability of the target, from a capability of the holding unit down to the target, or from a need of the caller up to a need of the holding unit; for an event, the same with caller and target exchanged. In a unit without children, a hop between a capability and a need of the unit says that the capability's implementation uses the need.
2. The part MUST be an operation or event of that connection's contract, which is one document at every level. Where two connections between the same two units have the part, the hop MUST name the capability of the provider: `target.capability.part`, also for an event, whose provider is the caller.
3. A scenario SHOULD be held by the lowest unit that contains every unit it names. An included scenario MUST exist in the unit named, and every hop of it MUST resolve at this level too.
4. Every wiring line of a unit SHOULD be used by a hop of a scenario: a hop that passes through the unit, or a hop of a child at the capability or need that the line connects. The rule is silent for a unit that no scenario passes through, and for a line that meets a need of the unit inside (`need: child.capability`): the unit's own code uses it, which no hop names.
