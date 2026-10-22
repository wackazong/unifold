# The reference tool

`unifold` is one Python file,
[unifold.py](../../skills/unifold/scripts/unifold.py). It checks a project
against the [standard](spec.md), compares the wiring with the dependencies
it finds in code, generates the diagrams, and answers questions about the
map. Its findings: [rules.md](rules.md). Its JSON: [tool-json.md](tool-json.md).

## Running it

It needs Python 3.9 or newer and PyYAML. The package is not published yet.
Until it is, run the file from a clone; `uv` installs PyYAML by itself:

```sh
uv run docs/skills/unifold/scripts/unifold.py check     # or: python3 ... with PyYAML installed
uvx --from . unifold check                             # from a clone, as the installed command
```

Once published: `uvx unifold check`. The examples below write `unifold`.
`PATH` is any folder inside the project (default: the current folder).

## Commands

| Command | Effect |
|---|---|
| `init [DIR] [--agents]` | Starts a project in `DIR`: writes the root manifest if there is none, then the generated files. Changes no existing manifest. |
| `check [PATH]` | Reports findings. Changes nothing, unless `--fix` is given. |
| `generate [PATH]` | Writes diagrams, decision indexes and, at level `full`, `AGENTS.md`; refreshes skill stubs and the root block where they exist. |
| `show [PATH]` | One unit: capabilities, needs, who finally provides and uses them, with status. |
| `capability PATH NAME` | Both ends of every connection of one capability or need, with contracts and README sections. |
| `impact PATH [CAPABILITY]` | Every unit that depends on the unit or capability, transitively, and the context items that cite its files. |
| `tree [PATH] [--depth N]` | The unit tree with status, capabilities and needs. |
| `deps [PATH] [--write FILE]` | The dependencies between folders that the extractors find, as JSON. |
| `stamp [PATH]` | Writes or refreshes the stamps of the context items at or below `PATH`, and prints each with file, line and the source it cites. |
| `cited-by FILE` | Context items and links that cite `FILE`, with line and `Says` text. `FILE` may be deleted already. |
| `skills [sync] [PATH]` | Lists all skills; `sync` writes stubs into `.agents/skills` and `.claude/skills` ([agents.md](agents.md)). |
| `site [PATH] [-o FILE]` | Writes the HTML explorer. |
| `rules [ID]` | Prints the rule table, or one rule with its fix. |
| `mcp [PATH]` | Serves `show`, `capability`, `impact`, `check` and `tree` over MCP. |

Every command except `mcp` accepts `--json`. With `--json`, a failure also
prints JSON ([tool-json.md](tool-json.md)).

| Exit code | Meaning |
|---|---|
| 0 | No error (with `--strict`: no warning either) |
| 1 | Findings; or `generate` refused to overwrite a hand-written file |
| 2 | Cannot run: wrong usage, no project, root manifest unusable for this command, file not writable |
| 3 | Internal error. `UNIFOLD_DEBUG=1` shows the traceback. |

## check

| Option | Effect |
|---|---|
| `--fix` | First writes what `generate` would write, then checks. It writes no stamp. |
| `--strict` | Warnings fail too. |
| `--quiet`, `-q` | No info findings, no fix hints. |
| `--format github` | Prints workflow commands; GitHub shows them on the changed lines. |
| `--deps FILE` | Adds observed dependencies from a list. |
| `--no-deps` | Does not read code. With `--deps`, only the list counts. |
| `--rule ID` | Reports only this rule. Repeatable. |

One line per finding, then a summary:

```text
error W2 cloud/unifold.yaml:14: need 'alerts.push' has no provider
    fix: Add `alerts.push: <provider>` to the wiring of this manifest, or declare a need `push` here to pass it up.
12 unit(s): 1 error(s), 0 warning(s), 0 info  [W2×1]; 19 dependencies observed in code
```

Generated files are built in memory and compared, so a stale diagram is an
error; `check --fix` repairs it. `--fix` never adds or refreshes a stamp:
only `unifold stamp` does, after you have compared `Says` with the source.

## Dependencies from code

`check` reads build files and imports and compares the result with the
wiring ([spec.md](spec.md), section 7). `unifold deps` prints what it found.

| Ecosystem | Recognised by | A dependency is | `kind` |
|---|---|---|---|
| Cargo | `Cargo.toml` with `[workspace]` or `[package]` | a `path` dependency, also through `workspace = true`; it belongs to the folder below the package that holds all its `[lib]` and `[[bin]]` sources, if there is one | `cargo`; `cargo-dev` for dev-dependencies |
| npm, pnpm, yarn | `workspaces` in `package.json`, `pnpm-workspace.yaml`, `lerna.json` | a dependency of any sort on a package of the workspace, or a `file:` or `link:` path | `npm` |
| Go | `go.mod` | an import of another folder of the same or another module of the repository | `go`; `go-dev` from `_test.go` files |
| Python | `pyproject.toml`, `setup.py`, `setup.cfg`, folders with `__init__.py` | an import, absolute or relative, that resolves to another folder of the repository | `python`; `python-dev` from test files |

- Cargo and npm give one entry per pair of packages, Go and Python one per
  pair of folders, each with its `evidence`.
- A kind that ends in `-dev` exists only in tests: listed, never demanding wiring.
- Not read: packages outside a workspace, `testdata`, `vendor`,
  `third_party`, `node_modules`, ignored folders, nested projects. An import
  that could mean two packages of the repository is not guessed.
- TOML is read with `tomllib` (Python 3.11), else `tomli`, else a built-in
  reader; a file it cannot read is reported as a note and skipped.

For dependencies no extractor sees, such as calls between services, pass a
list. It adds to what is extracted:

```json
[{"from": "src/checkout", "to": "src/cart", "kind": "grpc", "evidence": "k8s env CART_ADDR"}]
```

`from` and `to` are files or folders, relative to the root; `kind` and
`evidence` are optional. A path that does not exist is an error. `unifold
deps --write deps.json` writes the extracted list in the same format.

## init

`unifold init` starts a project. If `DIR` has no `unifold.yaml`, it writes
the root manifest: the version of the standard, `name` from the folder
name, and `summary: TODO`, which `check` reports until a person has
written it. Then it runs `generate`. A project of one unit conforms.

`init` reads no code and writes no other manifest. The units of an
existing repository are a judgement about its architecture; a build file
knows packages, not units. A person makes that judgement, or an agent with
the skill `unifold-convert` ([first map](../../tutorials/first-map.md));
`check` then compares the result with the dependencies in the code.

`init --agents` also installs the skills `unifold` and `unifold-convert`
into `docs/skills/` (text, templates and this tool), runs `skills sync`,
and writes a marked block into the root `AGENTS.md`: about 15 lines, plus
one row per unit in projects up to 40 units; at level `full` the whole root
file is generated and the block is part of it. `generate` keeps the block
and the stubs current. It prints a hint if a `CLAUDE.md` would hide
`AGENTS.md` from Claude Code.

## Generated files

`generate` writes the files of [spec.md](spec.md), section 6, and for units
at level `full` the index `docs/decisions/index.md`. It removes generated
files it no longer writes, and it never overwrites a file that lacks the
generated marker: a hand-written `AGENTS.md` at level `full` is reported
until its content has moved to `README.md` and `docs/` and the file is
deleted. Links to files that do not exist are left out.

`unifold site` writes one HTML file with the tree, all diagrams and tables.
The page loads Mermaid from a CDN and says so if it cannot; the tables work
without it. `--mermaid FILE` embeds a local `mermaid.min.js` (the page then
works offline and grows by about 5 MB); `--mermaid URL` loads it elsewhere.

## Hooks and continuous integration

GitHub Actions: after `actions/checkout`, add the step
`- uses: <owner>/unifold@<tag>` (this repository; inputs `path`, `strict`,
`args`). Findings appear as annotations on the pull request.

[pre-commit](https://pre-commit.com): this repository offers the hooks
`unifold` (check) and `unifold-fix` (rewrite generated files, then check):

```yaml
repos:
  - repo: <URL of this repository>
    rev: <tag>
    hooks: [{id: unifold-fix}]
```

A coding agent should check when it stops, not after every edit: a unit
that is half written is broken on purpose. Claude Code, in
`.claude/settings.json`:

```json
{"hooks": {"Stop": [{"hooks": [{"type": "command", "timeout": 60,
  "command": "cd \"$CLAUDE_PROJECT_DIR\" && uvx unifold check --fix --quiet >&2 || exit 2"}]}]}}
```

## MCP

`unifold mcp [PATH]` is a [Model Context Protocol](https://modelcontextprotocol.io)
server over stdio, for agents that should read the map without a shell. It
offers five read-only tools, `show`, `capability`, `impact`, `check` and `tree`,
with the arguments of the commands and their JSON as the result. It speaks
protocol versions 2024-11-05, 2025-03-26 and 2025-06-18 and needs no
further package. To register it, give the client the command `uvx unifold
mcp`, for example in `.mcp.json`.

## What the tool does not read

- Folders whose name starts with a dot, the `docs` folder of a unit,
  `node_modules`, `__pycache__`, Cargo build folders, Python virtual
  environments, symbolic links to folders, and the `ignore` folders. List
  third-party code in the tree under `ignore` in the root manifest.
- Nested projects, for example a submodule with a root manifest of its
  own. `tree` lists them; they are checked on their own. Something in
  another repository is a need of the root; no map across repositories is
  produced.
- At level `core`: any prose, so a `README.md` that a package registry
  publishes stays as it is. At level `full`: Markdown files other than
  those named in [documents.md](documents.md), and text inside code blocks.
- The meaning of a summary, a contract or a `Says` paragraph.

## Testing another implementation

[conformance.py](../../../tests/conformance.py) holds the test cases as
data: small projects with the findings that `check --json` must report, as
rule, severity and file, and scenarios for `init`, stamps, `--fix`, JSON on
failure and MCP. `python3 tests/conformance.py --tool "CMD"` runs them
against another tool; `--write DIR` writes the cases as files. An
implementation conforms when all cases pass. Cases for generated files run
without the reference generator, so a second generator is tested too.
