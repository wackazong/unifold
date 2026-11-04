# The design ideas behind unifold

How ports and adapters, domain-driven design, SOLID and test-first design show in the standard. [reasoning.md](reasoning.md) says where the parts of unifold come from and what it adds.

## Ports and adapters

| Idea | In unifold |
|---|---|
| A port that the application provides | An entry of `capabilities` |
| A port that the application requires, in its own terms | An entry of `needs`. It names the contract that it and its provider share. |
| Adapter | A unit of kind `adapter`: the one unit that talks to one external system, a need of the root ([0010](../decisions/0010-three-kinds-of-units-carry-rules.md)) |
| Pure domain logic | A unit of kind `logic`: no input or output, no memory between calls; time and randomness arrive as parameters, so its tests need no fake |
| Composition root | The `wiring` of the parent |
| Test double | The `## Fake` of a contract: a replay of its examples, or a simplified behaviour with faults, defined where both sides see it; or another provider as a named alternative |
| Two adapters for one port | Capabilities that name the same contract |

A unit that holds rules of the domain names its needs in the words of the domain. If such a need is met behind a network or a device, an adapter unit stands in between ([wiring](wiring.md)). The three well-known kinds make this checkable: a `logic` unit reaches no need of the root, and a need of the root is reached only by adapters, unless it is a `platform` service such as a clock.

## Domain-driven design

| Idea | In unifold |
|---|---|
| Bounded context | A unit with a glossary of its own, usually near the top of the tree |
| Ubiquitous language | The glossary of that unit |
| Context map | The generated diagrams; the wiring is the list of relationships |
| Published language | The contract of a connection, a document both sides name; a language that many share lives in the references of the unit above them |
| Customer and supplier | One contract for the connection: a change to it is a change for both sides, and the checker refuses a connection whose sides disagree |
| Shared kernel | A contract in the references of the parent, named by several children |
| Anticorruption layer | An adapter unit |

## SOLID

| Principle | Where it shows |
|---|---|
| Single responsibility | `responsibility` states the one thing the unit is responsible for, and `## Why` the one piece of knowledge it hides ([0015](../decisions/0015-the-manifest-stays-small.md)); `## Why` gives the reasons. A responsibility that needs "and" to join unrelated things suggests a split. |
| Open for extension | New behaviour arrives as a new unit or a new provider. The wiring changes; the users do not. |
| Substitution | Every alternative meets all that the need expects. |
| Interface segregation | Several narrow capabilities instead of one that every user depends on in full. |
| Dependency inversion | A unit depends on its needs, which it states itself. It never names a provider. |
| Acyclic dependencies | Children of one unit should not need each other in a circle. |

## Test first

- A guarantee names something that can be observed. "Fast" is not a guarantee; "answers within 200 ms for a batch of 500" is.
- A contract contains examples per part: inputs with expected results. They become the first tests of the provider, and they are the whole behaviour of a replay fake ([0003](../decisions/0003-one-contract-per-connection.md)).
- A scenario becomes an integration test: the real units wired together, fakes only at the needs of the root, and `expect` says what the test asserts.
- The order of work for a new capability is: example in the contract, failing test, code, then `status: active`. A pointer to tests was removed ([0013](../decisions/0013-from-design-to-code-brief-trace-and-named-tests.md)): nothing ran it.

## What the principles do not decide

They do not say how big a unit is, how deep the tree goes, or which folder is a unit. That stays a judgement. Fewer, well-chosen units are better than many: a unit costs attention every time its surroundings change.
