# The files of a unit

Every unit has a manifest and two required files. Everything else is optional
and lives in `doc/` ([doc-folder.md](doc-folder.md)).

```text
<unit>/
├── README.md     required: the interface
├── AGENTS.md     required: the why, and pointers
├── unit.yaml     the manifest, unless it is the front matter of README.md
└── doc/          optional
```

A file is created only when there is something to put in it. Empty folders and
placeholder files MUST NOT be created. A small unit is complete with a
manifest, a `README.md` of a few lines and an `AGENTS.md` of ten.

## README.md: the interface

`README.md` is the only file of a unit that outsiders are expected to read. It
describes the unit as a closed box. The manifest sits next to it in
`unit.yaml`, or is its front matter ([manifest.md](manifest.md)).

### Body

The body explains the interface in words. It MUST be understandable without
opening any other file. It SHOULD use these sections:

| Section | Content |
|---|---|
| `# <unit name>` | Title, followed by one paragraph: what the unit is and what it is for |
| `## Provides` | One `###` subsection per provided port: what it offers, what it guarantees, its limits, a link to its contract, a short example |
| `## Needs` | One `###` subsection per need: what the unit expects from whoever provides it |
| `## Out of scope` | What the unit deliberately does not do |
| `## More` | Links to `AGENTS.md`, `doc/context.md`, the diagrams and the decision index |

Rules for the body:

- It describes behaviour a user of the unit can rely on. It MUST NOT describe
  how the unit is built inside.
- It MUST NOT name siblings, the parent or users of the unit.
- Every guarantee is stated so that it can be checked: it names a value, a
  limit, an order or a response ([principles.md](principles.md)).
- It does not repeat the manifest as a list. A port whose `summary` says
  everything needs no subsection. A section that would be empty is omitted.
- For a need that is `optional`, the body says what the unit does without it.
- A need is described in the unit's own words. The body does not copy names,
  identifiers or layouts from the contract of whoever provides it.

### Delegated ports

When the [wiring](wiring.md) delegates a provided port to a child, or passes
a child's need up, the port appears in two manifests.

- The parent describes what the unit as a whole guarantees or expects, in its
  own words. It adds only what is true of the whole and does not copy the
  child's text.
- The child describes its own port without mentioning the parent.
- The contract has one home. It lives in the parent if the port combines
  several children or the parent adds something to it. Otherwise it lives in
  the child, and the parent's manifest has no `contract` for that port. If
  each level defines something of its own, both may have a contract; the
  child's says which part it refines and cites the parent's in
  `doc/context.md`.
- A child that implements a contract owned by its parent cites it in
  `doc/context.md`.
- A need that a unit passes up keeps its subsection: it states what the unit
  as a whole expects, precisely enough to be compared with a provider one
  level up (`C13`). The reviewer there cannot look into the child.

### The root README

The root unit's `README.md` is also the front page of the project. It keeps
whatever a front page needs, such as installation, status, contributing and
licence, in sections of its own. In addition it SHOULD:

- say that the project is documented with unifold and link to the standard,
- link to the architecture diagram as the map of the project,
- keep its manifest in `unit.yaml`, so that the page starts with its title.

## AGENTS.md: the why, and pointers

`AGENTS.md` is the entry point for an agent that starts working in the unit.
Many coding agents load this file by themselves when they touch the folder. A
human reads it to learn why the unit looks the way it does.

It explains **why** the unit is composed as it is. It does not explain
**how** it is composed: the structure is in the manifest and in the generated
diagrams.

| Section | Required | Content |
|---|---|---|
| `# AGENTS.md: <unit name>` | yes | Title, then one line saying that the folder is a unifold unit and where the standard's skills are |
| `## Why` | yes | Why the unit exists, what makes it change, and why it is cut this way: the forces, the main trade-off, what must stay true. At most 20 non-blank lines (`T4`). |
| `## Read next` | yes | Ordered links: `README.md`, then `doc/context.md`, `doc/architecture.md`, the diagrams, the decision index, the main references, as far as they exist |
| `## Skills` | if the unit has skills | A table: one row per skill in `doc/skills/`, with a link to its `SKILL.md` and when to use it |
| `## Commands` | no | The few commands needed to build, test and run the unit, at most ten lines. Longer procedures are skills. |
| `## Rules for work here` | no | Constraints and pitfalls that hold in this unit and cannot be derived from code |

Rules:

- The first lines below the title of a unit that is not the root say, in
  substance: "This folder is a unifold unit. The standard and its skills
  `read-docs`, `write-docs` and `check-docs` are in the project root, the
  nearest folder above whose manifest contains `unifold`. From there,
  `python3 doc/skills/check-docs/scripts/unifold.py show <this folder>`
  prints this unit with its neighbours." The command is written from the
  root, with the path of the unit. It is the one place where a unit states
  its own location; correct it when the unit is moved.
- `AGENTS.md` MUST link to every skill of the unit. Agents do not search
  `doc/skills/`; this table is how they find a skill.
- It MUST NOT list the child units, the ports or the wiring. Naming a child
  inside a sentence of reasoning, with a link to its `README.md`, is fine.
- A rule or invariant that child units must follow is recorded as a decision
  or a reference, and `AGENTS.md` links to it. Children can cite decisions
  and references in their `doc/context.md`; they cannot cite an `AGENTS.md`.
- It MUST NOT repeat or contradict an ancestor's `AGENTS.md`. Agents that
  load several of these files do not resolve conflicts reliably.
- If the why needs more than 20 lines, the rest goes to
  `doc/architecture.md` and `AGENTS.md` keeps a summary and a link.

### The root AGENTS.md

The root unit's `AGENTS.md` additionally:

- MUST tell the reader to use the
  [read-docs](../../skills/read-docs/SKILL.md) skill before anything else
  (in a project the link reads `doc/skills/read-docs/SKILL.md`),
- MUST list the three skills of the standard in its skills table,
- SHOULD state the project-wide rules that every agent must know, in a few
  lines, or link to the reference that holds them.

## What goes where

| You want to record | Put it in |
|---|---|
| What the unit offers and requires | the manifest |
| What a user can rely on | body of `README.md` |
| The exact definition of a port | a contract: an interface file or `doc/references/` |
| Why the unit is built this way | `AGENTS.md`, overflow in `doc/architecture.md` |
| A rule inherited from above | `doc/context.md` |
| A choice between options, with reasons | `doc/decisions/` |
| A fact to look up: format, protocol, term | `doc/references/` |
| A procedure: how to do a task here | `doc/skills/` |
| Which units exist and how they connect | nowhere by hand; it is generated |
