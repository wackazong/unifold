# The manifest

The manifest is the YAML front matter at the top of a unit's `README.md`. It
is the single place where structure is declared. Diagrams, tables and checks
are derived from it. A machine-readable schema is in
[manifest.schema.json](manifest.schema.json).

## Example

```yaml
---
unit: cloud
summary: Stores readings and turns them into alerts
kind: system
status: planned
provides:
  public-api:
    kind: http
    summary: Upload readings and query plants and alerts
    contract: doc/references/public-api.md
needs:
  push-service:
    kind: http
    summary: Delivers a notification to a phone
wiring:
  public-api: gateway.public-api
  gateway.ingest: ingest.ingest-api
  alerts.push: push-service
---
```

## Fields

| Field | Required | Type | Meaning |
|---|---|---|---|
| `unit` | yes | name | Name of the unit. MUST equal the folder name. For the root unit it is the project name. |
| `summary` | yes | one line | What the unit is, in one sentence without a final full stop. Shown in generated tables. |
| `youmedoc` | root only | string | Version of the standard, for example `"0.1"`. Its presence marks a project root. |
| `kind` | no | word | What sort of thing the unit is. Free vocabulary, see below. |
| `status` | no | word | `planned`, `active` or `deprecated`. Default: `active`. |
| `provides` | no | map | Provided ports, keyed by port name. |
| `needs` | no | map | Needs, keyed by port name. |
| `wiring` | no | map | Connections inside this unit. See [wiring.md](wiring.md). |

Other top-level keys SHOULD NOT be used. The checker warns about them.

### Names

- A unit name consists of letters, digits, `-` and `_` and starts with a
  letter or digit. It contains no dot, because the dot separates unit and port
  in the wiring. A folder whose name does not fit cannot be a unit.
- A port name consists of lower-case letters, digits and `-`.
- Children of one unit MUST have different names, also when plain folders lie
  between them and the parent.
- Port names are local to a unit. Two units may both have a port `events`.
- Prefer unit names that are not everyday words of the project. A unit named
  `store` or `server` is hard to tell from the ordinary word in running text.

### status

| Value | Meaning |
|---|---|
| `planned` | The documents describe an intention. Code is missing or incomplete. |
| `active` | The code exists and the documents describe it. |
| `deprecated` | Still present, to be removed. `README.md` says what replaces it. |

### kind of a unit

Free text, one word. Suggested values: `system`, `service`, `library`, `app`,
`firmware`, `tool`, `test`, `specification`, `infrastructure`.

## provides

Each entry describes one provided port.

| Key | Required | Meaning |
|---|---|---|
| `summary` | yes | One line: what the port offers. |
| `kind` | no | The technical nature of the port, see below. |
| `contract` | no | Where the exact definition lives: a path inside the unit, or a URL. |

`contract` points to the most precise description that exists: an OpenAPI or
AsyncAPI file, a Protobuf or WIT file, a JSON Schema, a header file, the
public entry file or folder of a library, or a Markdown reference in
`doc/references/`. Before code exists it points to the Markdown reference. The
path MUST stay inside the unit. For a reference that is split into a folder,
it points to the `index.md`. For a port that is delegated to a child, see
"Delegated ports" in [unit-files.md](unit-files.md).

## needs

Each entry describes one need.

| Key | Required | Meaning |
|---|---|---|
| `summary` | yes | One line: what the unit expects from the provider. |
| `kind` | no | The technical nature, see below. |
| `optional` | no | `true` if the unit works without it. Default: `false`. |

A need is written from the point of view of the unit that has it. It states
the expectation in the unit's own words. It never names the provider.

The needs of the root unit are the things the whole project requires from the
outside world: external services, hardware, people.

## kind of a port

Free text, one word. A need and its provider SHOULD have the same kind; the
checker warns when they differ. Suggested values:

| Kind | Typical meaning |
|---|---|
| `library` | Functions or types linked into the same program |
| `http`, `grpc` | A request and response API over the network |
| `events` | A stream of messages the provider publishes |
| `queue`, `db`, `storage` | A piece of infrastructure the provider operates |
| `cli` | A command line |
| `ui` | A user interface for people |
| `file` | A file or a file format the provider produces |
| `protocol` | A wire protocol the provider speaks, for example over BLE or serial |
| `specification` | A definition others implement or conform to |
| `hardware` | A physical part, signal or bus |
| `config` | Settings the provider supplies |

A project may add its own kinds. It SHOULD list them in a reference of the
root unit.

## What the manifest does not contain

- No description of how the unit works inside.
- No list of users of the unit.
- No list of child units. The folder tree is that list.
- No version numbers and no build information. Those belong to the build
  system.

## Changing a manifest

A change to `provides` or `needs` changes the interface of the unit. Follow
the procedure in [workflow.md](workflow.md): change the child, then the
parent's wiring, then run the checker and regenerate.
