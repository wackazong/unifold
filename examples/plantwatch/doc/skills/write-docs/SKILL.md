---
name: write-docs
description: Create or change the documents of a youmedoc project - units, ports, wiring, decisions, references, skills. Use it when you design a new part, change an interface, record a decision, or document a folder that has no documents yet.
---
# Write the docs of a youmedoc project

Use [read-docs](../read-docs/SKILL.md) first, so that you know the unit you
are working in. The reasons behind these procedures are in
[workflow.md](../../references/youmedoc/workflow.md).

## Templates

Copy a template, fill it in, delete the comments.

| File to create | Template |
|---|---|
| `README.md` of a unit | [README.template.md](assets/README.template.md) |
| `AGENTS.md` of a unit | [AGENTS.template.md](assets/AGENTS.template.md) |
| `doc/context.md` | [context.template.md](assets/context.template.md) |
| `doc/architecture.md` | [architecture.template.md](assets/architecture.template.md) |
| `doc/decisions/NNNN-title.md` | [decision.template.md](assets/decision.template.md) |
| `doc/references/<topic>.md` | [reference.template.md](assets/reference.template.md) |
| `doc/skills/<name>/SKILL.md` | [SKILL.template.md](assets/SKILL.template.md) |

## Add a unit

1. Check that the folder deserves to be a unit
   ([concepts.md](../../references/youmedoc/concepts.md), last section).
   The folder name is the unit name: letters, digits, `-`, `_`.
2. Write `README.md` from the template. Set `status: planned` if the code
   does not exist. Declare provided ports and needs
   ([manifest.md](../../references/youmedoc/manifest.md)). Write needs
   without looking at the siblings: say what is needed, not who has it.
3. Write `AGENTS.md` from the template. The `## Why` section is the part
   that matters. Do not list children or ports in it.
4. If the unit relies on decisions, conventions or terms from above, write
   `doc/context.md` and cite them there with a restatement.
5. In the parent's `README.md`, add wiring lines: one for every need of the
   new unit, and one for every port of it that a sibling or the parent uses
   ([wiring.md](../../references/youmedoc/wiring.md)).
6. For every wiring line you added, read both ends and make sure the need
   is covered by what the provider's `README.md` offers.
7. Finish (see below).

## Change a port

1. Change the manifest and the body of the unit's `README.md`.
2. Change the wiring in the parent's `README.md`. If a need cannot be met
   inside the parent, add a need to the parent and continue one level up.
3. If the change had alternatives, record a decision.
4. Finish.

## Record a decision

1. Choose the lowest unit whose insides the decision fully covers. A
   decision about how two siblings talk belongs to their parent.
2. Take the next free four-digit number in that unit's `doc/decisions/`.
3. Write the file from the template with `status: proposed`. Never set
   `accepted` yourself; a human does that.
4. Never edit an accepted decision. Write a new one and set the old one to
   `superseded by NNNN`.
5. In units below that depend on it, add a line to `doc/context.md`.
6. Finish. The generator adds the decision to `doc/decisions/index.md`.

## Add a reference

1. Write `doc/references/<topic>.md` from the template: facts only.
2. If it would exceed 200 lines, make it a folder with an `index.md` and
   parts.
3. Link it from the file that needs it: the `contract` field, the
   `README.md`, `AGENTS.md` or another reference.

## Add a skill

1. Create `doc/skills/<name>/SKILL.md` from the template in the lowest unit
   in which the whole procedure takes place. `name` equals the folder name.
2. Add a row to the `## Skills` table of that unit's `AGENTS.md`.

## Rules to keep in mind while writing

- At most 200 lines per file.
- Link every mention of another file. Within the unit freely; down only to
  a child's `README.md`; up only from `doc/context.md`; never sideways
  ([rules.md](../../references/youmedoc/rules.md)).
- One home for every fact. Link instead of repeating.
- Never write structure by hand: no lists of children, ports or wiring
  outside the manifest.
- Never edit files in `doc/diagrams/` or `doc/decisions/index.md`.
- Style: [markdown.md](../../references/youmedoc/markdown.md).

## Finish

1. Run the generator.
2. Use the [check-docs](../check-docs/SKILL.md) skill.
3. Tell the human what you created or changed, which decisions wait for
   acceptance, and which warnings remain.
