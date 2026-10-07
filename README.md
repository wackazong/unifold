---
unit: youmedoc
youmedoc: "0.1"
summary: A convention for keeping project knowledge in Markdown next to the code, written by AI and corrected by humans
kind: specification
status: active
provides:
  specification:
    kind: specification
    summary: The text of the standard, in chapters of at most 200 lines
    contract: doc/references/youmedoc/index.md
  skills:
    kind: skill
    summary: Three skills that teach an agent to read, write and check a youmedoc project
    contract: doc/skills
  checker:
    kind: cli
    summary: Reference tool that checks the mechanical rules and generates diagrams and indexes
    contract: doc/references/youmedoc/checker.md
needs:
  python:
    kind: runtime
    summary: Python 3.9 or newer with PyYAML, to run the checker
---
# youmedoc

youmedoc is a convention for organising the knowledge about a software project
inside its repository. Knowledge lives in short Markdown files in the folder it
concerns. Selected folders are **units** with a declared interface; a parent
knows its children only through that interface. Diagrams are generated.
The files are written mainly by AI agents and read and corrected by humans.

This repository contains the standard, and it is documented with the standard.

Start reading at [doc/references/youmedoc/index.md](doc/references/youmedoc/index.md).

## Provides

### `specification`

The standard itself: an overview, twelve chapters and a JSON Schema in
[doc/references/youmedoc/](doc/references/youmedoc/index.md). The chapters
define the files of a unit, the manifest, the wiring, the generated diagrams,
the writing rules and the ruleset. Version 0.1 is a draft: rules may still
change, and each change is recorded as a decision.

### `skills`

Three skills in the [Agent Skills](https://agentskills.io/specification) format:

| Skill | Purpose |
|---|---|
| [read-docs](doc/skills/read-docs/SKILL.md) | Find your way through a youmedoc project |
| [write-docs](doc/skills/write-docs/SKILL.md) | Create and change units, decisions, references and skills; includes file templates |
| [check-docs](doc/skills/check-docs/SKILL.md) | Enforce the ruleset with the checker and by review |

### `checker`

One Python file,
[youmedoc.py](doc/skills/check-docs/scripts/youmedoc.py), with the commands
`check`, `generate`, `tree` and `init`. It is described in
[checker.md](doc/references/youmedoc/checker.md). It checks documents against
each other. It does not read code.

## Needs

### `python`

Only the checker needs it. The standard can be followed without the tool; the
[check-docs](doc/skills/check-docs/SKILL.md) skill says how.

## Use youmedoc in your repository

1. Copy the standard into your repository root:

   ```sh
   uv run doc/skills/check-docs/scripts/youmedoc.py init /path/to/your/repo
   ```

2. Give your root `README.md` a manifest with `youmedoc: "0.1"` and add a
   link to the standard, <https://youmedoc.example>.
3. Follow [workflow.md](doc/references/youmedoc/workflow.md).

## Example

[examples/plantwatch](examples/plantwatch/README.md) is a complete youmedoc
project without product code: a sensor device, its emulator, a test rig, a
mobile app and a set of cloud services. It is a nested project and is checked
on its own.

## Out of scope

- No build, packaging or deployment.
- No check that code matches the documents.
- No rules for Markdown files outside units and their `doc/` folders.

## More

- [AGENTS.md](AGENTS.md): why the standard is built this way
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
