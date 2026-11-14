# unifold 0.4: wiring

Version 0.4. The second page of the standard, after [spec.md](spec.md), whose terms and keywords apply here.

## 3. Wiring

`wiring` is a mapping. The key is a need, or a capability of the unit; the value is its provider: "this is met by that". A reference is either a bare name, an entry of the unit itself, or `child.name`, an entry of a direct child. A reference is split at its last dot. `child` is the child's folder name, or its path relative to the unit (`a/utils.matcher`); the path MUST be used when two children have the same folder name. A line MUST have one of these forms and name entries that exist:

| Key | Value | Meaning |
|---|---|---|
| `child.need` | `sibling.capability` | Another child provides for the need. |
| `child.need` | `own-need` | The need is passed up: whatever meets this unit's own need meets it. |
| `own-need` | `child.capability` | A child provides for a need of this unit, for example of its own code. The need is met inside this unit. |
| `own-capability` | `child.capability` | A child implements a capability of this unit. |
| any key above | `{name: provider, ...}` | Named alternatives, each in the form for that key. The first is the default. |

1. **One level.** Wiring names only entries of the unit itself and of its direct children. It MUST NOT name anything deeper.
2. **Complete.** Every need of every child MUST be connected by a line of the parent, unless it is `optional` or the child meets it inside. Nothing is connected without a line: a need of the parent with the same name does not meet a need of a child.
3. **Sides.** A bare key MUST NOT name both a need and a capability of the unit. A need that the unit meets inside MUST NOT be a provider, a need that a child meets inside MUST NOT be wired again, and a child MUST NOT provide for its own need.
4. **Alternatives.** A need has one provider at a time. The build or the deployment decides which alternative is in use; this standard does not describe configurations. Every alternative MUST meet all that the need expects.
5. **Direction.** A connection records a dependency, not the direction in which data flows. A subscriber needs the stream; the publisher provides it.
6. **Final provider.** Who finally provides for a need, or uses a capability, is found by following needs up and capabilities down.
7. **Contract.** Both sides of every connection MUST name a contract, and the same one. So the contract of a connection lies in the unit that wires it, or higher.
8. **Used.** Every capability of a child SHOULD be used: a line names it as the provider of a need, or as the implementation of a capability of the unit.
9. **No cycle.** The children of a unit SHOULD NOT need each other in a cycle.
10. **Status.** An `active` unit SHOULD NOT get a need from a provider that is `planned` or `deprecated`, unless the need is `optional`. Of named alternatives, the default counts.

### Kinds of units

`kind` in a manifest is free text. Three values carry rules about final providers (rule 6). Any other value carries none, and a unit that states no kind is not judged.

| Kind | What the unit is | Rule |
|---|---|---|
| `logic` | A pure calculation. | Every child SHOULD be a `logic` unit, and the final provider of every need SHOULD be a `logic` unit, so that no need reaches a need of the root. |
| `stateful` | A unit that keeps state. | None: it may need anything. |
| `adapter` | The one unit that talks to one external system. | The final provider of a need of an `adapter` SHOULD NOT be an `adapter`. |

A need of the root that is not marked `platform` is an external system. Only `adapter` units SHOULD finally reach it: a `logic` or `stateful` unit that does is reported. [wiring.md](../explanation/wiring.md#kinds-of-units) explains the kinds.

