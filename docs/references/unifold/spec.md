# unifold 0.1: the standard

Draft 0.1. This page is the whole standard for level `core`; level `full` adds
[documents.md](documents.md). MUST, MUST NOT, SHOULD and MAY are used as in
[BCP 14](https://www.rfc-editor.org/info/bcp14). Examples are not normative.

## 1. Terms

| Term | Meaning |
|---|---|
| Unit | A folder that contains a file named `unifold.yaml`, its manifest. Nothing else makes a folder a unit. The unit's name is the folder's name. |
| Root | The top unit of a project. Its manifest has the key `unifold`. |
| Project | The root and everything below it, without nested projects (section 8). |
| Plain folder | A folder that is not a unit. It belongs to the nearest unit above it. |
| Parent, child | The parent of a unit is the nearest unit above it; plain folders in between do not count. Siblings have the same parent. Ancestors are the parent, its parent, and so on. |
| Capability | A named interface that a unit provides: an API, a library, a command, a stream of events, a format. It is something others may use, not a feature of the product, and not an access right. |
| Need | A named thing that a unit requires from outside itself. It says what is required, never who supplies it. |
| Wiring | The map in a unit's manifest that connects needs to providers. One need joined to its provider is a connection. |
| Contract | The exact definition of a capability or need: a file or a URL. |

## 2. The manifest

```yaml
summary: Creates invoices            # billing/unifold.yaml
capabilities:
  invoices:
    summary: Create and fetch invoices
    contract: openapi.yaml
    verified-by: tests/api
needs:
  clock: A time source          # short form: the text is the summary
  mailer: {summary: Sends an invoice to a customer, optional: true}
```

A manifest is a YAML mapping with these keys. Any other key is an error.

| Key | Required | Meaning |
|---|---|---|
| `summary` | yes | What the unit is, in one line. A summary that starts with `TODO` marks a draft and is reported. A summary that is only a placeholder in angle brackets, `<...>`, is an error. |
| `kind` | no | Free text, for example `library`, `service`, `app`, `adapter`. |
| `status` | no | `planned` (code missing or incomplete), `active` (default) or `deprecated` (to be removed). |
| `owner` | no | The team or person responsible. Units below inherit it until one sets its own. |
| `capabilities` | no | The capabilities, keyed by name. |
| `needs` | no | The needs, keyed by name. The needs of the root are what the project requires from the outside world; they are never wired. |
| `wiring` | no | The connections inside this unit (section 3). |
| `level` | no | `core` (default) or `full`. It holds for the unit and everything below it, until a unit below sets another value (section 4). |
| `x-...` | no | A key that starts with `x-`, here or in an entry of `capabilities` or `needs`, belongs to the project and is ignored. |
| `unifold` | root: yes | Root only. The version of this standard, as a string: `"0.1"`. |
| `name` | no | Root only. The name of the project. Default: the name of the root folder. Every root manifest SHOULD set it: generated files contain the name, so without it a copy in a folder of another name has stale generated files. |
| `ignore` | no | Root only. A list of folders, relative to the root, that are not searched for units. |
| `diagrams` | no | Root only. `parents` (default), `all` or `none` (section 6). |
| `diagram-links` | no | Root only. How boxes in diagrams link: `none` (default), `relative`, or a base URL. |
| `max-lines` | no | Root only. The line limit for documents at level `full`. Default: 200. |

An entry of `capabilities` or `needs` is a string, its summary, or a mapping
with these keys:

| Key | Required | Meaning |
|---|---|---|
| `summary` | yes | One line: what the capability offers, or what the need expects. `TODO` and `<...>` as for the unit. |
| `kind` | no | Free text for the technical nature, for example `library`, `http`, `events`, `cli`. |
| `contract` | no | Where the exact definition is: a URL, or a path. A path is relative to the folder of the manifest, MAY point anywhere inside the project, and MUST exist. |
| `verified-by` | no | What checks the entry against its contract, for example tests: a URL or a path, as for `contract`. Leaving it out is never a finding. |
| `conforms-to` | no | On a capability: the name of a need of the same unit. The capability implements the definition that the unit receives through that need. |
| `optional` | no | On a need only: `true` if the need may stay unconnected. Default: `false`. |

The name of a capability or need consists of letters, digits, `-` and `_`,
starts with a letter or a digit, and is local to the unit. A folder name
MAY contain dots. No unit lies in a folder whose name starts with a dot, or
in the `docs` folder of a unit. A manifest does not list child units or
users.

## 3. Wiring

`wiring` is a mapping. The key is a need, the value is its provider: "this
need is met by that provider". A reference is a bare name, which is an
entry of the unit itself, or `child.name`, which is an entry of a direct
child. A reference is split at its last dot. `child` is the folder name of
the child, or its path relative to the unit (`"a/utils.capability"`); the
path MUST be used when two children have the same folder name.

| Key | Value | Meaning |
|---|---|---|
| `child.need` | `sibling.capability` | Another child provides for the need. |
| `child.need` | `own-need` | The need is passed up: whatever meets this unit's own need meets it. |
| `own-capability` | `child.capability` | A child implements a capability of this unit. |
| `child.need` | `./folder` | A plain folder of this unit provides; `./` alone means the code of this unit itself. It marks code that is not yet described as a unit. |
| `child.need` | `{name: provider, ...}` | Named alternatives, each in one of the forms above. The first is the default. |

1. **One level.** Wiring names only entries of the unit itself and of its
   direct children. It MUST NOT name anything deeper.
2. **Complete.** Every need of every child MUST be connected, unless it is
   `optional`. The provider is, in this order: (a) a line whose key names
   that child and need; (b) **implicit pass-up:** if the unit itself
   declares a need of the same name, the child's need is connected to it.
   Otherwise the need is unconnected, which is an error.
3. **Sides.** A key is a need of a child or a capability of the unit. A
   value is a capability of a child or, for a need only, a need of the unit
   or a folder. A child that provides for its own need is an error.
4. **Alternatives.** A need has one provider at a time. The build or the
   deployment decides which alternative is in use; this standard does not
   describe configurations. Every alternative MUST meet all that the need
   expects.
5. **Kinds.** A need and its provider SHOULD have the same `kind`. A
   difference is reported only when both state a kind.
6. **Direction.** A connection records a dependency, not the direction in
   which data flows. A subscriber needs the stream; the publisher provides.
7. **Final provider.** Who finally provides for a need, or uses a
   capability, is found by following needs up and capabilities down.

## 4. Levels

| Level | Required per unit | Checked |
|---|---|---|
| `core` | `unifold.yaml` | Manifests, wiring, generated files, the comparison with code (section 7), and that the paths named in manifests exist. Nothing reads or constrains `README.md` or any other prose. |
| `full` | also `README.md`; `AGENTS.md` is generated (section 6) | In addition, the conventions of [documents.md](documents.md), for the files of that unit. A single unit MAY be at `full` while the rest stays at `core`. |

## 5. What a checker guarantees

A conforming checker reads a project, changes nothing, and reports findings
with a severity: `error`, `warn` or `info`. It MUST report at least:

| Finding | Severity |
|---|---|
| A manifest that is not valid: not a YAML mapping, an unknown key, a wrong type, no `summary`; a root without `unifold` | error |
| A wiring reference to a child, capability or need that does not exist, or that is on the wrong side | error |
| A need of a child that is not `optional` and not connected | error |
| A path in a manifest that does not exist or leaves the project | error |
| A generated file that is missing, or differs from what the generator would write now | error |
| A dependency found in code that no connection covers (section 7) | error |
| A connection for which no dependency is found in code (section 7) | warn |
| `summary: TODO` | warn |

No error means consistent, not correct: no checker judges whether a summary
is true. Reference tool: [tool.md](tool.md), [rules.md](rules.md).

## 6. Generated files

Diagrams are generated from the manifests. They MUST NOT be drawn or edited
by hand. A diagram is Markdown with a Mermaid flowchart and the same content
as tables. Every generated file starts with a comment that begins with
`<!-- unifold:generated`, which counts only at a path the generator writes.

| File in the unit | Shows | Written for |
|---|---|---|
| `docs/diagrams/component.md` | The children of the unit and the connections between them. | Units that have children. |
| `docs/diagrams/context.md` | The unit inside the frame of its parent, with the siblings it is connected to; tables of the final provider of each need and the final users of each capability. | Units that have children and a parent. |
| `docs/diagrams/architecture.md` | The unit opened up three levels deep. | Units whose children have children. |
| `AGENTS.md` | Where the documents and skills of the unit are, for coding agents; at the root also the unifold block with the index of units. | Units at level `full`. |

- `diagrams: all` also writes `context.md` for units without children;
  `diagrams: none` writes no diagram.
- An arrow points from the unit that needs to the unit that provides. A
  need that three or more children pass up by name is listed once below the
  picture. A `planned` unit is marked.
- Generated links are URL-encoded. Generated files SHOULD be committed.

## 7. Comparison with dependencies in code

Manifests can agree with each other and still be wrong. A checker therefore
compares the wiring with dependencies observed in the code. Each has `from`
and `to`, paths of files or folders relative to the root, and optionally
`kind` and `evidence`, which say how and where it was found:

```json
[{"from": "billing", "to": "platform", "kind": "cargo", "evidence": "billing/Cargo.toml"}]
```

- Each path belongs to the nearest unit at or above it. A path that does
  not exist is an error. A dependency inside one unit is ignored.
- A dependency from unit A to unit B is covered when a need of A, or of a
  unit between A and their nearest common ancestor, is connected to a
  capability of B, or of a unit between B and that ancestor.
- A dependency on code of an ancestor that lies in no child unit is covered
  by a `./folder` or `./` line for a folder that contains the target. Code
  of a unit itself MAY depend on anything below that unit.
- A dependency that only tests have, such as a dev-dependency, has a `kind`
  that ends in `-dev`. It counts as observed and never needs a connection.
- Any other dependency that is not covered is an error. A connection with
  no observed dependency, between two units whose dependencies are both
  extracted, is a warning. The comparison is per pair of units, not per capability.

A checker SHOULD extract dependencies itself from build files it
understands, and MUST accept a list in this format ([tool.md](tool.md)).

## 8. Nested projects

A folder below the root whose manifest has the key `unifold` is the root of
a nested project. It is a separate project, checked on its own. The outer
project does not treat it as a child: nothing is wired to it.

## 9. Conformance

- A project conforms to unifold 0.1 when a conforming checker reports no
  error for it, with the comparison of section 7 switched on. It MAY then
  say "This repository follows unifold 0.1", and add "at level full" if the
  root manifest sets `level: full`. Warnings do not break conformance.
- A tool conforms when it accepts and rejects the same manifests as this
  page, connects needs as section 3 says, and reports the findings of
  section 5. [tool.md](tool.md) says how to test another implementation.
