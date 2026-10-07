# The manifest

The manifest is the single place where structure is declared. Diagrams, tables
and checks are derived from it. A machine-readable schema is in
[manifest.schema.json](manifest.schema.json).

## Where it lives

A unit has exactly one manifest, in one of two places:

- as YAML front matter at the top of the unit's `README.md`, or
- as a file `unit.yaml` next to the `README.md`.

`unit.yaml` is the usual place. It keeps the `README.md` plain Markdown for
code hosts and package registries, lets an editor check the manifest against
the schema, and gives tools and agents a small file to read. Front matter
keeps the declaration and its explanation in one file; use it where the
`README.md` is read only inside the repository
([coexistence.md](coexistence.md)). A folder is a unit when it has a
`unit.yaml`, or a `README.md` whose front matter contains the key `unit`.

## Example

```yaml
unit: cloud
summary: Stores readings and turns them into alerts
kind: system
status: planned
owner: backend team
provides:
  public-api:
    kind: http
    summary: Upload readings and query plants and alerts
    contract: doc/references/public-api.md
    verified-by: tests/api
needs:
  push-service:
    kind: http
    summary: Delivers a notification to a phone
wiring:
  public-api: gateway.public-api
  gateway.ingest: ingest.ingest-api
  alerts.push: push-service
```

## Fields

| Field | Required | Meaning |
|---|---|---|
| `unit` | yes | Name of the unit. MUST equal the folder name. For the root unit it is the project name. |
| `summary` | yes | What the unit is, in one line without a final full stop. |
| `kind` | no | What sort of thing the unit is, one word. Suggested: `system`, `service`, `library`, `app`, `firmware`, `tool`, `test`, `adapter`, `specification`, `infrastructure`. |
| `status` | no | `planned`, `active` or `deprecated`. Default: `active`. |
| `owner` | no | The team or person responsible. Inherited by the units below until one of them sets its own. |
| `provides` | no | Provided ports, keyed by port name. |
| `needs` | no | Needs, keyed by port name. |
| `wiring` | no | Connections inside this unit. See [wiring.md](wiring.md). |
| `x-...` | no | Any key that starts with `x-` is the project's own and is ignored by the standard. |

Only in the root manifest:

| Field | Required | Meaning |
|---|---|---|
| `youmedoc` | yes | Version of the standard, `"0.1"`. Its presence marks a project root. |
| `level` | no | `core` or `full` (default). At `core` only the rules of [core.md](core.md) apply. |
| `ignore` | no | List of folders, relative to the root, that are not scanned for units. |
| `diagram-links` | no | How boxes in generated diagrams link: `none` (default), `relative`, or the base URL of the repository's file view. See [diagrams.md](diagrams.md). |

Any other key is an error. It is usually a typing mistake.

### Names

- A unit name consists of letters, digits, `-` and `_` and starts with a
  letter or digit. It contains no dot, because the dot separates unit and port
  in the wiring. A folder whose name does not fit cannot be a unit.
- A port name consists of lower-case letters, digits and `-`.
- Children of one unit MUST have different names, also when plain folders lie
  between them and the parent.
- Port names are local to a unit.
- Prefer unit names that are not everyday words of the project. A unit named
  `store` or `server` is hard to tell from the ordinary word in running text.

### status

| Value | Meaning |
|---|---|
| `planned` | The documents describe an intention. Code is missing or incomplete. |
| `active` | The code exists, and the checks named by `verified-by` pass. |
| `deprecated` | Still present, to be removed. `README.md` says what replaces it. |

## provides

| Key | Required | Meaning |
|---|---|---|
| `summary` | yes | One line: what the port offers. |
| `kind` | no | The technical nature of the port, see below. |
| `contract` | no | Where the exact definition lives: a path inside the unit, or a URL. |
| `verified-by` | no | What holds the unit to the contract: a path inside the unit to tests or to a catalogue of checks, or a URL. Expected for every port of an `active` unit; a `planned` unit omits it until the checks exist. |
| `conforms-to` | no | The name of a need of the same unit. Says that this port implements the definition the unit receives through that need, for example a protocol defined by a `specification` unit. Two alternatives that conform to the same definition can replace each other. |

`contract` points to the most precise description that exists: an OpenAPI or
AsyncAPI file, a Protobuf or WIT file, a JSON Schema, a header file, the
public entry file of a library, or a Markdown reference in
`doc/references/`; for a split reference, its `index.md`. Before code exists
it points to the Markdown reference. For a port that is delegated to a child,
see "Delegated ports" in [unit-files.md](unit-files.md).

## needs

| Key | Required | Meaning |
|---|---|---|
| `summary` | yes | One line: what the unit expects from the provider. |
| `kind` | no | The technical nature, see below. |
| `optional` | no | `true` if the need may be left unwired. The `README.md` says what the unit does then. Default: `false`. |
| `contract` | no | The interface the unit expects, defined by the unit itself: a path inside the unit, or a URL. |

A need is written from the point of view of the unit that has it, in the
unit's own words. It never names the provider. A need with a `contract` is an
interface the unit owns: providers are held to it
([principles.md](principles.md)). The needs of the root unit are what the
project requires from the outside world: external services, hardware, people.

### What is a need and what is not

Declare a need when the thing is provided by another unit of the project,
when a stand-in can replace it, or when it is an external system the project
depends on by contract.

Do not declare a need for what every unit of that kind has anyway: the
language runtime, the standard library, the operating system, packages the
build system fetches, logging and similar utilities. A need that every unit
would have to declare belongs in a convention of the root unit, not in every
manifest.

## kind of a port

Free text, one word. A need and its provider SHOULD have the same kind; the
checker warns when they differ (`W4`). Suggested values:

| Kind | Typical meaning |
|---|---|
| `library` | Functions or types linked into the same program |
| `http`, `grpc` | A request and response API over the network |
| `events` | A stream of messages the provider publishes |
| `queue`, `db`, `storage` | A piece of infrastructure the provider operates |
| `cli`, `ui` | A command line; a user interface for people |
| `file` | A file or a file format the provider produces |
| `protocol` | A wire protocol the provider speaks |
| `specification` | A definition others implement or conform to |
| `hardware` | A physical part, signal or bus |
| `config` | Settings the provider supplies |

`contract` and `verified-by` are paths, not links. They may point anywhere
inside the unit, also into a child, for example to the test catalogue of a
child that verifies a promise of the whole.

The `kind` of a unit names its role, not its packaging: a unit that
translates between a need and a technology is an `adapter`, also when it is
built as a library.

## What the manifest does not contain

- No description of how the unit works inside.
- No list of users of the unit, and no list of child units. The folder tree
  is that list.
- No version numbers and no build information.
