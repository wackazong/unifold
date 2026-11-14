# Write a scenario

1. Choose the lowest unit that contains every unit the story names; a hop to a need of the root belongs to the root.
2. Under `scenarios` in its manifest, from [unifold.template.yaml](../assets/unifold.template.yaml): `summary`, `source`, `given`, `hops`, `expect`. Do not name the scenario like a part of a connection of its unit.
3. Write one hop per step, in the order a reader follows the story: `caller -> target.part`, units by their path from the holding unit, a capability or need of the holding unit bare. Every part must be an operation or event of the contract of the connection the hop uses; where two connections share the part, write `target.capability.part`. Write a hop in the direction of its part: the consumer calls an operation, the provider raises an event.
4. Add a note after `: ` where a reader needs it: what is passed, what comes back, or that a step repeats. Keep it short; the detail is in the contract and its examples. Quote a note that contains `: ` or ` #`, or starts with `[` or `{`.
5. A story that a child already tells is included as `child.scenario`, or `caller -> child.scenario` where the child's capability has several users at this level. Write what holds before the story starts under `given`, as sentences.
6. Run `check`. A hop that does not resolve means a missing connection, a missing part or a wrong cut: fix the manifests or the contract, never the story. Look at the result in the explorer, `unifold explore`.
7. [Finish](../SKILL.md#4-finish).
