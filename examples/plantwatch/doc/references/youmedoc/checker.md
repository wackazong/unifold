# The checker and generator

The standard comes with a reference tool. It is one Python file,
[youmedoc.py](../../skills/check-docs/scripts/youmedoc.py), shipped inside
the [check-docs](../../skills/check-docs/SKILL.md) skill, so every project
that carries the standard also carries the tool.

The tool reads the [manifests](manifest.md) and the Markdown files. It does
not read code.

## Requirements

Python 3.9 or newer and the PyYAML package. With `uv`, no installation is
needed; the file declares its dependency:

```sh
uv run doc/skills/check-docs/scripts/youmedoc.py check
```

Otherwise:

```sh
python3 -m pip install pyyaml
python3 doc/skills/check-docs/scripts/youmedoc.py check
```

The examples below shorten the call to `youmedoc`.

## Commands

| Command | Effect |
|---|---|
| `youmedoc check [PATH]` | Checks the project that contains `PATH` against the [tool rules](rules-tool.md). Changes nothing. |
| `youmedoc generate [PATH]` | Writes all generated files: diagrams and decision indexes. Removes generated diagram files that are no longer produced. |
| `youmedoc tree [PATH]` | Prints the unit tree with status and ports. |
| `youmedoc init TARGET` | Copies the standard into `TARGET`: `doc/references/youmedoc/` and the three skills. |

`PATH` is any folder inside the project and defaults to the current folder.
The tool walks upward until it finds the root manifest.

Options of `check`:

| Option | Effect |
|---|---|
| `--strict` | Exit code 1 also when there are warnings |
| `--quiet` | Do not print info findings |

## Output of check

One line per finding, then a summary:

```text
E W2 cloud/README.md: need 'alerts.push' is not wired
W W3 cloud/README.md: 'platform.sql-db' is provided but nothing needs it
18 unit(s): 1 error(s), 1 warning(s), 0 info
```

The fields are severity, rule ID, file and message. Rule IDs are explained in
[rules-tool.md](rules-tool.md).

| Exit code | Meaning |
|---|---|
| 0 | No errors (and no warnings, with `--strict`) |
| 1 | Errors found |
| 2 | No project found, or the root manifest is unusable |

## What generate writes

| File | For |
|---|---|
| `doc/diagrams/context.md` | every unit |
| `doc/diagrams/component.md` | units with children |
| `doc/diagrams/architecture.md` | units with children |
| `doc/decisions/index.md` | units with at least one decision |

The content is described in [diagrams.md](diagrams.md). Running `generate`
twice without changes writes nothing the second time.

## Order of use

`README.md` and `AGENTS.md` link to generated files. In a new unit these
links are broken until the generator has run. Therefore:

1. `youmedoc generate`
2. `youmedoc check`

## What the tool ignores

- Folders whose name starts with a dot, and `node_modules`, `target` and
  `__pycache__`.
- Nested projects. They are listed by `tree` and checked on their own.
- Markdown files outside the managed set ([markdown.md](markdown.md)).
- Links inside code blocks and code spans, anchors, and external URLs.

## What the tool cannot do

- It does not check the [review rules](rules-review.md).
- It does not compare the documents with the code.
- It does not find mentions of other units in running text; it only sees
  links.

## Use in continuous integration

```sh
uv run doc/skills/check-docs/scripts/youmedoc.py check --strict --quiet
```

With `--strict`, a stale generated file (`G1`) fails the build. This keeps
the committed diagrams in step with the manifests.

## Other implementations

The tool is a reference implementation. Another implementation conforms if it
reports the same rule IDs for the same projects and generates diagrams that
show the same units, ports and connections.
