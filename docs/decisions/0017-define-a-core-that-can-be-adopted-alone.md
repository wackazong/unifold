---
status: superseded by 0023
date: 2026-10-07
---
# Define a core that can be adopted alone

## Context and Problem Statement

A second review by a tech lead and by an open-source maintainer came to the
same result: the idea that can spread is small, namely manifests, wiring, a
check and generated diagrams, and it was buried in about 2 000 lines of text
with 57 rules, 30 copied files and a mandatory tool. A convention that wants
wide use must be followable from one page.

## Considered Options

- Keep one level: everything or nothing
- Three levels: core, documented, reviewed
- Two levels, `core` and `full`, named in the root manifest, with "checked"
  and "reviewed" as claims at either level

## Decision Outcome

Chosen option: "two levels", because the step from "structure only" to
"structure plus written knowledge" is the one real threshold, and a third
level would be a claim nobody can verify.

- A chapter `core.md` states ten rules on one page.
- At level `core` nothing is copied into the repository, no `AGENTS.md` is
  required, and the tool applies only the structure, manifest, wiring and
  generation rules.
- `unifold init --level core` starts such a project with two files.

### Consequences

- Good: a project can try the part with the clearest benefit in minutes.
- Good: the full standard keeps the copy of the text and the skills that
  agents need offline.
- Bad: two levels to explain, and a core project has no rule against upward
  or sideways links.
- Bad: the ten rules are stated in `core.md` and again, in detail, in the
  chapters.
