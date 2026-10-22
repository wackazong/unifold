---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Keep the reference chapters directly in docs/references

## Context and Problem Statement

The reference chapters of the standard lived in `docs/references/unifold/`. The subfolder came from [0008](0008-copy-the-standard-into-every-project.md): the chapters were copied into the root unit of every project, and the name kept them apart from the contracts, the glossary and the conventions of that project. This repository used the same path so that the layout was the same everywhere. [0028](0028-reference-the-standard-instead-of-copying-it.md) ended the copying, and [0035](0035-sort-the-docs-folder-by-diataxis.md) kept the subfolder without a reason.

## Considered Options

- Keep `docs/references/unifold/`
- Move the chapters to `docs/references/`

## Decision Outcome

Chosen option: "move the chapters to `docs/references/`", because nothing is copied into other projects any more, so the name protects nothing, and because this repository is not a unit and has no other references that the chapters could collide with.

- The chapters are `docs/references/<name>.md`, as the standard says a reference is.
- The site builder, the conformance suite and every link follow.

### Consequences

- Good: the repository of the standard follows the layout the standard describes, with one folder per kind and one file per topic.
- Good: relative links from the chapters climb one level less.
- Bad: every link to a chapter changes once, inside and outside this repository.
