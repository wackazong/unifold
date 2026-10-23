# unifold 0.1: the standard

Version 0.1. This page is the standard for manifests, wiring, generated files and the comparison with code; [documents.md](documents.md) and [writing.md](writing.md) are the standard for the documents of a unit. MUST, MUST NOT, SHOULD and MAY are used as in [BCP 14](https://www.rfc-editor.org/info/bcp14). Examples are not normative.

## 1. Terms

| Term | Meaning |
|---|---|
| Unit | A folder that contains a file named `unifold.yaml`, its manifest. Nothing else makes a folder a unit. The unit's name is the folder's name. A unit SHOULD hold code that is built, run or deployed. A document is never a unit. |
| Root | The top unit of a project. Its manifest has the key `unifold`. |
| Project | The root and everything below it, except nested projects (section 8). |
| Plain folder | A folder that is not a unit. It belongs to the nearest unit above it. |
| Parent, child | The parent of a unit is the nearest unit above it; plain folders in between do not count. Siblings have the same parent. Ancestors are the parent, its parent, and so on; descendants are the reverse. |
| Capability | A named interface that a unit provides: an API, a library, a command, a stream of events. It is something others use, not a feature of the product and not an access right. |
| Need | A named thing that a unit requires from outside itself. It says what is required, never who supplies it. |
| Wiring | The mapping in a unit's manifest from needs to providers. A provider is a capability of a child or a need of the unit itself. One need joined to its provider is a connection. |
| Contract | The document that defines a capability or need exactly, given as a path or a URL. Both sides of a connection name the same contract. |

## 2. The manifest

```yaml
summary: Creates invoices            # billing/unifold.yaml
capabilities:
  invoices:
    summary: Create and fetch invoices
    contract: openapi.yaml
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
| `needs` | no | The needs, keyed by name. The needs of the root are what the project requires from outside; nothing above wires them. |
| `wiring` | no | The connections inside this unit (section 3). |
| `x-...` | no | A key that starts with `x-`, here or in an entry of `capabilities` or `needs`, belongs to the project and is ignored. |
| `unifold` | root: yes | Root only. The version of this standard, as a string: `"0.1"`. |
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
| `contract` | no | The exact definition: a URL, or a path relative to the folder of the manifest. A path MUST exist and lie in this unit, in an ancestor or in a descendant. |
| `verified-by` | no | What checks the entry against its contract, for example tests: a URL or a path, as for `contract`. Leaving it out is never a finding. |
| `optional` | no | On a need only: `true` if the need may stay unconnected. Default: `false`. |

The name of a capability or need consists of letters, digits, `-` and `_`, starts with a letter or a digit, and is local to the unit. A folder name MAY contain dots. No unit lies in a folder whose name starts with a dot, or in the `docs` folder of a unit. A manifest does not list its children or its users.

## 3. Wiring

`wiring` is a mapping. The key is a need, the value its provider: "this need is met by that provider". A reference is either a bare name, an entry of the unit itself, or `child.name`, an entry of a direct child. A reference is split at its last dot. `child` is the child's folder name, or its path relative to the unit (`a/utils.matcher`); the path MUST be used when two children have the same folder name.

| Key | Value | Meaning |
|---|---|---|
| `child.need` | `sibling.capability` | Another child provides for the need. |
| `child.need` | `own-need` | The need is passed up: whatever meets this unit's own need meets it. |
| `own-capability` | `child.capability` | A child implements a capability of this unit. |
| `child.need` | `{name: provider, ...}` | Named alternatives, each in one of the forms above. The first is the default. |

1. **One level.** Wiring names only entries of the unit itself and of its direct children. It MUST NOT name anything deeper.
2. **Complete.** Every need of every child MUST be connected, unless it is `optional`. The provider is, in this order: (a) a line whose key names that child and need; (b) **implicit pass-up:** a need of the unit itself with the same name. Otherwise the need is unconnected, which is an error.
3. **Sides.** A key is a need of a child or a capability of the unit. A value is a capability of a child or, for a need only, a need of the unit. A child that provides for its own need is an error.
4. **Alternatives.** A need has one provider at a time. The build or the deployment decides which alternative is in use; this standard does not describe configurations. Every alternative MUST meet all that the need expects.
5. **Kinds.** A need and its provider SHOULD have the same `kind`. A difference is reported only when both state a kind.
6. **Direction.** A connection records a dependency, not the direction in which data flows. A subscriber needs the stream; the publisher provides it.
7. **Final provider.** Who finally provides for a need, or uses a capability, is found by following needs up and capabilities down.
8. **Contract.** Both sides of every connection MUST name a contract, and the same one.

## 4. Documents

Every unit MUST have a `README.md`: what it is for, why it is built this way, what can be relied on. Everything else written about a unit lives in its `docs/`, sorted by kind, as [documents.md](documents.md) and [writing.md](writing.md) say. A checker reads links and lengths, not meaning.

## 5. What a checker guarantees

A conforming checker reads a project, changes nothing, and reports findings with a severity: `error`, `warn` or `info`. It MUST report at least:

| Finding | Severity |
|---|---|
| A manifest that is not valid: not a YAML mapping, an unknown key, a wrong type, no `summary`; a root without `unifold` | error |
| A wiring reference to a child, capability or need that does not exist, or that is on the wrong side | error |
| A need of a child that is not `optional` and not connected | error |
| A path in a manifest that does not exist, or lies where section 2 forbids | error |
| A unit without `README.md`; a link in a hand-written document whose target does not exist, or that points where [documents.md](documents.md) forbids | error |
| A side of a connection without a contract, or two sides that name different contracts | error |
| A generated file that is missing, or differs from what the generator would write now | error |
| A dependency found in code that no connection covers (section 7) | error |
| A connection for which no dependency is found in code (section 7) | warn |
| `summary: TODO` | warn |

No error means consistent, not correct: no checker judges whether a summary is true. Reference tool: [tool.md](tool.md), [rules.md](rules.md).

## 6. Generated files

Diagrams and indexes are generated from the manifests and MUST NOT be edited by hand. A diagram is Markdown with a Mermaid flowchart and the same content as tables. Every generated file starts with a comment that begins with `<!-- unifold:generated`; the comment counts only at a path the generator writes.

| File in the unit | Shows | Written for |
|---|---|---|
| `docs/diagrams/component.md` | The children of the unit and the connections between them. | Units that have children. |
| `docs/diagrams/context.md` | The unit inside the frame of its parent, with the siblings it is connected to; tables of the final provider of each need and the final users of each capability. | Units that have children and a parent. |
| `docs/diagrams/architecture.md` | The unit opened up three levels deep, or fewer where the page would exceed the line limit. | Units whose children have children. |
| `docs/decisions/index.md` | The decisions of the unit, with status and date. | Units that have decisions. |
| `AGENTS.md` | Where the documents and skills of the unit are, for coding agents; at the root also the unifold block with the index of units. | Every unit. |

- `diagrams: all` also writes `context.md` for units without children; `diagrams: none` writes no diagram.
- An arrow points from the unit that needs to the unit that provides. A need that three or more children pass up by name is listed once below the picture. A `planned` unit is marked.
- Generated links are URL-encoded. Generated files SHOULD be committed.

## 7. Comparison with dependencies in code

Manifests can agree with each other and still be wrong, so a checker compares the wiring with dependencies observed in the code. A dependency has `from` and `to`, paths of files or folders relative to the root, and optionally `kind` and `evidence`, which say how and where it was found:

```json
[{"from": "billing", "to": "platform", "kind": "cargo", "evidence": "billing/Cargo.toml"}]
```

- Each path belongs to the nearest unit at or above it. A path that does not exist is an error. A dependency inside one unit is ignored.
- A dependency from unit A to unit B is covered when a need of A, or of a unit between A and their nearest common ancestor, is connected to a capability of B, or of a unit between B and that ancestor.
- Code of a unit itself MAY depend on anything below that unit. Code below a unit that depends on code of the unit itself is not covered.
- A dependency that only tests have, such as a dev-dependency, has a `kind` that ends in `-dev`. It counts as observed and never needs a connection.
- Any other dependency that is not covered is an error. A connection with no observed dependency, between two units whose dependencies are both extracted, is a warning. The comparison is per pair of units, not per capability.

A checker SHOULD extract dependencies itself from build files it understands, and MUST accept a list in this format ([tool.md](tool.md)).

## 8. Nested projects

A folder below the root whose manifest has the key `unifold` is the root of a nested project: a separate project, checked on its own. The outer project does not treat it as a child, and nothing is wired to it.

## 9. Conformance

- A project conforms to unifold 0.1 when a conforming checker reports no error for it, with the comparison of section 7 switched on. Warnings do not break conformance. A conforming project MAY say "This repository follows unifold 0.1".
- A tool conforms when it accepts and rejects the same manifests as this page, connects needs as section 3 says, and reports the findings of section 5. [tool.md](tool.md) says how to test another implementation.
