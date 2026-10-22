---
status: superseded by 0028
date: 2026-10-06
---

# Copy the standard into every project

## Context and Problem Statement

Agents need the rules while they work. They may have no network access, and a link to a web page does not tell them which version a project follows.

## Considered Options

- Link to the published standard only
- Copy the chapters, the three skills and the tool into the root unit of each project, and record the version in the root manifest
- Publish the tool as a package and keep only the text in the project

## Decision Outcome

Chosen option: "copy everything into the root unit", because the project is then self-contained, the version is explicit, and the tool that checks a project is the one that matches its copy of the rules.

The root `README.md` also links to the published standard for human readers.

### Consequences

- Good: works offline, and the same paths exist in every project.
- Good: updating the standard is one visible change in version control.
- Bad: about thirty files of the standard sit in every repository. For a small library that is more than its own documentation. A lighter mode, in which a project keeps only the `read-docs` skill and refers to the published standard by URL, needs a stable published address first and is left open.
- Bad: copies fall behind. Nothing tells a project that a newer version exists.
- Bad: someone may edit the copy. The standard forbids it; nothing prevents it.
