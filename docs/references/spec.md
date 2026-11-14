# unifold 0.4: the standard

Version 0.4. The standard for manifests, wiring, scenarios and generated files has four pages: this one, with the terms and the manifest; [spec-wiring.md](spec-wiring.md), with wiring and the kinds of units; [spec-scenarios.md](spec-scenarios.md), with scenarios; and [spec-conformance.md](spec-conformance.md), with documents, what a checker guarantees, generated files and conformance. The standard for the documents of a unit is [documents.md](documents.md), [placement.md](placement.md), [writing.md](writing.md), [decision-records.md](decision-records.md), [contracts.md](contracts.md) and [contract-parts.md](contract-parts.md). The explanation chapters and the tutorial add no rule. MUST, MUST NOT, SHOULD and MAY are used as in [BCP 14](https://www.rfc-editor.org/info/bcp14). Examples are not normative.

## 1. Terms

| Term | Meaning |
|---|---|
| Unit | A folder that contains a file named `unifold.yaml`, its manifest. Nothing else makes a folder a unit. The unit's name is the folder's name. A unit SHOULD hold code that is built, run or deployed. A document is never a unit. |
| Root | The top unit of a project. Its manifest has the key `unifold`. |
| Project | The root and everything below it, except nested projects ([section 8](spec-conformance.md#8-nested-projects)). |
| Plain folder | A folder that is not a unit. It belongs to the nearest unit above it. |
| Parent, child | The parent of a unit is the nearest unit above it; plain folders in between do not count. Siblings have the same parent. Ancestors are the parent, its parent, and so on; descendants are the reverse. |
| Capability | A named interface that a unit provides: an API, a library, a command, a stream of events. It is something others use, not a feature of the product and not an access right. |
| Need | A named thing that a unit requires and does not implement itself. It says what is required, never who supplies it. |
| Wiring | The mapping in a unit's manifest from needs to providers: the needs of its children, and needs of its own that a child meets. A provider is a capability of a child or, for a need of a child, a need of the unit. |
| Connection | A need joined to its provider, or a capability of the unit joined to the capability of the child that implements it. |
| Consumer, provider | The two sides of a connection: the unit whose need it meets, and the unit whose capability meets it. The consumer calls an operation, and the provider answers; the provider raises an event, and the consumer receives it. |
| Hop | One step of a scenario: from a caller to an operation or event of a connection's contract, with an optional note ([section 4](spec-scenarios.md#4-scenarios)). |
| Contract | The document that defines a connection exactly: its parts, each with a signature and examples, and the fake that stands in for it in tests. It is a reference, `docs/references/<topic>.md`, that both sides name (section 2, and rule 7 of [section 3](spec-wiring.md#3-wiring)). A protocol or format name such as `http` or `json` is not a contract, and neither is a schema file such as `openapi.yaml`. |
| Part | One operation, event or type of a contract: a `###` heading under `## Parts`, or a file of a contract folder ([contract-parts.md](contract-parts.md)). |
| Scenario | A story through the software, step by step: which unit uses which connection, in which order. It is declared in a manifest as hops ([section 4](spec-scenarios.md#4-scenarios)). |
| State | A state of a connection that its contract describes under `## States`: what a consumer can see of the connection or must respect ([contracts.md](contracts.md#states)). |

## 2. The manifest

```yaml
responsibility: Sends frames over the serial line    # transport/unifold.yaml
kind: adapter
runs-as: library
not:
  - the layout of a frame
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

A manifest MUST be a YAML mapping that holds the required keys of this table, no key twice and no key but these. Every value MUST have the form that its row gives, a key marked "Root only" MUST NOT stand in another manifest, and no text of a manifest MUST be a placeholder in angle brackets, `<...>`, as its whole value.

| Key | Required | Meaning |
|---|---|---|
| `responsibility` | yes | What the unit is responsible for, in one sentence on one line. It SHOULD NOT start with `TODO`, which marks a draft. |
| `kind` | no | Free text. The values `logic`, `stateful` and `adapter` carry rules ([section 3](spec-wiring.md#kinds-of-units)); any other value is allowed and carries none. |
| `runs-as` | no | What the unit runs as: `library`, `process`, `job`, `ui` or `firmware`. The diagrams show it. |
| `status` | no | `planned` (code missing or incomplete), `active` (default) or `deprecated` (to be removed). |
| `not` | no | A list of what the unit does not do, one line each. |
| `capabilities` | no | The capabilities, keyed by name. |
| `needs` | no | The needs, keyed by name. The parent wires them, except a need that the unit meets inside ([section 3](spec-wiring.md#3-wiring)). The needs of the root that it does not meet inside are what the project requires from outside. |
| `wiring` | no | The connections inside this unit ([section 3](spec-wiring.md#3-wiring)). |
| `scenarios` | no | The scenarios this unit holds, keyed by name ([section 4](spec-scenarios.md#4-scenarios)). |
| `x-...` | no | A key that starts with `x-`, here or in an entry of `capabilities`, `needs` or `scenarios`, belongs to the project and is ignored. |
| `unifold` | root: yes | Root only. The version of this standard, as the string `"0.4"`. |
| `name` | no | Root only. The name of the project. Default: the name of the root folder. It SHOULD be set, because generated files contain it. |
| `ignore` | no | Root only. Folders, relative to the root, that are not searched for units. Each MUST exist. |

An entry of `capabilities` or `needs` is a string, its summary; a mapping with these keys; or empty, with no value or `{}`. Exactly one wiring line MUST join an empty entry to another entry, whose summary and contract it takes: a need of a child from its provider, a capability from the child that implements it, a need that a child meets inside from that child.

| Key | Required | Meaning |
|---|---|---|
| `summary` | yes | One line: what the capability provides, or what the need expects. `TODO` as for `responsibility`. |
| `contract` | no | The contract of the connection (section 1): a path, relative to the folder of the manifest, to a Markdown file in `docs/references/` of this unit or of an ancestor, without a fragment, or a mapping with `path` and `parts`, the names of the parts this side uses. It MUST exist, and every name under `parts` MUST be a part of it. A URL is not a contract; a reference links a definition from outside the project. |
| `optional` | no | On a need only: `true` if the need may stay unconnected. Default: `false`. |
| `platform` | no | On a need of the root, and MUST NOT stand elsewhere: `true` marks a service of the host such as time or randomness. It is not an external system, and its contract describes a controllable fake. |

The name of a capability, need or scenario MUST consist of ASCII letters, digits, `-` and `_` and start with an ASCII letter or a digit; it is local to the unit. A folder name MAY contain dots. These folders are not searched for units: a folder whose name starts with a dot, the `docs` folder of a unit, `node_modules`, `__pycache__`, a Python virtual environment (a folder with `pyvenv.cfg`), a Cargo build folder (`target` with `CACHEDIR.TAG`), a symbolic link, a folder under `ignore`, and what version control ignores. A manifest does not list its children or its users.
