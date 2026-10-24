# unifold 0.2: the standard

Version 0.2. This page is the standard for manifests, wiring and generated files; [documents.md](documents.md) and [writing.md](writing.md) are the standard for the documents of a unit. MUST, MUST NOT, SHOULD and MAY are used as in [BCP 14](https://www.rfc-editor.org/info/bcp14). Examples are not normative.

## 1. Terms

| Term | Meaning |
|---|---|
| Unit | A folder that contains a file named `unifold.yaml`, its manifest. Nothing else makes a folder a unit. The unit's name is the folder's name. A unit SHOULD hold code that is built, run or deployed. A document is never a unit. |
| Root | The top unit of a project. Its manifest has the key `unifold`. |
| Project | The root and everything below it, except nested projects (section 7). |
| Plain folder | A folder that is not a unit. It belongs to the nearest unit above it. |
| Parent, child | The parent of a unit is the nearest unit above it; plain folders in between do not count. Siblings have the same parent. Ancestors are the parent, its parent, and so on; descendants are the reverse. |
| Capability | A named interface that a unit provides: an API, a library, a command, a stream of events. It is something others use, not a feature of the product and not an access right. |
| Need | A named thing that a unit requires and does not implement itself. It says what is required, never who supplies it. |
| Wiring | The mapping in a unit's manifest from needs to providers: the needs of its children, and needs of its own that a child meets. A provider is a capability of a child or, for a need of a child, a need of the unit. One need joined to its provider is a connection. |
| Contract | The document that defines a connection exactly: what travels, in which form, with examples. It is a reference, `docs/references/<topic>.md` of the unit that wires the connection or of a unit above it, and both sides name it. A kind such as `http` or `json` is not a contract, and neither is a schema file such as `openapi.yaml`. |

## 2. The manifest

```yaml
summary: Creates invoices            # billing/unifold.yaml
capabilities:
  invoices:
    summary: Create and fetch invoices
    contract: ../docs/references/invoices.md
    verified-by: tests/api
needs:
  clock: {summary: A time source, contract: ../docs/references/clock.md}
  mailer: {summary: Sends an invoice to a customer, optional: true}
```

A manifest is a YAML mapping with these keys. Any other key is an error.

| Key | Required | Meaning |
|---|---|---|
| `summary` | yes | What the unit is, in one line. A summary that starts with `TODO` marks a draft and is reported. A summary that is only a placeholder in angle brackets, `<...>`, is an error. |
| `kind` | no | Free text, for example `library`, `service`, `app`, `adapter`. |
| `status` | no | `planned` (code missing or incomplete), `active` (default) or `deprecated` (to be removed). |
| `owner` | no | The team or person responsible. Descendants inherit it until one sets its own. |
| `capabilities` | no | The capabilities, keyed by name. |
| `needs` | no | The needs, keyed by name. The parent wires them, except a need that the unit meets inside (section 3). The needs of the root that it does not meet inside are what the project requires from outside. |
| `wiring` | no | The connections inside this unit (section 3). |
| `x-...` | no | A key that starts with `x-`, here or in an entry of `capabilities` or `needs`, belongs to the project and is ignored. |
| `unifold` | root: yes | Root only. The version of this standard, as a string: `"0.2"`. |
| `name` | no | Root only. The name of the project. Default: the name of the root folder. It SHOULD be set: generated files contain it, so a copy in a folder of another name would otherwise have stale generated files. |
| `ignore` | no | Root only. Folders, relative to the root, that are not searched for units. What version control ignores is not searched either. |
| `diagrams` | no | Root only. `parents` (default), `all` or `none` (section 6). |
| `diagram-links` | no | Root only. How boxes in diagrams link: `none` (default), `relative`, or a base URL. |
| `max-lines` | no | Root only. The line limit for hand-written documents. Default: 200. |

An entry of `capabilities` or `needs` is either a string, its summary, or a mapping with these keys:

| Key | Required | Meaning |
|---|---|---|
| `summary` | yes | One line: what the capability provides, or what the need expects. `TODO` and `<...>` as for the unit. |
| `kind` | no | Free text for the technical nature, for example `library`, `http`, `events`, `cli`. |
| `contract` | no | The contract of the connection (section 1): a path, relative to the folder of the manifest, to a Markdown file in `docs/references/` of this unit or of an ancestor. It MUST exist. A URL is not a contract; a reference links a definition from outside the project. |
| `verified-by` | no | What checks the entry against its contract, for example tests: a URL, or a path relative to the folder of the manifest. A path MUST exist and lie in this unit, in an ancestor or in a descendant. Leaving it out is never a finding. |
| `optional` | no | On a need only: `true` if the need may stay unconnected. Default: `false`. |

The name of a capability or need consists of letters, digits, `-` and `_`, starts with a letter or a digit, and is local to the unit. A folder name MAY contain dots. No unit lies in a folder whose name starts with a dot, or in the `docs` folder of a unit. A manifest does not list its children or its users.

## 3. Wiring

`wiring` is a mapping. The key is a need, or a capability of the unit; the value is its provider: "this is met by that". A reference is either a bare name, an entry of the unit itself, or `child.name`, an entry of a direct child. A reference is split at its last dot. `child` is the child's folder name, or its path relative to the unit (`a/utils.matcher`); the path MUST be used when two children have the same folder name.

| Key | Value | Meaning |
|---|---|---|
| `child.need` | `sibling.capability` | Another child provides for the need. |
| `child.need` | `own-need` | The need is passed up: whatever meets this unit's own need meets it. |
| `own-need` | `child.capability` | A child provides for a need of this unit, for example of its own code. The need is met inside this unit. |
| `own-capability` | `child.capability` | A child implements a capability of this unit. |
| any key above | `{name: provider, ...}` | Named alternatives, each in the form for that key. The first is the default. |

```yaml
# shop/unifold.yaml: the main program of shop uses both children
needs:
  clock: {summary: The current time, contract: docs/references/clock.md}      # met inside
  mailer: {summary: Sends mail, contract: docs/references/mailer.md}          # from outside
wiring:
  billing.clock: platform.clock     # a need of a child, met by a sibling
  billing.mailer: mailer            # a need of a child, passed up
  clock: platform.clock             # a need of shop itself, met by a child
```

1. **One level.** Wiring names only entries of the unit itself and of its direct children. It MUST NOT name anything deeper.
2. **Complete.** Every need of every child MUST be connected by a line of the parent, unless it is `optional` or the child meets it inside. Nothing is connected without a line: a need of the parent with the same name does not meet a need of a child.
3. **Sides.** A key is a need of a child, a need of the unit or a capability of the unit; a bare key that names both a need and a capability of the unit is an error. A value is a capability of a child or, for a need of a child, a need of the unit that the unit does not meet inside. A need that a child meets inside MUST NOT be wired again. A child that provides for its own need is an error.
4. **Alternatives.** A need has one provider at a time. The build or the deployment decides which alternative is in use; this standard does not describe configurations. Every alternative MUST meet all that the need expects.
5. **Kinds.** A need and its provider SHOULD have the same `kind`. A difference is reported only when both state a kind.
6. **Direction.** A connection records a dependency, not the direction in which data flows. A subscriber needs the stream; the publisher provides it.
7. **Final provider.** Who finally provides for a need, or uses a capability, is found by following needs up and capabilities down. A need that a unit meets inside is followed down; its user is the unit itself.
8. **Contract.** Both sides of every connection MUST name a contract, and the same one. So the contract of a connection lies in the unit that wires it, or higher.

## 4. Documents

Every unit MUST have a `README.md`: what it is for, why it is built this way, what can be relied on. Everything else written about a unit lives in its `docs/`, sorted by kind, as [documents.md](documents.md) and [writing.md](writing.md) say. A checker reads links and lengths, not meaning.

## 5. What a checker guarantees

A conforming checker reads a project, changes nothing, and reports findings with a severity: `error`, `warn` or `info`. It MUST report at least:

| Finding | Severity |
|---|---|
| A manifest that is not valid: not a YAML mapping, an unknown key, a wrong type, no `summary`; a root without `unifold` | error |
| A wiring line that section 3 does not allow, or that names a child, capability or need that does not exist | error |
| A need of a child that is not `optional`, not met inside the child, and not connected | error |
| A path in a manifest that does not exist, or lies where section 2 forbids | error |
| A unit without `README.md`; a link in a hand-written document whose target does not exist, that leaves the project, or that is an absolute path | error |
| A side of a connection without a contract, or two sides that name different contracts | error |
| A generated file that is missing, ignored by version control, or differs from what the generator would write now | error |
| A link in a hand-written document that points in a direction [documents.md](documents.md) forbids | warn |
| `summary: TODO` | warn |

No error means consistent, not correct: no checker reads the code, and none judges whether a summary is true. Reference tool: [tool.md](tool.md), [rules.md](rules.md).

## 6. Generated files

Diagrams and indexes are generated from the manifests and MUST NOT be edited by hand. A diagram is Markdown with a Mermaid flowchart and the same content as tables. Every generated file starts with a comment that begins with `<!-- unifold:generated`; the comment counts only at a path the generator writes.

| File in the unit | Shows | Written for |
|---|---|---|
| `docs/diagrams/component.md` | The children of the unit and the connections between them and with the unit's own needs. | Units that have children. |
| `docs/diagrams/context.md` | The unit inside the frame of its parent, with the siblings it is connected to; tables of the final provider of each need and the final users of each capability. | Units that have children and a parent. |
| `docs/diagrams/architecture.md` | The unit opened up three levels deep, or fewer where the page would exceed the line limit. | Units whose children have children. |
| `docs/decisions/index.md` | The decisions of the unit, with status and date. | Units that have decisions. |
| `AGENTS.md` | Where the documents and skills of the unit are, for coding agents; at the root also the unifold block with the index of units. | Every unit. |

- `diagrams: all` also writes `context.md` for units without children; `diagrams: none` writes no diagram.
- An arrow points from what needs to what provides. A need of the unit to which three or more children pass up is listed once below the picture. A `planned` unit is marked.
- Generated links are URL-encoded.
- Generated files MUST be committed, and kept current with every change to what they show. A checker cannot see a commit; it reports a generated file that is missing, out of date, or ignored by version control.

## 7. Nested projects

A folder below the root whose manifest has the key `unifold` is the root of a nested project: a separate project, checked on its own. The outer project does not treat it as a child, and nothing is wired to it.

## 8. Conformance

- A project conforms to unifold 0.2 when a conforming checker reports no error for it. Warnings do not break conformance. A conforming project MAY say "This repository follows unifold 0.2".
- A tool conforms when it accepts and rejects the same manifests as this page, connects needs as section 3 says, and reports the findings of section 5. [tool.md](tool.md) says how to test another implementation.
- A checker MAY read a project that says `"0.1"` with the meaning of 0.1: a bare wiring key always names a capability, and a need of a child is connected without a line to a need of the unit with the same name.
