# The doc folder

A unit MAY have a folder named `doc/`. It holds the unit's internal knowledge.
Outsiders are not expected to read it. The two files outside `doc/` are
described in [unit-files.md](unit-files.md).

```text
doc/
├── context.md        inherited decisions, conventions and terms
├── architecture.md   longer explanation of the design
├── decisions/        decision records
├── references/       facts to look up
├── skills/           procedures
├── diagrams/         generated
└── assets/           images and other non-Markdown files
```

Only these entries are allowed. A `doc/` folder is never a unit and never
contains units.

## context.md

`doc/context.md` lists what the unit inherits from the levels above it:
decisions, conventions and terms that a reader must know to understand the
unit.

It is the **only** hand-written file of a unit that may link upward. Each item
has three parts:

| Part | Content |
|---|---|
| Source | A link to an ancestor's decision, reference or `README.md` |
| What it says | The item restated in one or two lines |
| What it means here | The consequence for this unit |

The restatement is deliberate redundancy. It keeps the unit understandable
when the folder is read or copied on its own and the link leads nowhere.

Rules:

- A unit that relies on anything decided or defined above it MUST have
  `doc/context.md` and MUST cite it there.
- Links may target only ancestors: their `README.md`, files in their
  `doc/decisions/` and files in their `doc/references/`. Siblings are never
  cited.
- Cite only what matters for this unit. Do not copy the ancestor's list.
- A unit with several ancestors MAY group the items by ancestor.
- The restatement of a definition, such as a data model or a contract the
  unit implements, may be longer than two lines.
- The title of a cited item is a quotation and may contain names that the
  unit must otherwise not mention.
- Other files of the unit refer to an inherited item by linking to this
  file.
- The root unit has nothing above it and normally has no `context.md`.

## architecture.md

`doc/architecture.md` is the long form of the `## Why` section of
`AGENTS.md`. Write it when the why does not fit there.

It MAY contain:

- the reasoning behind the decomposition into children,
- invariants: what must always or never be true inside the unit,
- behaviour over time, for example a hand-drawn sequence diagram,
- views that the folder tree cannot show, for example deployment,
- trade-offs, with links to the decisions that settled them.

It MUST NOT restate the structure: no list of children, no list of ports, no
description of who is wired to whom. That is in the manifest and in the
[generated diagrams](diagrams.md). It may link to them, name children in its
reasoning, and use tables that say something the manifest does not.

An invariant that child units must obey is recorded as a decision or a
reference, because children cannot cite this file.

## decisions/

Decision records use [MADR](https://adr.github.io/madr/). One file per
decision, named `NNNN-short-title.md` with a four-digit number that is unique
within the unit.

Front matter:

```yaml
---
status: proposed          # proposed | accepted | rejected | deprecated | superseded by NNNN
date: 2026-10-06
decision-makers: [name]   # optional
---
```

Body sections: `# Title`, `## Context and Problem Statement`,
`## Considered Options`, `## Decision Outcome` with `### Consequences`.
`## Decision Drivers`, `## Pros and Cons of the Options` and
`## More Information` are optional.

Rules:

- A decision belongs to the lowest unit whose insides it fully covers. A
  decision about how two siblings talk to each other belongs to their parent.
  A unit that owns a shared definition decides its shape; adopting a change
  that affects its users is a decision of their common parent.
- The title of a decision that child units will cite SHOULD NOT name a
  child.
- An accepted decision is not edited, except for its `status`. To change it,
  write a new decision and set the old one to `superseded by NNNN`.
- A decision written by an agent starts as `proposed`. Only a human sets
  `accepted`.
- Refer to a decision by a link. Inside the unit that owns it, the link text
  is the number. In `doc/context.md` of a unit below, it is unit and number,
  for example `cloud/0002`.
- `doc/decisions/index.md` is generated. It lists all decisions of the unit
  with status and date.

## references/

References hold facts that someone looks up: the contract of a port, a wire
format, a data model, a convention, a glossary.

- A reference is a file `doc/references/<topic>.md`.
- A reference that would exceed 200 lines is split: it becomes a folder
  `doc/references/<topic>/` with an `index.md` that links to every part.
- The contract of a provided port SHOULD live here, or in a machine-readable
  file that the manifest's `contract` field points to.
- A reference states facts in the present tense. Reasons go to decisions.
  A procedure of the system, such as the steps of a protocol, is a fact and
  belongs here. A procedure for whoever works on the unit is a skill.
- API reference that a tool can produce from code is not written by hand.

## skills/

A skill is a procedure: how to do a recurring task in this unit. Skills follow
the [Agent Skills](https://agentskills.io/specification) format.

```text
doc/skills/<skill-name>/
├── SKILL.md      required
├── scripts/      optional: executable helpers
└── assets/       optional: templates and other resources
```

`SKILL.md` begins with front matter:

```yaml
---
name: add-migration          # MUST equal the folder name
description: Add a schema migration to the storage unit. Use when a table changes.
---
```

Rules:

- The unit's `AGENTS.md` MUST link to every skill. See
  [unit-files.md](unit-files.md).
- A skill describes steps and checks. Facts it needs are linked from
  `doc/references/`.
- A skill belongs to the lowest unit in which the whole procedure takes place.
- Skill names SHOULD be unique in the project. Prefix them with the unit name
  when two units need a similar skill.
- A skill of a unit below the root refers to the three skills of the
  standard by name, for example "finish with the `check-docs` skill", without
  a link. Every project has them in its root unit.
- Files in `scripts/` and `assets/` are resources. The Markdown rules do not
  apply to them.

Agents do not discover `doc/skills/` by themselves. Discovery works through
`AGENTS.md`. A project MAY also expose the skills at the path its agent scans,
for example with symbolic links. youmedoc does not regulate that.

## diagrams/

`doc/diagrams/` contains only generated files: `context.md`, and for units
with children also `component.md` and `architecture.md`. See
[diagrams.md](diagrams.md). Diagrams drawn by hand belong in
`architecture.md`.

## assets/

`doc/assets/` holds images and other files that Markdown files of the unit
embed or link to.
