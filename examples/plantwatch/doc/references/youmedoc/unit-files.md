# The files of a unit

Every unit has two required files. Everything else is optional and lives in
`doc/` ([doc-folder.md](doc-folder.md)).

```text
<unit>/
├── README.md     required: the interface
├── AGENTS.md     required: the why, and pointers
└── doc/          optional
```

A file is created only when there is something to put in it. Empty folders and
placeholder files MUST NOT be created.

## README.md: the interface

`README.md` is the only file of a unit that outsiders are expected to read. It
describes the unit as a closed box.

### Manifest

The file MUST begin with the manifest as YAML front matter. The fields are
defined in [manifest.md](manifest.md).

### Body

The body explains the interface in words. It MUST be understandable without
opening any other file. It SHOULD use these sections:

| Section | Content |
|---|---|
| `# <unit name>` | Title, followed by one paragraph: what the unit is and what it is for |
| `## Provides` | One `###` subsection per provided port: what it offers, what it guarantees, its limits, a link to its contract, a short example |
| `## Needs` | One `###` subsection per need: what the unit expects from whoever provides it |
| `## Out of scope` | What the unit deliberately does not do |
| `## More` | Links to `AGENTS.md`, the diagrams and other files of the unit |

Rules for the body:

- It describes behaviour that a user of the unit can rely on. It MUST NOT
  describe how the unit is built inside.
- It MUST NOT name siblings, the parent or users of the unit.
- It MUST NOT repeat the manifest as a list. The manifest already lists the
  ports. The body adds what one line cannot say.
- A port whose `summary` says everything needs no subsection. A section
  that would be empty is omitted.
- For a need that is `optional`, the body says what the unit does without
  it.
- A need is described in the unit's own words. The body does not copy names,
  identifiers or layouts from the contract of whoever provides it.

### Delegated ports

When the [wiring](wiring.md) delegates a provided port to a child, or passes
a child's need up, the port appears in two manifests and is described in two
`README.md` files.

- The parent describes what the unit as a whole guarantees or expects. It
  writes this in its own words and does not copy the child's text.
- The child describes its own port without mentioning the parent.
- The contract has one home. It lives in the parent if the port combines
  several children or the parent adds something to it. Otherwise it lives in
  the child, and the parent's manifest has no `contract` for that port.
- A child that implements a contract owned by its parent cites it in
  `doc/context.md`.

### The root README

The root unit's `README.md` is also the project's front page. In addition to
the sections above it SHOULD say that the project is documented with youmedoc
and link to the standard:

```markdown
This repository is documented with [youmedoc](https://youmedoc.example).
Start with [AGENTS.md](AGENTS.md).
```

## AGENTS.md: the why, and pointers

`AGENTS.md` is the entry point for an agent that starts working in the unit.
Many coding agents load this file by themselves when they touch the folder. A
human reads it to learn why the unit looks the way it does.

It explains **why** the unit is composed as it is. It does not explain
**how** it is composed: the structure is in the manifest and in the generated
diagrams.

### Sections

| Section | Required | Content |
|---|---|---|
| `# AGENTS.md: <unit name>` | yes | Title, then one line that says the folder is a youmedoc unit and links to the standard |
| `## Why` | yes | Why the unit exists and why it is cut this way: the forces, the main trade-off, what must stay true. At most about 15 lines of prose. |
| `## Read next` | yes | Ordered links: `README.md`, then `doc/context.md`, `doc/architecture.md`, the diagrams, the decision index, the main references, as far as they exist |
| `## Skills` | if the unit has skills | A table: one row per skill in `doc/skills/`, with a link to its `SKILL.md` and when to use it |
| `## Rules for work here` | no | Constraints and pitfalls that hold in this unit and cannot be derived from code |

### Rules

- `AGENTS.md` MUST link to every skill of the unit. Agents do not search
  `doc/skills/`; this table is how they find a skill.
- It MUST NOT list the child units, the ports or the wiring. Naming a child
  inside a sentence of reasoning, with a link to its `README.md`, is fine.
- A rule or invariant that child units must follow is recorded as a decision
  or a reference, and `AGENTS.md` links to it. Children can cite decisions
  and references in their `doc/context.md`; they cannot cite an `AGENTS.md`.
- It MUST NOT repeat what an ancestor's `AGENTS.md` says. Inherited rules are
  cited in `doc/context.md`.
- It MUST NOT contradict an ancestor's `AGENTS.md`. Agents that load several
  of these files do not resolve conflicts reliably.
- Step-by-step procedures belong in skills. `AGENTS.md` links to them.
- If the why needs more than about 15 lines of prose, the rest goes to
  `doc/architecture.md` and `AGENTS.md` keeps a summary and a link.

### The root AGENTS.md

The root unit's `AGENTS.md` additionally:

- MUST tell the reader to use the
  [read-docs](../../skills/read-docs/SKILL.md) skill before anything else,
- MUST list the three skills of the standard in its skills table,
- SHOULD state the project-wide rules that every agent must know, in a few
  lines, or link to the reference that holds them.

In a project the link reads `doc/skills/read-docs/SKILL.md`, relative to the
root.

### Agents that read another file name

Some agents load a file with a different name. youmedoc does not regulate
that. If your agent needs it, add a bridge file next to `AGENTS.md` that only
points to it.

## What goes where

| You want to record | Put it in |
|---|---|
| What the unit offers and requires | manifest in `README.md` |
| What a user can rely on | body of `README.md` |
| Why the unit is built this way | `AGENTS.md`, overflow in `doc/architecture.md` |
| A rule inherited from above | `doc/context.md` |
| A choice between options, with reasons | `doc/decisions/` |
| A fact to look up: format, protocol, term | `doc/references/` |
| A procedure: how to do a task here | `doc/skills/` |
| Which units exist and how they connect | nowhere by hand; it is generated |
