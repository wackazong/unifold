---
status: proposed
date: 2026-10-07
---
# Reference the standard instead of copying it

## Context and Problem Statement

[0008](0008-copy-the-standard-into-every-project.md) copied the chapters
and the skills into every project, so that agents could read the rules
without network access. In use the copy was 32 to 36 files and about
100 KB. It appeared in every search of the project, with examples whose
names resembled the project's own; a local edit of it went unnoticed; and
`init` had to replace it on every update. Reviewers named it as a reason
not to adopt.

## Considered Options

- Keep the copy
- Keep the copy and add checksums
- Copy nothing: the root manifest names the version, projects link to
  `https://unifold.md`, the tool is installed as a package, and
  `init --agents` installs only the skill with its templates and the tool

## Decision Outcome

Chosen option: "copy nothing", because the standard for level `core` now
fits on one page that a tool implements, and a project should carry its
own files only.

- `pyproject.toml` makes the tool installable (`uvx unifold`,
  `pipx run unifold`) once the package is published. A pre-commit hook, a
  GitHub Action and a Claude Code plugin are provided.
- The skill is self-contained for the usual procedures and links to the
  site for the rest.

### Consequences

- Good: a project at level `core` contains manifests and generated
  diagrams, nothing else.
- Good: project search finds only the project.
- Bad: without network access an agent has the skill but not the
  chapters.
- Bad: the site must keep every published version available, because the
  root manifest names a version and nothing in the project holds its text.
- Bad: until the package is published, running the tool needs a clone of
  the standard's repository.
- Bad: a project with `--agents` still carries a copy of the skill and the
  tool, which can fall behind.
