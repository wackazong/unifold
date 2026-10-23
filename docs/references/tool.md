# The reference tool

`unifold` is one Python file, [unifold.py](../skills/unifold/scripts/unifold.py). It checks a project against the [standard](spec.md), generates the diagrams, and answers questions about the map. Its findings: [rules.md](rules.md). Its JSON: [tool-json.md](tool-json.md).

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
| `check [PATH]` | Reports findings. Changes nothing, unless `--fix` is given. |
| `generate [PATH]` | Writes diagrams, decision indexes and the `AGENTS.md` of every unit; writes the skill stubs where their folders exist. |
| `show [PATH]` | One unit: capabilities, needs, who finally provides and uses them, with status. |
| `capability PATH NAME` | Both ends of every connection of one capability or need, with contracts and README sections. |
| `impact PATH [CAPABILITY]` | Every unit that depends on the unit or capability, transitively, and the context items that cite its files. |
| `tree [PATH] [--depth N]` | The unit tree with status, capabilities and needs. |
| `stamp [PATH]` | Writes or refreshes the stamps of the context items at or below `PATH`, and prints each with file, line and the source it cites. |
| `cited-by FILE` | Context items and links that cite `FILE`, with line and `Says` text. `FILE` may be deleted already. |
| `skills [sync] [PATH]` | Lists all skills; `sync` writes their stubs into `.agents/skills` and `.claude/skills`, and the other generated files as `generate` does ([agents.md](agents.md)). |
| `site [PATH] [-o FILE]` | Writes the HTML explorer. |
| `rules [ID]` | Prints the rule table, or one rule with its fix. |

Every command accepts `--json`. With `--json`, a failure also prints JSON ([tool-json.md](tool-json.md)).

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
| `--rule ID` | Reports only this rule. Repeatable. |

One line per finding, then a summary:

```text
error W2 cloud/unifold.yaml:14: need 'alerts.push' has no provider
    fix: Add `alerts.push: <provider>` to the wiring of this manifest, or declare a need `push` here and pass it up (`alerts.push: push`).
12 unit(s): 1 error(s), 0 warning(s), 0 info  [W2×1]
```

Generated files are built in memory and compared, so a stale diagram is an error; `check --fix` repairs it. `--fix` never adds or refreshes a stamp: only `unifold stamp` does, after you have compared `Says` with the source.

## init

`unifold init` starts a project. If `DIR` has no `unifold.yaml`, it writes the root manifest: the version of the standard, `name` from the folder name, and `summary: TODO`, which `check` reports until a person has replaced it. If `DIR` has no `README.md`, it writes one from the template of the `unifold` skill, with placeholders in angle brackets to replace; `check` reports only its two example headings. Then it runs `generate`. A hand-written `AGENTS.md` is in the way of the generated one: on a terminal `init` asks whether to replace it, otherwise it keeps the file and says so. A project of one unit conforms at once: `check` reports warnings and no error.

`init` reads no code and writes no other manifest. The units of an existing repository are a judgement about its architecture; a build file knows packages, not units. A person makes that judgement, or an agent with the skill `unifold-convert` ([first map](../tutorials/first-map.md)); `check` then says what is missing or inconsistent.

The root `AGENTS.md` always carries the unifold block: about 15 lines, plus one row per unit when the project has at most 40 units below the root. `init --agents` also installs the skills `unifold` and `unifold-convert` into `docs/skills/` (text, templates and this tool) and runs `skills sync`; the block then names the installed tool and links the skills. It prints a hint if a `CLAUDE.md` at the root does not mention `AGENTS.md`, which hides it from Claude Code.

## Generated files

`generate` writes the files of [spec.md](spec.md), section 6, and the index `docs/decisions/index.md` of every unit that has decisions. It removes generated files it no longer writes, and it never overwrites a file that lacks the generated marker: a hand-written `AGENTS.md` is reported until its content has moved to `README.md` and `docs/` and the file is deleted. Links to files that do not exist are left out.

`unifold site` writes one HTML file with the tree, all diagrams and tables. The page loads Mermaid from a CDN and says so if it cannot; the tables work without it. `--mermaid FILE` embeds a local `mermaid.min.js` (the page then works offline and grows by about 5 MB); `--mermaid URL` loads it elsewhere.

## Hooks and continuous integration

GitHub Actions: after `actions/checkout`, add the step `- uses: <owner>/unifold@<tag>` (this repository; inputs `path`, `strict`, `args`). Findings appear as annotations on the pull request.

[pre-commit](https://pre-commit.com): this repository provides the hooks `unifold` (check) and `unifold-fix` (rewrite generated files, then check):

```yaml
repos:
  - repo: <URL of this repository>
    rev: <tag>
    hooks: [{id: unifold-fix}]
```

A coding agent should check when it stops, not after every edit: a unit that is half written is broken on purpose. Claude Code, in `.claude/settings.json`:

```json
{"hooks": {"Stop": [{"hooks": [{"type": "command", "timeout": 60,
  "command": "cd \"$CLAUDE_PROJECT_DIR\" && uvx unifold check --fix --quiet >&2 || exit 2"}]}]}}
```

## What the tool does not read

- Code, in whatever language. The tool reads `unifold.yaml` files and Markdown documents.
- Folders whose name starts with a dot, the `docs` folder of a unit, `node_modules`, `__pycache__`, Cargo build folders, Python virtual environments, symbolic links to folders, the `ignore` folders, and every file and folder that git ignores (`.gitignore`, `.git/info/exclude` and the global excludes; a committed file is read even if a pattern matches it). List third-party code that is committed under `ignore` in the root manifest.
- Nested projects, for example a submodule with a root manifest of its own. `tree` lists them; they are checked on their own. Something in another repository is a need of the root; no map across repositories is produced.
- Markdown files other than those named in [documents.md](documents.md), and text inside code blocks.
- The meaning of a summary, a contract or a `Says` paragraph.

## Testing another implementation

[conformance.py](../../tests/conformance.py) holds the test cases as data: small projects with the findings that `check --json` must report, as rule, severity and file, and scenarios for `init`, stamps, `--fix` and JSON on failure. `python3 tests/conformance.py --tool "CMD"` runs them against another tool; `--write DIR` writes the cases as files. An implementation conforms when all cases pass. Cases for generated files run without the reference generator, so a second generator is tested too.
