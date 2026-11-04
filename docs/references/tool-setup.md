# Setting up the tool

How a project starts with the [reference tool](tool.md), how it runs in hooks and continuous integration, and how another implementation is tested.

## init

`unifold init` starts a project. If `DIR` has no `unifold.yaml`, it writes the root manifest: the version of the standard, `name` from the folder name, and `responsibility: TODO`, which `check` reports until a person has replaced it. If `DIR` has no `README.md`, it writes one from the template of the `unifold` skill, with placeholders in angle brackets to replace. Then it writes the generated files, as `check --fix` does. A hand-written `AGENTS.md` is in the way of the generated one: on a terminal `init` asks whether to replace it, otherwise it keeps the file and says so. A project of one unit conforms at once: `check` reports warnings and no error.

`init` reads no code and writes no other manifest. The units of an existing repository are a judgement about its architecture; a build file knows packages, not units. A person makes that judgement, or an agent with the skill `unifold-convert` ([first map](../tutorials/first-map.md)); `check` then says what is missing or inconsistent.

The root `AGENTS.md` always carries the unifold block: about 15 lines, plus one row per unit when the project has at most 40 units below the root. `init --agents` also installs the skills `unifold` and `unifold-convert` into `docs/skills/` (text, templates and this tool) and writes the skill stubs into `.agents/skills/` and `.claude/skills/`; the block then names the installed tool and links the skills. `check --fix` keeps the stubs current wherever these folders exist. `init --agents` prints a hint if a `CLAUDE.md` at the root does not mention `AGENTS.md`, which hides it from Claude Code.

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

## Testing another implementation

[conformance.py](../../tests/conformance.py) holds the test cases as data: small projects with the findings that `check --json` must report, as rule, severity and file, and scenarios for `init`, `impact`, `--fix`, `model`, `--ignore` and JSON on failure. `uv run tests/conformance.py --tool "CMD"` runs them against another tool; `--write DIR` writes the cases as files. An implementation conforms when all cases pass. Cases for generated files run without the reference generator, so a second generator is tested too.
