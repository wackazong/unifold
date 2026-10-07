---
name: read-docs
description: Find your way through a repository that is documented with unifold. Use it before you read, change or review anything in such a repository, and whenever you enter a folder you do not know yet.
license: MIT OR Apache-2.0
---
# Read the docs of a unifold project

In a unifold project the knowledge about a folder is in that folder. Reading
in the right order gives you what you need with few files.

## First: find your unit and its neighbourhood

1. **Find your unit.** Start at the file or folder your task concerns. Walk
   up until a folder has a manifest: a file `unit.yaml`, or a `README.md`
   whose front matter contains `unit:`. That folder is your unit. Folders you
   passed are plain folders. The project root is the nearest folder above
   whose manifest contains `unifold:`; the standard and its skills are there.
2. **Ask the tool.** From the unit's folder run

   ```sh
   uv run <root>/doc/skills/check-docs/scripts/unifold.py show
   ```

   (or `python3` with PyYAML). It prints the unit's ports, who finally
   provides each need, who finally uses each port, the parent, the children,
   the skills, the decisions and the files of the unit. `--json` gives the
   same as data. `tree` prints all units of the project.
3. **Without the tool,** read the unit's generated
   `doc/diagrams/context.md`: its tables hold the same resolved neighbours.

## Then: read what your task needs

| Your task | Read, in this order |
|---|---|
| Use the unit from outside, or answer what it offers | The unit's `README.md`. For exact definitions, the `contract` of the port. |
| Change code inside the unit | `README.md`, `AGENTS.md`, `doc/context.md`. Then the skill in the `## Skills` table of `AGENTS.md` that fits the task. |
| Change a port of the unit | The above, then `unifold port <unit folder> <port>`: it prints what each side of every connection says about the port. |
| Change a value, a limit or a default | `show` for the users of the port it belongs to; `cited-by` on the file that defines it; then search the project for the old value in every notation (15 minutes, 900 s). |
| Add a unit below this one | This unit's `AGENTS.md` skills table first: a project skill for it takes precedence. Then the `write-docs` skill. |
| Understand why it is built this way | `AGENTS.md`, `doc/architecture.md`, `doc/decisions/index.md` |
| Find out what a term means | `doc/references/glossary.md` of the unit; if the term is not there, the items in `doc/context.md` that cite an ancestor's glossary |
| Review a change | The `check-docs` skill |

## Rules for moving around

- **Down only through interfaces.** To learn about a child, read the child's
  `README.md` and nothing else. Enter the child, and start again at the top
  of this skill, only when your task is inside it.
- **Up only when needed.** `doc/context.md` tells you which decisions and
  conventions from above apply. Go to the parent only if it does not answer
  your question.
- **Never sideways by guessing.** Do not open a sibling to find out what a
  need means. The need's text in your unit's `README.md` says what is
  expected. Who provides it is in the output of `show`; read that provider's
  `README.md` only if you must know what it guarantees.

## Resolving wiring by hand

If you cannot run the tool: the wiring is in the manifest of the parent.

- The line whose key is `your-unit.need` names the provider. A value
  `sibling.port` is that sibling's port. A bare value, such as `clock`, is a
  need of the parent itself: repeat the lookup one level up with
  `parent.clock`. A value that starts with `./` is a plain folder.
- The lines whose value is `your-unit.port` name the users. A key
  `sibling.need` is that sibling. A bare key is a port of the parent itself:
  repeat one level up to find who uses the parent's port.
- Read only the manifest of a parent, not its body.

## Things to know while reading

- Files are at most 200 lines. If you need more than a handful of files, you
  are probably reading outside your unit.
- Files in `doc/diagrams/` and `doc/decisions/index.md` are generated. Trust
  them for structure, never edit them.
- Only decisions with status `accepted` bind. `proposed` is not yet agreed;
  `deprecated` and `superseded` no longer apply.
- A unit with `status: planned` describes intended behaviour; its code may
  not exist.

## Before and after

- Before you change documents, use the
  [write-docs](../write-docs/SKILL.md) skill.
- After any change, use the [check-docs](../check-docs/SKILL.md) skill.

## The standard

The full text of unifold is in this project. Start at
[index](../../references/unifold/index.md), which lists the rules in brief
and every chapter. The chapters you need most often:

| Chapter | Content |
|---|---|
| [unit-files](../../references/unifold/unit-files.md) | `README.md` and `AGENTS.md` |
| [doc-folder](../../references/unifold/doc-folder.md) | Context, architecture, decisions, references, skills |
| [manifest](../../references/unifold/manifest.md) | Manifest fields |
| [wiring](../../references/unifold/wiring.md) | Connecting needs to providers |
| [rules](../../references/unifold/rules.md) | The ruleset and the direction rules |
| [checker](../../references/unifold/checker.md) | The tool |
