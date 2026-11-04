# unifold 0.4: documents, checks and conformance

Version 0.4. The third page of the standard, after [spec.md](spec.md) and [spec-wiring.md](spec-wiring.md); the terms and keywords of the first page apply here.

## 5. Documents

Every unit MUST have a `README.md`: what it is for, and why it is built this way. What can be relied on is in the contracts that its manifest names; their body is defined in [contracts.md](contracts.md). Everything else written about a unit lives in its `docs/`, sorted by kind, as [documents.md](documents.md) and [writing.md](writing.md) say. A checker reads links, headings, front matter and length; in a contract the `Kind:`, `Pre:`, `Result:`, `Errors:` and `Examples:` lines of a part, the names in code font under `Errors:`, whether a fenced block exists under a part heading and which types of the contract it names, whether the examples table has a row, and the `Start:` line and the table of `## States`; in a decision its front matter. It reads nothing else inside a fenced block and judges no sentence. This is the one list; the other chapters link to it.

## 6. What a checker guarantees

A conforming checker reads a project, changes nothing, and reports findings with a severity: `error`, `warn` or `info`. An error is what makes the map inconsistent; everything that makes a map better but is not needed for consistency is a warning. It MUST report at least:

| Finding | Severity |
|---|---|
| A manifest that is not valid: not a YAML mapping, an unknown key, a wrong type, no `responsibility`; a root whose `unifold` is not the string `"0.4"`; `platform` outside a need of the root; a `not` that is not a list of one-line texts; an empty entry that no wiring line joins to exactly one other entry | error |
| A wiring line that [section 3](spec-wiring.md#3-wiring) does not allow, or that names a child, capability or need that does not exist | error |
| A need of a child that is not `optional`, not met inside the child, and not connected | error |
| A path in a manifest that does not exist, or lies where [section 2](spec.md#2-the-manifest) forbids; a name under `parts` that is no part of the contract | error |
| A scenario without `summary`, `hops` or `expect`; a command or query without a result, or a hop with a result that is not text; a `parallel` or `repeat` that is not formed as section 4 says; an included scenario that does not exist; a hop that does not resolve as [section 4](spec-wiring.md#4-scenarios) says, in the direction of the call, whose part is a type, or whose name is ambiguous | error |
| A hop whose result `= <case>` names no example of the part, or whose input is the `Input` of an example and whose result is not that example's `Expected` | error |
| An item of `given` that names no state of a contract with `## States`; a hop that the states of its connection do not allow | error |
| A `## States` table without a start state, or with a part, result or next state that the contract does not have, or with two rows for one step | error |
| A unit without `README.md`; a link in a hand-written document whose target does not exist, that leaves the project (a nested project included), or that is an absolute path | error |
| A side of a connection without a contract, or two sides that name different contracts | error |
| A decision whose file is not named `NNNN-short-title.md` with a number that is unique in the unit, whose status is not one of [decision-records.md](decision-records.md#decisions), whose `date` is not a date, that is `accepted` without `decision-makers`, that is `superseded by` a decision that does not exist, or that is `derived` without `derived-from` and `## Source says` | error |
| A generated file that is missing, ignored by version control, or differs from what the generator would write now; a generated file that the generator no longer writes; a hand-written file in `docs/diagrams/`; a stale skill stub where the stub folders exist | error |
| A `logic` or `adapter` unit that breaks its rule; a need of the root without `platform` that a `logic` or `stateful` unit finally reaches | warn |
| A contract without `## Use`, `## Parts` or `## Fake`; a part without a known `Kind:` or a fenced signature; a command or query without `Pre:`, `Result:`, `Errors:` and an examples table with the columns of [contracts.md](contracts.md#parts), a row, and case names that are unique in the part; a type defined twice within one subtree | warn |
| A hop whose result differs from an error case of its part only in case, or in `-` and `_` | warn |
| A `## Qualities` section that is not a table `Aspect \| Guarantee`; an event without `When:` and `Delivery:`, or with an examples table whose columns are not those of [contracts.md](contracts.md#parts) | warn |
| A wiring line of a unit that no hop of a scenario uses: neither a hop that passes through the unit nor a hop of a child at the capability or need the line connects | warn |
| A link in a hand-written document that goes sideways, into a unit that is neither above nor below ([placement.md](placement.md#where-a-file-may-point)) | warn |
| A hand-written document with more than 1,500 words, counted outside its front matter as the strings between spaces that contain a letter or a digit | warn |
| `responsibility: TODO`, `summary: TODO` | warn |
| A `README.md` without a `#` title first, without one paragraph after it or without `## Why`, or with a placeholder `<...>` of the template | warn |
| A skill folder without `SKILL.md`, or one whose front matter lacks `name`, equal to the folder name, or `description` | warn |

No error means consistent, not correct: no checker reads the code, and none judges whether a text is true. Reference tool: [tool.md](tool.md), [rules.md](rules.md).

## 7. Generated files

Diagrams and indexes are generated from the manifests and MUST NOT be edited by hand. A diagram is Markdown with a Mermaid chart and the same content as tables. The sequence diagram of a scenario and the state diagram of a contract are not files of the project: a tool draws them on demand ([tool.md](tool.md)). Every generated file starts with a comment that begins with `<!-- unifold:generated`; the comment counts only at a path the generator writes.

| File in the unit | Shows | Written for |
|---|---|---|
| `docs/diagrams/component.md` | The children of the unit, each with its responsibility, kind and `runs-as`, and the connections between them and with the unit's own needs. | Units that have children. |
| `docs/decisions/index.md` | The decisions of the unit, with status and date. | Units that have decisions. |
| `AGENTS.md` | Where the documents and skills of the root are, for coding agents, and the unifold block with the index of units. | The root only. |

- `diagrams: none` writes no diagram.
- An arrow points from what needs to what provides. A need of the unit to which three or more children pass up is listed once below the picture. A `planned` unit is marked.
- Generated links are URL-encoded.
- Generated files MUST be committed, and kept current with every change to what they show. A checker cannot see a commit; it reports a generated file that is missing, out of date, or ignored by version control.

## 8. Nested projects

A folder below the root whose manifest has the key `unifold` is the root of a nested project: a separate project, checked on its own. The outer project does not treat it as a child, and nothing is wired to it.

## 9. Conformance

- A project conforms to unifold 0.4 when a conforming checker reports no error for it. Warnings do not break conformance. A conforming project MAY say "This repository follows unifold 0.4".
- A tool conforms when it accepts and rejects the same manifests as the standard, connects needs as [section 3](spec-wiring.md#3-wiring) says, resolves hops as [section 4](spec-wiring.md#4-scenarios) says, and reports the findings of section 6. [tool.md](tool.md) says how to test another implementation. A tool of version 0.4 reads version 0.4 only.
