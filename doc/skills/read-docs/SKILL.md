---
name: read-docs
description: Find your way through a repository that is documented with youmedoc. Use it before you read, change or review anything in such a repository, and whenever you enter a folder you do not know yet.
---
# Read the docs of a youmedoc project

In a youmedoc project the knowledge about a folder is in that folder. Reading
in the right order gives you what you need with few files. Reading at random
costs context and misses the rules that apply.

## Steps

1. **Find your unit.** Start at the file or folder your task concerns. Walk
   up until a folder has a `README.md` whose front matter contains `unit:`.
   That folder is your unit. Folders you passed on the way are plain folders.
2. **Read the interface.** Read the unit's `README.md`: the manifest, then
   the body. You now know what the unit provides and needs.
3. **Read the why.** Read `AGENTS.md` in the same folder. Follow its
   `## Read next` list as far as your task requires. Note its skills table.
4. **Read the inherited rules.** If `doc/context.md` exists, read it. It
   tells you which decisions and conventions from above apply here.
5. **Look at the diagrams.** `doc/diagrams/context.md` shows the unit among
   its siblings. `doc/diagrams/component.md` shows its children. Use the
   table below each diagram to move to another unit.
6. **Go down only through interfaces.** To learn about a child, read the
   child's `README.md` and nothing else. Enter the child, and repeat from
   step 2, only when your task is inside it.
7. **Go up only when needed.** If `doc/context.md` does not answer a
   question about the surroundings, go to the parent unit and repeat from
   step 2 there.
8. **Do not read siblings to understand a unit.** The unit's needs say what
   it expects. If you must know what a provider guarantees, look up the need
   in the `wiring` of the parent's manifest and read the provider's
   `README.md`.

## Where to find what

| Question | Where |
|---|---|
| What does this unit offer and require? | Manifest and body of its `README.md` |
| What exactly is the contract of a port? | The `contract` path in the manifest |
| Who provides a need of this unit? | `wiring` in the parent's `README.md`: the line whose key is `unit.need` |
| Who uses a port of this unit? | `wiring` in the parent's `README.md`: the lines whose value is `unit.port` |
| Why is the unit built this way? | `AGENTS.md`, then `doc/architecture.md`, then `doc/decisions/index.md` |
| Which rules from above apply here? | `doc/context.md` |
| How do I do a certain task here? | Skills table in `AGENTS.md` |
| What does a term mean? | A glossary in `doc/references/` of this unit or, via `doc/context.md`, of an ancestor |
| Does the code exist yet? | `status` in the manifest |

## Things to know while reading

- Files are at most 200 lines. If you need more than a handful of files, you
  are probably reading outside your unit.
- Files in `doc/diagrams/` and `doc/decisions/index.md` are generated. Trust
  them for structure, never edit them.
- A decision with status `proposed` is not yet agreed. A decision that is
  `deprecated` or `superseded` no longer applies.
- A unit with `status: planned` describes intended behaviour.

## Before and after

- Before you change documents, use the
  [write-docs](../write-docs/SKILL.md) skill.
- After any change, use the [check-docs](../check-docs/SKILL.md) skill.

## The standard

The full text of youmedoc is in this project:

| Chapter | Content |
|---|---|
| [index](../../references/youmedoc/index.md) | Overview and goals |
| [concepts](../../references/youmedoc/concepts.md) | Terms and principles |
| [unit-files](../../references/youmedoc/unit-files.md) | `README.md` and `AGENTS.md` |
| [doc-folder](../../references/youmedoc/doc-folder.md) | Context, architecture, decisions, references, skills |
| [manifest](../../references/youmedoc/manifest.md) | Manifest fields |
| [wiring](../../references/youmedoc/wiring.md) | Connecting needs to providers |
| [diagrams](../../references/youmedoc/diagrams.md) | Generated diagrams |
| [markdown](../../references/youmedoc/markdown.md) | Writing rules |
| [rules](../../references/youmedoc/rules.md) | The ruleset and the direction rules |
| [workflow](../../references/youmedoc/workflow.md) | Design first, change, adopt, copy |
| [checker](../../references/youmedoc/checker.md) | The tool |
