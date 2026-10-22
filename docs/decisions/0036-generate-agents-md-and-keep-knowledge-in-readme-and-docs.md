---
status: proposed
date: 2026-10-21
---
# Generate AGENTS.md and keep knowledge in README.md and docs

## Context and Problem Statement

[0009](0009-explain-the-why-and-never-write-structure-by-hand.md) made
`AGENTS.md` the home of the unit's why, its skills table, its commands and
its rules for work. That put the most important text of a unit into a file
that is named for one kind of reader, and it created a second place beside
`README.md` and `docs/` where project knowledge lives. People and agents
should read the same documents; what an agent needs that a person does not
is only a pointer to them.

## Considered Options

- Keep the why in `AGENTS.md`
- Leave `AGENTS.md` to the project and check nothing
- Generate `AGENTS.md` at level `full` and move its content to `README.md`
  and `docs/`

## Decision Outcome

Chosen option: "generate it", because everything the file then holds can be
derived: the skills of the unit, the documents of the unit by kind, and at
the root the unifold block with the unit index. What cannot be derived, the
why, moves to `README.md`.

- `README.md` gets a `## Why` section of at most 20 lines that are not
  blank: why the unit exists, why it is cut this way, what must stay true.
  The long form is `docs/explanation/reasoning.md`.
- `## Commands` and `## Read next` move to `README.md` as optional
  sections. Rules for work here become invariants
  (`docs/explanation/invariants.md`) or conventions
  (`docs/references/conventions.md`).
- `AGENTS.md` is a generated file at level `full`: the one line "unifold
  unit; run `unifold show` here", a pointer to `README.md`, the documents
  by kind, the skills table. The checker reports it like a stale diagram.
  At level `core` the tool keeps inserting only the root block.
- A hand-written `AGENTS.md` without the generated marker is never
  overwritten; the checker says what to move and asks for the file to be
  deleted.

This amends 0009: the rule "reasons and pointers only, never structure"
stands, but the reasons are in `README.md` and the pointers are generated.

### Consequences

- Good: one set of documents for people and agents; nothing is written
  twice for a second audience.
- Good: the skills table and the document list can no longer go stale.
- Bad: an agent that loads only `AGENTS.md` sees no reason at all until it
  opens `README.md`; the generated file says so in its first paragraph.
- Bad: `README.md` grows by a section that readers of a package registry
  may not expect.
- Bad: a project that wants free text in `AGENTS.md`, for example coding
  style for agents, has to put it into a reference or a skill, or keep a
  `CLAUDE.md` or similar file of its own beside it.
