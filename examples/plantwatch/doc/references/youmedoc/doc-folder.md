# The doc folder

A unit MAY have a folder named `doc/`. It holds the unit's internal knowledge.
Outsiders are not expected to read it. The files outside `doc/` are described
in [unit-files.md](unit-files.md).

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

The checker manages these entries and nothing else. A `doc/` folder is never
a unit and never contains units.

## context.md

`doc/context.md` lists what the unit inherits from the levels above it:
decisions, conventions and terms that a reader must know to understand the
unit. It is the **only** hand-written file of a unit that may link upward.

Each item is a short section:

```markdown
### [cloud/0002 Each service owns its data](../../doc/decisions/0002-each-service-owns-its-data.md)

Says: no service reads or writes the database schema of another.

Here: `ingest` keeps its duplicate index in a schema of its own.
```

The heading links to the source. "Says" restates the item. "Here" gives the
consequence for this unit. The restatement is deliberate redundancy: it keeps
the unit understandable when the folder is read or copied on its own.

Rules:

- A unit that relies on anything decided or defined above it MUST have
  `doc/context.md` and MUST cite it there.
- Links may target only ancestors: their `README.md`, files in their
  `doc/decisions/` and files in their `doc/references/`. Siblings are never
  cited.
- "Says" has at most about 200 characters. Restate only the part this unit
  uses. The restatement of something the unit implements, such as a data
  model, a contract or a calling convention, may be longer.
- Cite only what matters for this unit. A context file with more than about
  ten items usually copies its ancestors instead of selecting from them.
  Several items may cite different sections of one file.
- Inheritance is not repeated: if a parent's reference already restates a
  rule of the root, the unit cites the parent's reference only.
- A heading for a source that is not a decision reads
  `<unit>: <file topic>, <section>`.
- A unit with several ancestors groups the items by ancestor under `##`
  headings.
- The title of a cited item is a quotation and may contain names that the
  unit must otherwise not mention.
- Other files of the unit refer to an inherited item by linking to this file.
- When a cited source changes, every restatement of it is checked. The
  [checker](checker.md) lists the files that cite a source (`cited-by`).

## architecture.md

`doc/architecture.md` is the long form of the `## Why` section of
`AGENTS.md`. Write it when the why does not fit there. It MAY contain the
reasoning behind the decomposition, invariants, behaviour over time as a
hand-drawn diagram, views the folder tree cannot show such as deployment, and
trade-offs with links to the decisions that settled them.

It MUST NOT restate the structure: no list of children, no list of ports, no
description of who is wired to whom. It may link to the
[generated diagrams](diagrams.md), name children in its reasoning, and use
tables that say something the manifest does not.

An invariant that child units must obey is recorded as a decision or a
reference, because children cannot cite this file.

## decisions/

Decision records use [MADR](https://adr.github.io/madr/). One file per
decision, named `NNNN-short-title.md` with a four-digit number that is unique
within the unit. Front matter:

```yaml
---
status: proposed              # proposed | accepted | rejected | deprecated | superseded by NNNN
date: 2026-10-06
decision-makers: [name]       # required once the status is accepted
---
```

Body sections: `# Title`, `## Context and Problem Statement`,
`## Considered Options`, `## Decision Outcome` with `### Consequences`.

Rules:

- A decision belongs to the lowest unit whose insides it fully covers. A
  decision about how two siblings talk to each other belongs to their parent.
  A unit that owns a shared definition decides its shape; adopting a change
  that affects its users is a decision of their common parent.
- A decision written by an agent starts as `proposed`. Only a human sets
  `accepted`, and names the people who decided in `decision-makers`.
- An accepted decision is not edited, except for its `status`. To change it,
  write a new decision and set the old one to `superseded by NNNN`.
- Only `accepted` decisions bind. A unit with `status: active` does not rely
  on a decision that is still `proposed`.
- The title of a decision that child units will cite SHOULD NOT name a child.
- Refer to a decision by a link. Inside the unit that owns it, the link text
  is the number; in `doc/context.md` of a unit below, unit and number, for
  example `cloud/0002`.
- `doc/decisions/index.md` is generated.

## references/

References hold facts that someone looks up: the contract of a port, a wire
format, a data model, a convention, a glossary.

- A reference is a file `doc/references/<topic>.md`. One that would exceed
  200 lines becomes a folder `doc/references/<topic>/` with an `index.md`
  that links to every part.
- `doc/references/glossary.md` is the glossary of the unit: the terms that
  have one fixed meaning inside it. A term is defined in the lowest unit that
  covers all its uses. Terms of ancestors still apply; the unit cites the
  ones whose exact wording matters in `doc/context.md`.
- A contract SHOULD contain examples: concrete cases with inputs and expected
  results ([principles.md](principles.md)).
- A reference states facts in the present tense. Reasons go to decisions. A
  procedure of the system, such as the steps of a protocol, is a fact and
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

`SKILL.md` begins with front matter that has a `name`, equal to the folder
name, and a `description` that says what the skill does and when to use it.

- The unit's `AGENTS.md` MUST link to every skill.
- A skill describes steps and checks. Facts it needs are linked from
  `doc/references/`.
- A skill belongs to the lowest unit in which the whole procedure takes place.
  Where a skill of the unit and a skill of the standard cover the same task,
  the unit's skill is followed and the standard's supplies what it leaves
  open.
- Skill names SHOULD be unique in the project; prefix them with the unit name.
- A skill of a unit below the root refers to the three skills of the
  standard by name, for example "finish with the `check-docs` skill", without
  a link.
- Files in `scripts/` and `assets/` are resources. The Markdown rules do not
  apply to them.

## diagrams/ and assets/

`doc/diagrams/` contains only generated files ([diagrams.md](diagrams.md)).
`doc/assets/` holds images and other files that Markdown files of the unit
embed or link to.
