---
name: unifold
description: Work in a repository that contains unifold.yaml files. Find out what a folder provides and needs and who is on the other side, change units, capabilities and wiring, record decisions, and check the result. Use it when a task touches the interface or the dependencies of a folder, the architecture, or the documents of a unit, and before you finish any change in such a repository.
license: MIT OR Apache-2.0
---

# unifold

In a unifold project some folders are **units**: they contain a `unifold.yaml` that says what the folder is responsible for, what it provides, its **capabilities**, and what it **needs**. The nearest unit above connects each need to a provider in its `wiring`. Every connection has a **contract**, one document with the parts both sides use, their examples and the fake that tests use. A **scenario** in a manifest is a story through the software, told as hops across the map, one step after the other. A contract says how its connection is used, and where the connection has **states**, which ones a consumer can see. A tool checks that all of this is consistent and draws the diagrams; it does not read code. The standard starts at <https://unifold.md/spec>.

`unifold` below means the tool: `uvx unifold`, or the copy in this skill, `uv run <folder of this skill>/scripts/unifold.py`. It finds the project root from any folder inside the project.

## 1. Find your unit

```sh
unifold show [PATH]      # PATH: the file or folder of your task; default: here
```

`show` prints the unit that contains `PATH`: its responsibility, kind, not, status, capabilities and needs. For each need it names who finally provides it, and for each capability who finally uses it, each with its status. It also lists the parent, the children, the scenarios that pass through the unit, and its skills and decisions. `--json` gives the same as data; `unifold model --json` gives the whole project at once.

- `unifold capability PATH NAME` prints both sides of every connection of one capability or need: the texts and the contracts.
- `unifold impact PATH [CAPABILITY]` lists everything that depends on the unit or capability, through all levels, and the context items that cite its files.
- `unifold tree` prints all units.
- `unifold explore` writes the explorer, the whole map as one HTML page with every document beside it, and opens it in a browser; `--no-open` only writes it. The page is written outside the repository, nothing to commit.

Without the tool: your unit is the nearest folder at or above your file that has a `unifold.yaml`. Its parent is the next such folder above. The parent's `wiring` has the lines `your-unit.need: provider`; the provider is a capability of a sibling, or a need of the parent to which the need is passed up. A need without a line is not connected.

Every unit has a `README.md`, and its `docs/` follows the conventions used below. `AGENTS.md` is generated at the root only.

## 2. Read what the task needs

| Task | Read, in this order |
|---|---|
| Use the unit from outside | `show`; its `README.md`; the `contract` of the capability, which defines it |
| Implement a unit, or a part of one | `unifold brief`, which prints the parts, examples, fakes, states and scenarios; then [implement-a-unit.md](procedures/implement-a-unit.md) |
| Change code inside the unit | `show`; `README.md` (`## Why`); `docs/explanation/context.md` and `invariants.md`; a skill that `show` lists, if one fits |
| Change a capability or a need | The above; then `unifold capability` for that entry and `unifold impact` |
| Change a value, a limit, a default | `unifold impact` on the unit; the row in `docs/references/constants.md` where one exists; then search the project for the old value in every notation (15 minutes, 900 s) |
| Write or change a contract | The contract itself, part by part: <https://unifold.md/contracts>; `unifold capability` for every side that names it |
| Tell a story of the system | The scenarios of the manifests on its path; the explorer draws each |
| Use or build one connection | Its contract: `## Use`, `## States`, then the parts; the explorer draws the states; the scenarios that pass over it |
| Add a unit | The parent's `README.md` and manifest; for a repository without a map, the skill `unifold-convert` |
| Understand why it is built this way | `README.md` `## Why`, then `docs/explanation/reasoning.md` and `docs/decisions/index.md` |
| Find out what a term means | `docs/references/glossary.md` of the unit, then `docs/explanation/context.md`; a new term is a row there, from [glossary.template.md](assets/glossary.template.md) |
| Review a change | The review checklist: <https://unifold.md/writing#review-checklist> |

## 3. Change

Do not weaken a manifest to make the check pass. Mark a need `optional`, delete a capability or remove a connection only when that is the change you were asked to make.

Open the procedure for the task and follow its steps:

| Task | Procedure |
|---|---|
| Add a unit | [add-a-unit.md](procedures/add-a-unit.md) |
| Implement a unit from its contracts | [implement-a-unit.md](procedures/implement-a-unit.md) |
| Change a capability, a need, or a dependency in code | [change-an-interface.md](procedures/change-an-interface.md) |
| Change a value, a limit or a default that others rely on | [change-a-value.md](procedures/change-a-value.md) |
| Write or change a contract | [write-a-contract.md](procedures/write-a-contract.md) |
| Write a scenario | [write-a-scenario.md](procedures/write-a-scenario.md) |
| Record a decision | [record-a-decision.md](procedures/record-a-decision.md) |
| Add a skill | [add-a-skill.md](procedures/add-a-skill.md) |
| Move a unit | [move-a-unit.md](procedures/move-a-unit.md) |
| Write any other document, and the templates of all files | [write-a-document.md](procedures/write-a-document.md) |

## 4. Finish

```sh
unifold check --fix     # writes generated files
unifold check           # must report no error
```

- Fix every `error`. Fix the cause: wire a need, or pass it up; do not delete it.
- Judge every `warn`. Fix it, or keep it and say why. A warning about a contract's body or a scenario's coverage is work left, not an opinion.
- Never edit a generated file (first line `<!-- unifold:generated`). Change the manifest and run `check --fix`.

Report to the human:

- every capability, need, wiring line and contract you added, changed or removed;
- the decisions you wrote, proposed or derived, which wait for acceptance, and the skills you wrote, which wait for review;
- the warnings that remain, the responsibilities and summaries that are still `TODO`, and, after code, the examples that `unifold trace` says no test names;
- whether the check ran. If the tool could not run, say so.

## Rules for moving around

- **Down only through the interface.** To learn about a child unit, read its `unifold.yaml` and `README.md`. Enter it only when your task is inside it, and then start again at section 1.
- **Up: start with `docs/explanation/context.md`.** It selects what applies from above and says what it means here. Follow a link upward when you need the source.
- **Never sideways by guessing.** Do not open a sibling to learn what a need means; the need's text in your unit says what is expected. `show` tells you who provides it.
- Do not link to a sibling; declare a need. Do not name siblings or users.
- Write as [write-a-document.md](procedures/write-a-document.md) says.

## What not to trust blindly

| Sign | Meaning |
|---|---|
| `status: planned` | An intention. The code may not exist. |
| Decision with `status: proposed` | Not agreed yet. Only `accepted` and `derived` decisions bind. |
| `responsibility: TODO`, `summary: TODO` | A placeholder that nobody completed. |
| Decision with `status: derived` | A source settles it, says its author. Read `## Source says` against the passage before you rely on it. |
| A clean `check` | The files agree with each other. It does not mean that the code follows them, or that a text is true. |

## More

- The standard: <https://unifold.md/spec>; the documents of a unit: <https://unifold.md/documents>, <https://unifold.md/writing>, <https://unifold.md/contracts>
- Wiring: <https://unifold.md/wiring>; the tool: <https://unifold.md/tool>, <https://unifold.md/rules>
- Agents, the first map, the reasoning: <https://unifold.md/agents>, <https://unifold.md/first-map>, <https://unifold.md/reasoning>
