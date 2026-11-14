# unifold 0.4: documents, checks and conformance

Version 0.4. The fourth page of the standard, after [spec.md](spec.md), [spec-wiring.md](spec-wiring.md) and [spec-scenarios.md](spec-scenarios.md); the terms and keywords of the first page apply here.

## 5. Documents

Every unit MUST have a `README.md`: what it is for, and why it is built this way. What can be relied on is in the contracts that its manifest names; their body is defined in [contracts.md](contracts.md) and [contract-parts.md](contract-parts.md). Everything else written about a unit lives in its `docs/`, sorted by kind, as [documents.md](documents.md), [placement.md](placement.md), [writing.md](writing.md) and [decision-records.md](decision-records.md) say. The target of a relative link in a hand-written document MUST exist, with its anchor, inside the project, to which a nested project does not belong.

A checker reads links, headings, front matter and length; in a contract the `Carried by:` line of the header, the `Kind:`, `Pre:`, `Result:`, `Errors:`, `Examples:`, `When:` and `Delivery:` lines of a part, the names in code font under `Errors:`, whether a fenced block exists under a part heading and which types of the contract it names, the columns and the `Case` names of the examples table and whether it has a row, and the columns of the `## Qualities` table; in a decision its file name and front matter. It reads nothing else inside a fenced block and judges no sentence. This is the one list; the other chapters link to it.

## 6. What a checker guarantees

A conforming checker reads a project, changes nothing, and reports findings, each with a severity:

| Severity | The finding is |
|---|---|
| `error` | What makes the map inconsistent. |
| `warn` | What makes a map better but is not needed for consistency. |
| `info` | A notice that breaks no rule, such as an operation that no scenario uses. |

[rules.md](rules.md) lists the findings of the reference checker one by one, each with an id, its severity and its fix; a conforming checker MUST report at least these, with the same severity. A rule of the standard that no finding covers, such as whether a unit holds code, is for the people who write and review the map.

No error means consistent, not correct: no checker reads the code, and none judges whether a text is true. Reference tool: [tool.md](tool.md).

## 7. Generated files

Generated files are written from the manifests, the decisions and the skills, and MUST NOT be edited by hand. Every generated file starts with a comment that begins with `<!-- unifold:generated`, after its front matter where it has one; the comment counts only at a path the generator writes.

| File in the unit | Shows | Written for |
|---|---|---|
| `docs/decisions/index.md` | The decisions of the unit, with status and date. | Units that have decisions. |
| `AGENTS.md` | Where the documents and skills of the root are, for coding agents, and the unifold block with the index of units. | The root only. |

- Generated links are URL-encoded.
- Generated files MUST be committed, and kept current with every change to what they show. A checker cannot see a commit; it reports a generated file that is missing, out of date, or ignored by version control.
- A generated file that the generator no longer writes MUST be removed, and the `AGENTS.md` of the root MUST be the generated one. Where the stub folders exist, the skill stubs are generated files too, with the names and the text that [agents.md](agents.md#where-skills-are-found) gives them.

Diagrams are not files of the project. A tool draws them on demand from the manifests and the contracts: the component diagram of a unit with children, the sequence diagram of a scenario and the state diagram of a contract ([tool-output.md](tool-output.md)).

## 8. Nested projects

A folder below the root whose manifest has the key `unifold` is the root of a nested project: a separate project, checked on its own. The outer project does not treat it as a child, and nothing is wired to it.

## 9. Conformance

- A project conforms to unifold 0.4 when a conforming checker reports no error for it. Warnings do not break conformance. A conforming project MAY say "This repository follows unifold 0.4".
- A tool conforms when it accepts and rejects the same manifests as the standard, connects needs as [section 3](spec-wiring.md#3-wiring) says, resolves hops as [section 4](spec-scenarios.md#4-scenarios) says, and reports the findings of section 6. [tool.md](tool.md) says how to test another implementation. A tool of version 0.4 reads version 0.4 only.
