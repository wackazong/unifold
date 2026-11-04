# Coding agents

How a coding agent learns that a repository uses unifold, what it reads, and what it must not trust.

## Three ways in

| Way | What it is | When the agent sees it |
|---|---|---|
| `AGENTS.md` | A generated file at the root: a pointer to `README.md`, the documents and skills of the root by kind, and the unifold block: what unifold is, the commands `show`, `capability` and `check`, and an index of the units below the root (name, path, responsibility, and the status when it is not `active`) when there are at most 40 of them, otherwise a pointer to `unifold tree` | Always, where the agent loads `AGENTS.md` |
| The skills | `unifold-convert`, the procedure that brings a repository into the format, and `unifold`, the procedures for reading and changing a unifold project | When the agent decides that the task calls for it |
| The tool | `unifold show`, `capability`, `impact`, `brief`, `trace`, `scenario` and `check`, each with `--json` | When the agent runs it |

`unifold init --agents` sets up all three: it installs the skills and the tool in `docs/skills/` of the root, writes the stubs described below, and points the block in the root `AGENTS.md` at them ([tool.md](tool-setup.md#init)). Why there are three ways and not one: [reasoning](../explanation/reasoning.md#why-three-ways-in-for-agents).

## Where skills are found

No agent searches `docs/skills/`. unifold keeps skills there, next to the code they concern, and `unifold check --fix` writes a generated stub for each into `.agents/skills/` and `.claude/skills/` at the root, where these folders exist; `unifold init --agents` creates them. The stub of a skill of the root unit keeps the name of the skill, for example `unifold`. The stub of a skill of another unit is named `<unit>-<skill>`, unless the skill's name already starts with `<unit>-`; if two units would get the same name, the path of the unit with `-` for `/` takes the place of its name. A stub has the description of the skill, and its body says which file to read. Stubs are files, not symbolic links, so that they work on every operating system and relative links in the skill stay valid. Commit them. The checker reports stale stubs when the folders exist.

`.agents/skills` is the folder that the Agent Skills project recommends to all clients
([source](https://agentskills.io/client-implementation/adding-skills-support.md)).

## What agents differ in

Agents differ in which `AGENTS.md` files they load: some read every one from the root down to the working folder, some only the nearest, some none, and some stop at a size limit. They also search different folders for skills. Three choices follow from this:

- unifold writes one `AGENTS.md`, at the root, so an agent that reads only the nearest file still finds it. Below the root, `unifold show` prints what a file per unit would hold.
- The generated `AGENTS.md` is short: pointers, not text ([documents.md](documents.md)).
- `unifold init --agents` prints a hint when a `CLAUDE.md` exists that does not mention `AGENTS.md`. Claude Code then reads only `CLAUDE.md`, which has to import the other file with `@AGENTS.md` ([memory](https://code.claude.com/docs/en/memory)).

Every agent with a shell can run the tool, so the tool is the one way in that works for all of them.

## What the agent reads, in order

1. The root `AGENTS.md`, which its harness loads, and the `README.md` of the unit of its task. Its `## Why` is what cannot be derived from code.
2. `unifold show` in the folder of the task. It prints the unit, its capabilities and needs, who finally provides and uses them, the status of every unit it mentions, and the skills and decisions of the unit.
3. Only then further files: `docs/explanation/context.md`, a contract, the explanation file the task needs. The `unifold` skill has the table of what to read for which task.

`unifold impact` answers "what is affected if I change this": the units that depend on a unit or capability, through the whole tree, and the context items that cite its files.

## What an agent must not take as fact

The `unifold` skill lists the signs in its table [What not to trust blindly](../skills/unifold/SKILL.md#what-not-to-trust-blindly): a planned unit, a proposed or derived decision, a `TODO`, and a clean check, which says nothing about the code. `show` prints the status of every unit it mentions and marks planned units and proposed decisions.

## Hooks

An agent runs `unifold check` when it stops, not after every edit: a unit that is being added is broken for a moment. The hook for Claude Code, a pre-commit hook and a CI job are in [tool.md](tool-setup.md#hooks-and-continuous-integration).
