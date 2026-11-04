# Change a capability, a need, or a dependency in code

1. If your code starts to use another unit, declare the new need and wire it in the parent. If no sibling provides it, declare the need in the parent as well, pass it up (`unit.need: need`) and continue one level up. If the code of a unit with children starts to use one of its children, declare a need in that unit and wire it in its own wiring: `need: child.capability`. The tool does not read code: keeping the map in step with it is part of the change.
2. If a capability changes, change the contract that both sides name and the manifest: the part's signature, its examples, and `## Fake` if the stand-in changes. Rewrite each part to the new state; do not add a sentence about the change.
3. Run `unifold capability PATH NAME` and read both sides of every connection. The provider must still cover what each need expects.
4. If you renamed an entry, search the unit's files for the old name.
5. If the change had real alternatives, record a decision ([record-a-decision.md](record-a-decision.md)).
6. [Finish](../SKILL.md#4-finish).
