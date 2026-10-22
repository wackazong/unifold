---
status: proposed
date: 2026-10-07
---
# Ship one skill and generate stubs where agents look

## Context and Problem Statement

The standard had three skills (for reading, writing and checking), kept in
`docs/skills/` and announced only in `AGENTS.md`
([0004](0004-keep-skills-in-docs-skills-and-list-them-in-agents-md.md)).
Units below the root named them without a link
([0011](0011-name-the-standard-skills-instead-of-linking-upward.md)).
A check against the vendors' documentation showed that no agent searches
`docs/skills/`, so loading by description never happened; that the skills
linked to chapters by relative paths which break when a skill is reached
from another folder; and that their generic names collide with personal
skills. A benchmark found two or three skills better than four or more
([SkillsBench](https://arxiv.org/abs/2602.12670)).

## Considered Options

- Move skills into the agents' folders
- Keep three skills and add symbolic links
- One skill named `unifold`, self-contained; skills stay in `docs/skills/`;
  generated stub skills in `.agents/skills/` and `.claude/skills/`

## Decision Outcome

Chosen option: "one skill and generated stubs", because the source stays
with the unit, two folders reach eight of the ten agents examined, and
stub files work where symbolic links do not.

- The skill links to chapters only by `https://unifold.md/...` URL.
- `unifold skills sync` writes a stub per skill, with the same description
  and one line that names the file to read. A skill of the root keeps its
  name; a skill of another unit is `<unit>-<skill>`, or on a clash the
  unit's path with `-`.
- `unifold init --agents` installs the skill, writes the stubs and adds a
  block of about 15 lines, plus one row per unit, to the root `AGENTS.md`.

This supersedes 0011 and amends 0004: `docs/skills/` and the table in
`AGENTS.md` stay.

### Consequences

- Good: agents can load a skill by its description.
- Good: one skill of at most 200 lines instead of three.
- Bad: two more folders of generated files at the root, which can be
  stale; the checker reports that only when the folders exist.
- Bad: the skill needs network access to follow a link to a chapter.
- Bad: with all stubs at the root, a project with many skills can exceed
  the size to which some agents cut the list of skills.
- Bad: Kiro and Aider are not reached.
