# The checker and generator

The standard comes with a reference tool. It is one Python file,
[unifold.py](../../skills/check-docs/scripts/unifold.py), shipped inside
the [check-docs](../../skills/check-docs/SKILL.md) skill, so every project
that carries the standard also carries the tool. It reads the
[manifests](manifest.md) and the Markdown files. It does not read code.

## Running it

The tool needs Python 3.9 or newer and the PyYAML package. With `uv`, nothing
has to be installed; the file declares its dependency:

```sh
uv run doc/skills/check-docs/scripts/unifold.py check
```

Otherwise install PyYAML once (`python3 -m pip install pyyaml`) and call the
file with `python3`, on Windows with `py -3`. The examples below shorten the
call to `unifold`.

## Commands

| Command | Effect |
|---|---|
| `unifold check [PATH]` | Checks the project against the [tool rules](rules-tool.md). Changes nothing. |
| `unifold generate [PATH]` | Writes all generated Markdown files: diagrams and decision indexes. |
| `unifold show [PATH]` | Describes the unit that contains `PATH`: ports, who finally provides each need, who finally uses each port, parent, children, skills, decisions, files. |
| `unifold port PATH NAME` | Prints both ends of every connection of one port or need: the section of each `README.md` and the contracts. This is the comparison that review rule `C13` asks for. |
| `unifold stats [PATH]` | Counts hand-written files, words and context items per unit, wiring lines, ports with contracts and verification, and decisions by status. |
| `unifold tree [PATH]` | Prints the unit tree with status and ports. |
| `unifold skills [PATH]` | Lists every skill of the project with its unit and description. |
| `unifold decisions [PATH]` | Lists every decision of the project; `--status proposed` filters. |
| `unifold cited-by FILE` | Lists the managed files that link to `FILE`, for example the context files that restate a decision. |
| `unifold site [PATH]` | Writes the interactive HTML explorer ([diagrams.md](diagrams.md)); `-o FILE` sets the output, default `unifold.html` in the project root. |
| `unifold init TARGET` | Starts a project in `TARGET`: copies the standard, writes `unit.yaml`, `README.md` and `AGENTS.md` where they are missing, and generates, so that `check` is clean at once. In an existing project it replaces the copy of the standard. With `--level core` it copies nothing and writes only `unit.yaml` and `README.md`. |

`PATH` is any folder inside the project and defaults to the current folder.
The tool walks upward until it finds the root manifest.

`check`, `show`, `tree`, `stats`, `skills` and `decisions` accept `--json`
and then print JSON instead of text. `check` also accepts `--strict` (exit
code 1 on warnings too), `--quiet` (no info findings) and `--deps FILE`.

## check --deps: comparing the wiring with the code

The tool does not read code. A project can tell it what the code depends on,
and the tool compares that with the wiring (rules `D1` and `D2`):

```sh
unifold check --deps deps.json
```

`deps.json` is a list of observed dependencies between files or folders,
with paths relative to the project root:

```json
[{"from": "cloud/services/ingest/src/main.rs", "to": "cloud/platform/src/bus.rs"}]
```

How the list is produced depends on the language: from the build system's
dependency graph, from an import scanner, from a compiler report. unifold
defines only this format. A dependency inside one unit is ignored. A
dependency from one unit to another is allowed when a need of the first, or
of one of its ancestors below the common parent, is wired to the second.

## show: the neighbourhood of a unit

`show` answers in one call what would otherwise take reading the manifests of
several ancestors:

```text
unit      rules  (cloud/services/alerts/rules)
summary   Evaluates readings against the thresholds of a plant
status    planned · library
parent    cloud/services/alerts
provides
  evaluation (library)  contract doc/references/evaluation.md
      used by cloud/services/alerts/server as need 'evaluation'
needs
  thresholds (library)
      provided by cloud/services/alerts/plant-lookup port 'thresholds'
```

The same resolution is written into every unit's generated
`doc/diagrams/context.md`.

## Output of check

One line per finding, then a summary:

```text
E W2 cloud/README.md: need 'alerts.push' is not wired
W W3 cloud/README.md: 'platform.sql-db' is provided but nothing needs it
18 unit(s): 1 error(s), 1 warning(s), 0 info. Review rules C1 to C15 are not checked by this tool.
```

The fields are severity, rule ID, file and message. Rule IDs are explained in
[rules-tool.md](rules-tool.md).

| Exit code | Meaning |
|---|---|
| 0 | No errors (and no warnings, with `--strict`) |
| 1 | Errors found |
| 2 | No project found, or the root manifest is unusable |

## Order of use

`README.md` and `AGENTS.md` link to generated files. In a new unit these
links are broken until the generator has run. Therefore: first `generate`,
then `check`.

## What the tool ignores

- Folders whose name starts with a dot, the folders `node_modules`, `target`
  and `__pycache__`, and the folders listed under `ignore` in the root
  manifest.
- Nested projects. They are listed by `tree` and checked on their own.
- Entries of `doc/` that the standard does not define, and Markdown files
  outside the managed set ([markdown.md](markdown.md)).
- Links inside code blocks and code spans, anchors, and external URLs.

## What the tool cannot do

- It does not check the [review rules](rules-review.md).
- It does not compare the documents with the code.
- It finds a mention of another unit only if it is a link or written in code
  font.

## In continuous integration and before a commit

```sh
uv run doc/skills/check-docs/scripts/unifold.py check --strict --quiet
```

With `--strict`, a stale generated file (`G1`) fails the build. This keeps
the committed diagrams in step with the manifests. As a pre-commit hook, run
`generate`, add the changed generated files, then run `check`.

As a GitHub Actions job:

```yaml
jobs:
  unifold:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 -m pip install pyyaml
      - run: python3 doc/skills/check-docs/scripts/unifold.py check --strict --quiet
```

## Other implementations

The tool is a reference implementation. Its test cases are data: each case is
a small project with the findings it must produce. Another implementation
conforms if it reports the same rule IDs for the same cases and generates
diagrams that show the same units, ports and connections.
