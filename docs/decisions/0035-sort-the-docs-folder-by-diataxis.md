---
status: proposed
date: 2026-10-21
---
# Sort the docs folder by Diátaxis

## Context and Problem Statement

unifold is meant to hold all documentation of a project, for the people who
use a unit, the people who work inside it, and coding agents, from the first
day and also for a project of one unit. The `docs/` folder of a unit was a
list of fixed names (`context.md`, `architecture.md`, `decisions/`,
`references/`, `skills/`, `diagrams/`) without a stated idea of what kind of
knowledge goes where. A tutorial had no place; a procedure for an end user
had none either. The standard's own guide mixed reference pages with
explanation and how-to in one folder, `docs/references/unifold/`.

[Diátaxis](https://diataxis.fr) sorts documentation into four kinds by what
the reader is doing: tutorials (learning), how-to guides (a task), reference
(looking something up) and explanation (understanding).

## Considered Options

- Keep the fixed names and add more of them as needs arise
- One folder per Diátaxis kind, and nothing else, in `docs/`
- One folder per Diátaxis kind for hand-written prose, beside `decisions/`
  and `diagrams/`, which are records that tools index or write

## Decision Outcome

Chosen option: "four kinds beside `decisions/` and `diagrams/`", because a
reader who knows what they are doing then knows which folder to open, and a
writer knows where a new file goes without a list of names to remember.

- `docs/tutorials/<name>.md`: a lesson that leads a stated reader to a
  first result.
- `docs/skills/<name>/SKILL.md`: a how-to guide for a task, in the Agent
  Skills format, for people and agents alike.
- `docs/references/`: facts to look up, as before.
- `docs/explanation/`: the why, in files with fixed names
  ([0037](0037-split-the-explanation-into-one-file-per-arc42-concern.md))
  and topic files. `context.md` moves here from `docs/`.
- `docs/decisions/` and `docs/diagrams/` stay where they are: decision
  records are a dated log with its own format and tools, and diagrams are
  generated.
- The standard's own documents follow the same sorting: only reference
  pages stay in `docs/references/unifold/`; the design chapters become
  explanation files of this repository, and the first steps become a
  tutorial.

### Consequences

- Good: every hand-written file has one kind, and the kind says how it is
  written: a tutorial teaches, a skill instructs, a reference states, an
  explanation reasons.
- Good: end-user documentation has a place without a second structure.
- Bad: paths get longer (`docs/explanation/context.md`), and every upward
  link in an existing `context.md` changes.
- Bad: a unit with little to say has several nearly empty folders. The rule
  "create a file only when it has content" limits this.
- Bad: the tool reports an entry of `docs/` that fits no kind, so a `docs/`
  folder that also holds the source of a documentation site gets one
  finding per foreign entry.
