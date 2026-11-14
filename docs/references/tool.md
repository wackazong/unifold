# The reference tool

`unifold` is one Python file, [unifold.py](../skills/unifold/scripts/unifold.py). It checks a project against the [standard](spec.md), draws the diagrams, and answers questions about the map. Its findings: [rules.md](rules.md). Its JSON: [tool-json.md](tool-json.md). What it writes: [tool-output.md](tool-output.md). `init`, hooks, continuous integration and how to test another implementation: [tool-setup.md](tool-setup.md).

## Running it

It needs Python 3.9 or newer and PyYAML, and is published on PyPI as [unifold](https://pypi.org/project/unifold/):

```sh
uvx unifold check                                      # run it without installing
uv tool install unifold                                # or install the command (pipx install unifold works too)
uv run docs/skills/unifold/scripts/unifold.py check    # or run the copy that init --agents installs
```

The examples below write `unifold`. `PATH` is any folder inside the project (default: the current folder).

## Commands

| Command | Effect |
|---|---|
| `init [DIR] [--agents]` | Starts a project in `DIR`: writes the root manifest and a `README.md` from the template where there is none, then the generated files. Changes no existing manifest. |
| `check [PATH]` | Reports findings. Changes nothing, unless `--fix` is given: then it first writes the decision indexes, the root `AGENTS.md` and the skill stubs where their folders exist. |
| `show [PATH]` | One unit: responsibility, kind, not, capabilities, needs, who finally provides and uses them, with status, the scenarios that pass through it, and its documents, skills and decisions. |
| `capability PATH NAME` | Both ends of every connection of one capability or need, with summaries and contracts. |
| `impact PATH [CAPABILITY]` | Every unit that depends on the unit or capability, transitively, and the context items that cite its files. For a file, also one that is deleted already, every link that cites it, with file and line. |
| `brief [PATH]` | What to implement in the unit: the parts of its capabilities with signatures, fields and examples, the fakes of its needs, the qualities and states of its contracts, the scenarios through it, its constants and its context items ([below](#brief-and-trace)). |
| `trace [PATH] [--tests GLOB] [--strict] [--active]` | Which examples of the contracts of the unit's capabilities a file below the unit names by id, and which none does ([below](#brief-and-trace)). |
| `tree [PATH] [--depth N]` | The unit tree with status, kind, capabilities and needs. |
| `model [PATH]` | The resolved model of the project as JSON: every unit, connection, final provider, scenario and decision. For tools that build on the map. |
| `explore [PATH] [-o FILE\|DIR] [--no-open] [--mermaid URL\|FILE]` | Writes the explorer, one HTML page with the map and every document, and opens it in a browser. |
| `rules [ID]` | Prints the rule table, or one rule with its fix. |

Every command accepts `--json`. With `--json`, a failure also prints JSON ([tool-json.md](tool-json.md)).

| Exit code | Meaning |
|---|---|
| 0 | No error (with `--strict`: no warning either) |
| 1 | Findings; or `check --fix` refused to overwrite a hand-written file |
| 2 | Cannot run: wrong usage, no project, root manifest unusable for this command, file not writable |
| 3 | Internal error. `UNIFOLD_DEBUG=1` shows the traceback. |

## check

| Option | Effect |
|---|---|
| `--fix` | First writes every generated file, then checks. |
| `--strict` | Warnings fail too. |
| `--quiet`, `-q` | No info findings, no fix hints. |
| `--format json`, `--format github` | Prints JSON, the same as `--json`; or workflow commands, which GitHub shows on the changed lines. |
| `--rule ID` | Reports only this rule. Repeatable. |

One line per finding, then a summary:

```text
error W2 cloud/unifold.yaml:14: need 'alerts.push' has no provider
    fix: Add `alerts.push: <provider>` to the wiring of this manifest, or declare a need `push` here and pass it up (`alerts.push: push`).
12 unit(s): 1 error(s), 0 warning(s), 0 info  [W2×1]
```

A finding has a severity, the rule, the file to change with the line, what is wrong, and how to fix it. `unifold rules W2` prints one rule; [rules.md](rules.md) lists them all.

| Severity | Meaning | Effect on `check` |
|---|---|---|
| `error` | The map is inconsistent. | Exit code 1. |
| `warn` | Something that makes a map better but is not needed for consistency. A person decides. | Exit code 1 only with `--strict`. |
| `info` | A fact worth knowing. | None. Hidden by `--quiet`. |

`M1` and `S1` come first; the rest is sorted by file and line. A manifest that does not parse gives one `M1`, and no wiring finding is reported for the lines that name its unit. A root manifest that does not parse, or states another version than 0.4, gives one `M1` or `S1` and nothing else.

A project may add checks of its own in its build. It should not silence a rule by weakening a manifest, for example by marking a need `optional`. Where a rule cannot be followed in one place, a reference of the root unit says so, so that reviewers see the exception.

Generated files are built in memory and compared, so a stale decision index, `AGENTS.md` or skill stub is an error; `check --fix` repairs it.

## brief and trace

`unifold brief UNIT` prints what an implementer of the unit needs, from the contracts and the manifests: under `implement`, every part of every capability with its signature, `Pre:`, `Result:`, the error cases and the examples with their ids; under `fake, for your tests`, every need with the parts it uses and the `## Fake` of its contract; the `## Qualities` and `## States` of each contract; the scenarios that pass through the unit, with the hops that touch it marked; the rows of the nearest `constants.md`; and the items of `context.md`. `--json` gives the same as data.

`unifold trace UNIT` searches the files below the unit, outside `docs/`, for the ids of the examples of the contracts of its capabilities, `<contract>#<part>/<case-slug>`. It reads text and parses no code, so it works for every language; a test names the id in its name or in a comment. It reports `X1` (info) for an example that no file names and `X2` (warn) for an id that no example has. `--tests GLOB` limits the search to files whose path or name matches; `--strict` turns `X1` into a failure. The exit code is 1 on `X2`, and on `X1` with `--strict`. `--active` traces every unit of status `active` at and below `PATH`, each over its own files, and skips the others; a build runs `unifold trace --active --strict` ([setup](tool-setup.md#hooks-and-continuous-integration)). The procedure [implement a unit](../skills/unifold/procedures/implement-a-unit.md) uses both.

## What the tool does not read

- Code, in whatever language. The tool reads `unifold.yaml` files and Markdown documents; `trace` searches text files for example ids and parses nothing.
- The folders that [spec.md](spec.md#2-the-manifest) lists as not searched. What version control ignores is what git ignores: `.gitignore`, `.git/info/exclude` and the global excludes; a committed file is read even if a pattern matches it. List third-party code that is committed under `ignore` in the root manifest.
- Nested projects, for example a submodule with a root manifest of its own. `tree` lists them; they are checked on their own.
- Markdown files other than those named in [documents.md](documents.md), and text inside code blocks.
- The meaning of a responsibility, a contract or a context item. What it reads of a document is listed in [spec-conformance.md](spec-conformance.md#5-documents).
