---
name: unifold
description: Work in a repository that contains unifold.yaml files. Find out what a folder provides and needs and who is on the other side, change units, capabilities and wiring, record decisions, and check the result. Use it when a task touches the interface or the dependencies of a folder, the architecture, or the documents of a unit, and before you finish any change in such a repository.
license: MIT OR Apache-2.0
---

# unifold

In a unifold project some folders are **units**: they contain a `unifold.yaml` that says what the folder is responsible for, what it provides, its **capabilities**, and what it **needs**. The nearest unit above connects each need to a provider in its `wiring`. Every connection has a **contract**, one document with the parts both sides use, their examples and the fake that tests use. A **scenario** in a manifest tells a story as hops across the map. A tool checks that all of this is consistent and generates the diagrams; it does not read code. The standard is one page: <https://unifold.md/spec>.

`unifold` below means the tool: `uvx unifold`, or the copy in this skill, `uv run <folder of this skill>/scripts/unifold.py`. It finds the project root from any folder inside the project.

## 1. Find your unit

```sh
unifold show [PATH]      # PATH: the file or folder of your task; default: here
```

`show` prints the unit that contains `PATH`: its responsibility, kind, secret and not, status, capabilities and needs. For each need it names who finally provides it, and for each capability who finally uses it, each with its status. It also lists the parent, the children, the scenarios that pass through the unit, and its skills and decisions. `--json` gives the same as data; `unifold model --json` gives the whole project at once.

- `unifold capability PATH NAME` prints both sides of every connection of one capability or need: the texts and the contracts.
- `unifold impact PATH [CAPABILITY]` lists everything that depends on the unit or capability, through all levels, and the context items that cite its files.
- `unifold tree` prints all units.

Without the tool: your unit is the nearest folder at or above your file that has a `unifold.yaml`. Its parent is the next such folder above. The parent's `wiring` has the lines `your-unit.need: provider`; the provider is a capability of a sibling, or a need of the parent to which the need is passed up. A need without a line is not connected.

Every unit has a `README.md`; its `docs/` follows the conventions used below, and `AGENTS.md` is generated.

## 2. Read what the task needs

| Task | Read, in this order |
|---|---|
| Use the unit from outside | `show`; its `README.md`; the `contract` of the capability, which defines it |
| Change code inside the unit | `show`; `README.md` (`## Why`); `docs/explanation/context.md` and `invariants.md`; a skill from `AGENTS.md` if one fits |
| Change a capability or a need | The above; then `unifold capability` for that entry and `unifold impact` |
| Change a value, a limit, a default | `unifold impact` on the unit; the row in `docs/references/constants.md` where one exists; then search the project for the old value in every notation (15 minutes, 900 s) |
| Write or change a contract | The contract itself, part by part: <https://unifold.md/contracts>; `unifold capability` for every side that names it |
| Tell a story of the system | The scenarios of the manifests on its path; the generated `docs/diagrams/scenario-<name>.md` |
| Add a unit | The parent's `README.md` and manifest; for a repository without a map, the skill `unifold-convert` |
| Understand why it is built this way | `README.md` `## Why`, then `docs/explanation/reasoning.md` and `docs/decisions/index.md` |
| Find out what a term means | `docs/references/glossary.md` of the unit, then `docs/explanation/context.md`; a new term is a row there, from [glossary.template.md](assets/glossary.template.md) |
| Review a change | The review checklist: <https://unifold.md/writing#review-checklist> |

## 3. Change

Do not weaken a manifest to make the check pass. Mark a need `optional`, delete a capability or remove a connection only when that is the change you were asked to make.

### Add a unit

1. Create `unifold.yaml` in the folder from [unifold.template.yaml](assets/unifold.template.yaml). The folder name is the unit's name. Required: `responsibility`, one sentence; a unit with children also needs `kind`. Use `logic`, `stateful` or `adapter` where one fits: they carry rules. Write `secret`, the one piece of knowledge the unit hides, with the decision that says why, and `not`, what it leaves to others, naming the need through which it delegates. Set `status: planned` if the code does not exist yet.
2. Declare capabilities and needs with one line each. Write a need from the point of view of this unit: what is needed, never who has it. Do not declare the language runtime, registry packages or logging as needs.
3. Add a `wiring` line for every need to the parent's manifest (`new-unit.need: sibling.capability`). Where no sibling meets a need, declare it in the parent too and pass it up: `new-unit.need: need`. Add a line for each sibling need that the new unit meets.
4. Give both sides of every new connection the same `contract`: a document in `docs/references/` of the parent or a unit above it. Write it if it does not exist (below). A side that uses only some parts lists them under `contract: {path, parts}`.
5. Write `README.md` from the template below. Its `## Why` is the part that matters. Do not list children, capabilities or connections in prose; what the unit does not do is `not` in the manifest. `AGENTS.md` is generated in step 7.
6. Add the unit to the scenarios whose story passes through it, or write one (below).
7. Finish (section 4).

### Change a capability, a need, or a dependency in code

1. If your code starts to use another unit, declare the new need and wire it in the parent. If no sibling provides it, declare the need in the parent as well, pass it up (`unit.need: need`) and continue one level up. If the code of a unit with children starts to use one of its children, declare a need in that unit and wire it in its own wiring: `need: child.capability`. The tool does not read code: keeping the map in step with it is part of the change.
2. If a capability changes, change the contract that both sides name and the manifest: the part's signature, its examples, and `## Fake` if the stand-in changes. Change its section in `README.md` only if there is one; it says what the contract does not.
3. Run `unifold capability PATH NAME` and read both sides of every connection. The provider must still cover what each need expects.
4. If you renamed an entry, search the unit's files for the old name.
5. If the change had real alternatives, record a decision. Finish.

### Change a value that others rely on

1. Run `unifold impact PATH`. It lists the users of the unit.
2. Run `unifold cited-by FILE` for each file you changed. It lists every context item that restates the file: file, line and the `Says` text.
3. Read each cited source again and correct every `Says` that is no longer true.
4. Run `unifold stamp`. It prints each item it confirms, with file, line and source. `check --fix` never writes a stamp.
5. Search the project for the old value.

### Write a contract

1. Write `docs/references/<topic>.md` in the unit that wires the connection, from [contract.template.md](assets/contract/contract.template.md). The header names whose contract it is, the notation (WIT by default) and the sources as text.
2. Under `## Parts`, one `###` heading per operation, event or type, in kebab-case. Each has `Kind:` and a fenced code block with its signature. A command or query has `Pre:`, `Result:`, `Errors:` and an `Examples:` table: one row per case from the sources, both sides of every precondition, one row per error.
3. Define a type once in the subtree; link to it from other contracts.
4. Write `## Fake`: replay of the examples, a simplified behaviour with its faults, or `the real implementation` for a logic provider.
5. Longer than the line limit: a folder from [index.template.md](assets/contract/index.template.md) and [part.template.md](assets/contract/part.template.md), one file per part.
6. Name the contract from both sides, list `parts` where a side uses only some, and run `check`: it reports a part that is missing, a part without a signature or examples, and a contract without a fake.

### Write a scenario

1. Choose the lowest unit that contains every unit the story names; a hop to a need of the root belongs to the root.
2. Under `scenarios` in its manifest, from the template: `summary`, `source`, `hops`, `expect`. A hop is `caller -> target.part`: units by their path from the holding unit, a capability or need of the holding unit bare. Every part must be in the contract of the connection the hop uses.
3. Run `check`. A hop that does not resolve means a missing connection, a missing part or a wrong cut: fix the manifests or the contract, never the story. Then `check --fix` writes `docs/diagrams/scenario-<name>.md`.

### Record a decision

1. Choose the lowest unit whose insides the decision fully covers. A decision about how two siblings talk belongs to their parent.
2. Write `docs/decisions/NNNN-short-title.md` with the next free number, from [decision.template.md](assets/decision.template.md).
3. Keep `status: proposed`. Never set `accepted` and never fill in `decision-makers`; a person does both. Where a source settles the matter, write the decision from [decision-derived.template.md](assets/decision-derived.template.md) instead: `status: derived`, `derived-from` and `## Source says` complete enough to stand without the source. It binds until a person accepts or supersedes it.
4. Never edit an accepted decision. To replace it, write a new one and set the old one to `superseded by NNNN`. To change a part, write a new one that says "This amends NNNN:".
5. In a unit below that depends on it, add an item to `docs/explanation/context.md` from [context.template.md](assets/explanation/context.template.md). Do not type a stamp; run `unifold stamp`, which adds it. Finish.

### Add a skill

1. Write `docs/skills/<name>/SKILL.md` in the lowest unit in which the whole procedure happens, from [SKILL.template.md](assets/SKILL.template.md). `name` equals the folder name.
2. Run `unifold skills sync`. It writes the stubs through which agents find the skill. A stub is named `<unit>-<name>`, or by the bare name for a skill of the root.
3. Tell the human that the skill is new and unreviewed.

### Move a unit

1. Change the wiring in the old and the new parent, then run `check`.
2. Every upward link in `docs/explanation/context.md` is now reported: find each item again in the new place. Finish.

## 4. Finish

```sh
unifold check --fix     # writes generated files (never stamps)
unifold check           # must report no error
```

- Fix every `error`. Fix the cause: wire a need, or pass it up; do not delete it.
- Judge every `warn`. Fix it, or keep it and say why. A warning about a contract's body or a scenario's coverage is work left, not an opinion.
- Never edit a generated file (first line `<!-- unifold:generated`). Change the manifest and run `check --fix`.

Report to the human:

- every capability, need, wiring line and contract you added, changed or removed;
- the decisions you wrote, proposed or derived, which wait for acceptance, and the skills you wrote, which wait for review;
- the warnings that remain and the responsibilities and summaries that are still `TODO`;
- whether the check ran. If the tool could not run, say so.

## Rules for moving around

- **Down only through the interface.** To learn about a child unit, read its `unifold.yaml` and `README.md`. Enter it only when your task is inside it, and then start again at section 1.
- **Up only through `docs/explanation/context.md`.** It restates what applies from above. Open the source it links to only if the restatement does not answer your question.
- **Never sideways by guessing.** Do not open a sibling to learn what a need means; the need's text in your unit says what is expected. `show` tells you who provides it.
- In hand-written files of a unit, link freely inside the unit. Link down only to a child's `README.md`, up only from `docs/explanation/context.md`, and never to a sibling. Do not name siblings or users.
- Files have at most 200 lines. Split a file before it grows beyond that.

## What not to trust blindly

| Sign | Meaning |
|---|---|
| `status: planned` | An intention. The code may not exist. |
| Decision with `status: proposed` | Not agreed yet. Only `accepted` and `derived` decisions bind. |
| Warning "cited source changed" | A `Says` text may be out of date. Read the source, correct `Says`, run `unifold stamp`. |
| `responsibility: TODO`, `summary: TODO` | A placeholder that nobody completed. |
| Decision with `status: derived` | A source settles it, says its author. Read `## Source says` against the passage before you rely on it. |
| A clean `check` | The files agree with each other. It does not mean that the code follows them, or that a text is true. |

## Templates

| File | Template |
|---|---|
| `unifold.yaml` | [unifold.template.yaml](assets/unifold.template.yaml) |
| `README.md` of a unit | [README.template.md](assets/README.template.md) |
| `docs/explanation/<file>.md` | [assets/explanation/](assets/explanation/): one template per file, `context.template.md` among them |
| `docs/tutorials/<name>.md` | [tutorial.template.md](assets/tutorial.template.md) |
| `docs/decisions/NNNN-title.md` | [decision.template.md](assets/decision.template.md); a decision a source makes: [decision-derived.template.md](assets/decision-derived.template.md) |
| `docs/references/<topic>.md` | [reference.template.md](assets/reference.template.md); a contract: [contract.template.md](assets/contract/contract.template.md), or as a folder [index.template.md](assets/contract/index.template.md) with [part.template.md](assets/contract/part.template.md) per part |
| `docs/references/constants.md` | [constants.template.md](assets/constants.template.md) |
| `docs/references/glossary.md` | [glossary.template.md](assets/glossary.template.md): one row per term |
| `docs/skills/<name>/SKILL.md` | [SKILL.template.md](assets/SKILL.template.md) |
| A section for `CONTRIBUTING.md` | [CONTRIBUTING.snippet.md](assets/CONTRIBUTING.snippet.md) |

## More

- The standard: <https://unifold.md/spec>; the documents of a unit: <https://unifold.md/documents>, <https://unifold.md/writing>, <https://unifold.md/contracts>
- Wiring: <https://unifold.md/wiring>; the tool: <https://unifold.md/tool>, <https://unifold.md/rules>
- Agents, the first map, the reasoning: <https://unifold.md/agents>, <https://unifold.md/first-map>, <https://unifold.md/reasoning>
