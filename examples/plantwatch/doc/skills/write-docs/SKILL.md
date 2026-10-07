---
name: write-docs
description: Create or change the documents of a unifold project - units, ports, wiring, decisions, references, skills. Use it when you design a new part, change an interface, record a decision, or document a folder that has no documents yet.
license: MIT OR Apache-2.0
---
# Write the docs of a unifold project

Use [read-docs](../read-docs/SKILL.md) first, so that you know the unit you
are working in. If the `AGENTS.md` of that unit lists a skill for your task,
follow that skill; this one supplies the templates and the finish. The
reasons behind these procedures are in
[workflow.md](../../references/unifold/workflow.md).

## Templates

Copy a template, fill it in, delete the comments.

| File to create | Template |
|---|---|
| `unit.yaml`, the manifest of a unit | [unit.template.yaml](assets/unit.template.yaml) |
| `README.md` of a unit | [README.template.md](assets/README.template.md) |
| `AGENTS.md` of a unit | [AGENTS.template.md](assets/AGENTS.template.md) |
| `doc/context.md` | [context.template.md](assets/context.template.md) |
| `doc/architecture.md` | [architecture.template.md](assets/architecture.template.md) |
| `doc/decisions/NNNN-title.md` | [decision.template.md](assets/decision.template.md) |
| `doc/references/<topic>.md` | [reference.template.md](assets/reference.template.md) |
| `doc/skills/<name>/SKILL.md` | [SKILL.template.md](assets/SKILL.template.md) |
| A section for the project's `CONTRIBUTING.md` | [CONTRIBUTING.snippet.md](assets/CONTRIBUTING.snippet.md) |

## Add a unit

1. Check that the folder deserves to be a unit
   ([concepts.md](../../references/unifold/concepts.md), last section).
   The folder name is the unit name. Prefer a name that is not an everyday
   word.
2. Write the manifest and `README.md` from the template. Set
   `status: planned` if the code does not exist. Declare provided ports and
   needs ([manifest.md](../../references/unifold/manifest.md)). Write needs
   without looking at the siblings: say what is needed, in this unit's words,
   not who has it. Do not declare the runtime, the standard library or
   logging as needs.
3. Write each guarantee so that a test could check it. Put the exact
   definition of a port, with examples, into a contract reference.
4. Write `AGENTS.md` from the template. The `## Why` section is the part
   that matters: why the unit exists and what makes it change. Do not list
   children or ports in it.
5. If the unit relies on decisions, conventions or terms from above, write
   `doc/context.md` and cite them there, each with a restatement of at most
   two lines.
6. In the parent's manifest, add wiring lines: one for every need of the new
   unit, and one for every port of it that a sibling or the parent uses
   ([wiring.md](../../references/unifold/wiring.md)). If the kinds of a
   need and its provider differ, add an adapter unit; do not change the kind.
7. For every wiring line you added, read both ends and make sure the need is
   covered by what the provider's `README.md` offers.
8. Search the parent's hand-written files for the name of an existing
   sibling. Every table or statement that enumerates siblings needs the new
   unit too, and the parent's `## Why` must still be true.
9. Finish (see below).

## Change a port

1. Change the manifest, the body of the unit's `README.md` and the contract
   with its examples.
2. Change the wiring in the parent's manifest. If a need cannot be met inside
   the parent, add a need to the parent and continue one level up.
3. Run `show` on the unit. Read the `README.md` of every user or provider it
   lists and make sure both ends still match.
4. If the change had alternatives, record a decision.
5. Finish.

## Change a value that others rely on

1. Run `show` to find the users of the port the value belongs to.
2. If the value is defined in a reference or decision, run `cited-by` on that
   file and correct every restatement it lists.
3. Search the project for the old value.

## Record a decision

1. Choose the lowest unit whose insides the decision fully covers. A
   decision about how two siblings talk belongs to their parent.
2. Take the next free four-digit number in that unit's `doc/decisions/`.
3. Write the file from the template with `status: proposed`. Never set
   `accepted` yourself and never fill in `decision-makers`; a human does
   both.
4. Never edit an accepted decision. Write a new one and set the old one to
   `superseded by NNNN`.
5. In units below that depend on it, add an item to `doc/context.md`.
6. Finish. The generator adds the decision to `doc/decisions/index.md`.

## Add a reference or a skill

1. A reference is `doc/references/<topic>.md`: facts only. Over 200 lines it
   becomes a folder with an `index.md` and parts. Link it from the manifest's
   `contract`, the `README.md`, `AGENTS.md` or another reference.
2. A skill is `doc/skills/<name>/SKILL.md` in the lowest unit in which the
   whole procedure takes place; `name` equals the folder name. Add a row to
   the `## Skills` table of that unit's `AGENTS.md`.

## Rules to keep in mind while writing

- At most 200 lines per file; no line over 400 characters.
- Link every mention of another file. Within the unit freely; down only to
  a child's `README.md`; up only from `doc/context.md`; never sideways
  ([rules.md](../../references/unifold/rules.md)).
- Write the names of units and ports in code font. Never write the name of a
  sibling or ancestor outside `doc/context.md`.
- One home for every fact. Link instead of repeating.
- Never write structure by hand: no lists of children, ports or wiring
  outside the manifest.
- Never edit files in `doc/diagrams/` or `doc/decisions/index.md`.
- Never weaken a document to make the checker pass: do not mark a need
  `optional`, delete a port or drop an alternative unless that is the change
  you were asked to make.
- Style: [markdown.md](../../references/unifold/markdown.md).

## Finish

1. Run the generator.
2. Use the [check-docs](../check-docs/SKILL.md) skill.
3. Tell the human what you created or changed: every port, need, wiring line
   and contract that differs, which decisions wait for acceptance, and which
   warnings remain.
