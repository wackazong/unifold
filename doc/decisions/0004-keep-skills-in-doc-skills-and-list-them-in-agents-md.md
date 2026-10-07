---
status: proposed
date: 2026-10-06
---
# Keep skills in doc/skills and list them in AGENTS.md

## Context and Problem Statement

Procedures should live in the unit they concern and travel with it. Coding
agents discover skills only in fixed folders such as `.claude/skills/` or
`.agents/skills/`. None scans `doc/skills/`.

## Considered Options

- Store skills where one agent product scans
- Store skills in `doc/skills/` and require every unit's `AGENTS.md` to link
  to each of them
- Store skills in `doc/skills/` and generate links into the agents' folders

## Decision Outcome

Chosen option: "`doc/skills/` plus a table in `AGENTS.md`", because it keeps
all knowledge of a unit under one folder, does not tie the standard to one
agent product, and relies only on agents reading `AGENTS.md`, which is the
most widely supported mechanism.

### Consequences

- Good: the unit's knowledge is in one place and is copied as one folder.
- Good: one published evaluation found that agents use a documented index in
  `AGENTS.md` more reliably than skills they must discover themselves.
- Bad: an agent that does not read `AGENTS.md` in a folder never learns of
  the skills there. Automatic skill loading by description does not happen.
- Bad: projects that want native discovery must add links or copies for
  their agent themselves. The standard allows this and does not define it.
