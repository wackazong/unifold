# unifold 0.3: the standard

Version 0.3. This page is the standard for manifests, wiring, scenarios and generated files; [documents.md](documents.md) and [writing.md](writing.md) are the standard for the documents of a unit; [contracts.md](contracts.md) explains contracts. MUST, MUST NOT, SHOULD and MAY are used as in [BCP 14](https://www.rfc-editor.org/info/bcp14). Examples are not normative.

## 1. Terms

| Term | Meaning |
|---|---|
| Unit | A folder that contains a file named `unifold.yaml`, its manifest. Nothing else makes a folder a unit. The unit's name is the folder's name. A unit SHOULD hold code that is built, run or deployed. A document is never a unit. |
| Root | The top unit of a project. Its manifest has the key `unifold`. |
| Project | The root and everything below it, except nested projects (section 8). |
| Plain folder | A folder that is not a unit. It belongs to the nearest unit above it. |
| Parent, child | The parent of a unit is the nearest unit above it; plain folders in between do not count. Siblings have the same parent. Ancestors are the parent, its parent, and so on; descendants are the reverse. |
| Capability | A named interface that a unit provides: an API, a library, a command, a stream of events. It is something others use, not a feature of the product and not an access right. |
| Need | A named thing that a unit requires and does not implement itself. It says what is required, never who supplies it. |
| Wiring | The mapping in a unit's manifest from needs to providers: the needs of its children, and needs of its own that a child meets. A provider is a capability of a child or, for a need of a child, a need of the unit. One need joined to its provider is a connection. |
| Contract | The document that defines a connection exactly: its parts, each with a signature and examples, and the fake that stands in for it in tests. It is a reference, `docs/references/<topic>.md`, that both sides name (section 2, and rule 8 of section 3). A kind such as `http` or `json` is not a contract, and neither is a schema file such as `openapi.yaml`. |
| Part | One operation, event or type of a contract: a `###` heading under `## Parts`, or a file of a contract folder ([contracts.md](contracts.md)). |
| Scenario | One story told as the chain of calls it causes, declared in a manifest as hops (section 4). |

## 2. The manifest

```yaml
responsibility: Sends frames over the serial line    # transport/unifold.yaml
kind: adapter
secret:
  what: serial line access
  decision: docs/decisions/0001-the-line-is-one-unit.md
not:
  - frame layout: frames
  - retries after a failed write
capabilities:
  transport:
    summary: Sends a payload as one frame
    contract: ../docs/references/transport.md
needs:
  frames:
    summary: The layout of a frame
    contract:
      path: ../docs/references/frames.md
      parts:
        - encode
        - decode
  uart:
    summary: The serial port
    contract: ../docs/references/uart.md
```

A manifest is a YAML mapping with these keys. Any other key is an error.

| Key | Required | Meaning |
|---|---|---|
| `responsibility` | yes | What the unit is responsible for, in one sentence. A text that starts with `TODO` marks a draft and is reported. A placeholder in angle brackets, `<...>`, is an error. |
| `kind` | units with children, except the root | Free text. `logic`, `stateful` and `adapter` are well known and carry rules ([wiring.md](../explanation/wiring.md)): a `logic` unit has only `logic` children and reaches no need of the root; an `adapter` is the one unit that talks to one external system. Any other value is allowed and carries none. |
| `status` | no | `planned` (code missing or incomplete), `active` (default) or `deprecated` (to be removed). |
| `owner` | no | The team or person responsible. Descendants inherit it until one sets its own. |
| `secret` | no | What the unit hides because it is hard to get right or likely to change: `what`, one line, and `decision`, a path relative to the manifest to a decision of this unit or of an ancestor. |
| `not` | no | A list of what the unit does not do. An item is one line, or one line mapped to the need of this unit through which the thing is delegated: `frame layout: frames`. |
| `capabilities` | no | The capabilities, keyed by name. |
| `needs` | no | The needs, keyed by name. The parent wires them, except a need that the unit meets inside (section 3). The needs of the root that it does not meet inside are what the project requires from outside. |
| `wiring` | no | The connections inside this unit (section 3). |
| `scenarios` | no | The scenarios this unit holds, keyed by name (section 4). |
| `x-...` | no | A key that starts with `x-`, here or in an entry of `capabilities`, `needs` or `scenarios`, belongs to the project and is ignored. |
| `unifold` | root: yes | Root only. The version of this standard, as a string: `"0.3"`. |
| `name` | no | Root only. The name of the project. Default: the name of the root folder. It SHOULD be set, because generated files contain it. |
| `ignore` | no | Root only. Folders, relative to the root, that are not searched for units. What version control ignores is not searched either. |
| `diagrams` | no | Root only. `parents` (default), `all` or `none` (section 7). |
| `diagram-links` | no | Root only. How boxes in diagrams link: `none` (default), `relative`, or a base URL. |
| `max-lines` | no | Root only. The line limit for hand-written documents. Default: 200. |

An entry of `capabilities` or `needs` is either a string, its summary, or a mapping with these keys:

| Key | Required | Meaning |
|---|---|---|
| `summary` | yes | One line: what the capability provides, or what the need expects. `TODO` and `<...>` as for `responsibility`. |
| `kind` | no | Free text for the technical nature, for example `library`, `http`, `events`, `cli`. |
| `contract` | no | The contract of the connection (section 1): a path, relative to the folder of the manifest, to a Markdown file in `docs/references/` of this unit or of an ancestor, or a mapping with `path` and `parts`, the names of the parts this side uses. It MUST exist, and every name under `parts` MUST be a part of it. A URL is not a contract; a reference links a definition from outside the project. |
| `optional` | no | On a need only: `true` if the need may stay unconnected. Default: `false`. |
| `platform` | no | On a need of the root only: `true` marks a service of the host such as time or randomness. It is not an external system, and its contract describes a controllable fake. |

The name of a capability, need or scenario consists of letters, digits, `-` and `_`, starts with a letter or a digit, and is local to the unit. A folder name MAY contain dots. No unit lies in a folder whose name starts with a dot, or in the `docs` folder of a unit. A manifest does not list its children or its users.

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
5. **Kinds.** A need and its provider SHOULD have the same `kind`. A difference is reported only when both state a kind.
6. **Direction.** A connection records a dependency, not the direction in which data flows. A subscriber needs the stream; the publisher provides it.
7. **Final provider.** Who finally provides for a need, or uses a capability, is found by following needs up and capabilities down.
8. **Contract.** Both sides of every connection MUST name a contract, and the same one. So the contract of a connection lies in the unit that wires it, or higher.

## 4. Scenarios

```yaml
scenarios:
  open:
    summary: The host opens a session
    source: proto §5
    hops:
      - host -> session.open
      - session -> transport.send
      - transport/serial -> uart.write
    expect: one frame 1F 00 on the line
```

A scenario has `summary`, `hops` and `expect`; `source` is free text. A hop is `caller -> target.part`. A unit is named by its path from the holding unit, segments separated by `/`; a capability or need of the holding unit is named bare. A name is looked up as a descendant first, then as a capability or need of the holding unit; a name that is both is an error.

1. A hop MUST resolve, by rule 7 of section 3, to one connection: from a need of the caller to a capability of the target, from a capability of the holding unit down to the target, or from a need of the caller up to a need of the holding unit. In a unit without children, a hop from a capability to a need of the unit says that the capability's implementation uses the need.
2. The part MUST be a part of that connection's contract, which is one document at every level. Two connections between the same two units whose contracts both have the part are an error.
3. A scenario SHOULD be held by the lowest unit that contains every unit it names.

## 5. Documents

Every unit MUST have a `README.md`: what it is for, and why it is built this way. What can be relied on is in the contracts that its manifest names; their body is defined in [writing.md](writing.md) and explained in [contracts.md](contracts.md). Everything else written about a unit lives in its `docs/`, sorted by kind, as [documents.md](documents.md) and [writing.md](writing.md) say. A checker reads links, headings, front matter, length, whether a fenced block exists under a part heading and the names in code spans; it judges no sentence.

## 6. What a checker guarantees

A conforming checker reads a project, changes nothing, and reports findings with a severity: `error`, `warn` or `info`. An error is what makes the map inconsistent; everything that makes a map better but is not needed for consistency is a warning. It MUST report at least:

| Finding | Severity |
|---|---|
| A manifest that is not valid: not a YAML mapping, an unknown key, a wrong type, no `responsibility`; a unit with children below the root without `kind`; a root without `unifold`; `platform` outside a need of the root; a `secret` or `not` that section 2 does not allow | error |
| A wiring line that section 3 does not allow, or that names a child, capability or need that does not exist | error |
| A need of a child that is not `optional`, not met inside the child, and not connected | error |
| A path in a manifest that does not exist, or lies where section 2 forbids; a name under `parts` that is no part of the contract | error |
| A scenario without `summary`, `hops` or `expect`; a hop that does not resolve as section 4 says, or whose part is not in the contract, or whose name is ambiguous | error |
| A unit without `README.md`; a link in a hand-written document whose target does not exist, that leaves the project, or that is an absolute path | error |
| A side of a connection without a contract, or two sides that name different contracts | error |
| A decision whose status is not one of [writing.md](writing.md), or a `derived` decision without `derived-from` and `## Source says` | error |
| A generated file that is missing, ignored by version control, or differs from what the generator would write now | error |
| A `logic` or `adapter` unit that breaks its rule; a need of the root without `platform` that a unit with another `kind` finally reaches | warn |
| A contract without `## Parts` or `## Fake`; a part without a known `Kind:` or a fenced signature; a command or query without `Pre:`, `Result:`, `Errors:` and an example; a type defined twice within one subtree | warn |
| A wiring line of a unit that no hop of a scenario passing through the unit uses | warn |
| A link in a hand-written document that points in a direction [documents.md](documents.md) forbids | warn |
| A hand-written document with more lines than `max-lines` | warn |
| `responsibility: TODO`, `summary: TODO` | warn |

No error means consistent, not correct: no checker reads the code, and none judges whether a text is true. Reference tool: [tool.md](tool.md), [rules.md](rules.md).

## 7. Generated files

Diagrams and indexes are generated from the manifests and MUST NOT be edited by hand. A diagram is Markdown with a Mermaid chart and the same content as tables. Every generated file starts with a comment that begins with `<!-- unifold:generated`; the comment counts only at a path the generator writes.

| File in the unit | Shows | Written for |
|---|---|---|
| `docs/diagrams/component.md` | The children of the unit, each with its responsibility and kind, and the connections between them and with the unit's own needs. | Units that have children. |
| `docs/diagrams/context.md` | The unit inside the frame of its parent, with the siblings it is connected to; tables of the final provider of each need and the final users of each capability. | Units that have children and a parent. |
| `docs/diagrams/architecture.md` | The unit opened up three levels deep, or fewer where the page would exceed the line limit. | Units whose children have children. |
| `docs/diagrams/scenario-<name>.md` | One scenario as a sequence diagram, one lifeline per unit, capability or need named, with its kind and its responsibility or summary, drawn end to end across levels, with the hops as a table. | Units that hold scenarios. |
| `docs/decisions/index.md` | The decisions of the unit, with status and date. | Units that have decisions. |
| `AGENTS.md` | Where the documents and skills of the unit are, for coding agents; at the root also the unifold block with the index of units. | Every unit. |

- `diagrams: all` also writes `context.md` for units without children; `diagrams: none` writes no diagram.
- An arrow points from what needs to what provides. A need of the unit to which three or more children pass up is listed once below the picture. A `planned` unit is marked.
- Generated links are URL-encoded.
- Generated files MUST be committed, and kept current with every change to what they show. A checker cannot see a commit; it reports a generated file that is missing, out of date, or ignored by version control.

## 8. Nested projects

A folder below the root whose manifest has the key `unifold` is the root of a nested project: a separate project, checked on its own. The outer project does not treat it as a child, and nothing is wired to it.

## 9. Conformance

- A project conforms to unifold 0.3 when a conforming checker reports no error for it. Warnings do not break conformance. A conforming project MAY say "This repository follows unifold 0.3".
- A tool conforms when it accepts and rejects the same manifests as this page, connects needs as section 3 says, resolves hops as section 4 says, and reports the findings of section 6. [tool.md](tool.md) says how to test another implementation. A tool of version 0.3 reads version 0.3 only.
