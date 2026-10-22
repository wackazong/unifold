---
status: superseded by 0022
date: 2026-10-07
---
# Keep the manifest in unit.yaml by default

## Context and Problem Statement

[0001](0001-mark-units-in-the-readme-front-matter.md) allows the manifest as
front matter of `README.md` or as a file `unit.yaml`. The example used front
matter in 22 of 23 units. Three reviews objected: a parent's `README.md`
opened with up to 38 lines of YAML; a package registry shows front matter as
stray text; an editor cannot check front matter against the schema; and the
wiring, which is the unit's inside, stood in the file meant for outsiders.

## Considered Options

- Front matter only
- `unit.yaml` only
- Both allowed, `unit.yaml` as the default in templates, tool and examples

## Decision Outcome

Chosen option: "both allowed, `unit.yaml` by default", because the file form
has the practical advantages, and front matter remains a legitimate choice
for small units whose `README.md` is read only inside the repository.

### Consequences

- Good: every `README.md` starts with its title.
- Good: tools and agents read a small file to learn the structure.
- Bad: a unit has three files at least (two at level `core`).
- Bad: the declaration and its explanation are in two files that can
  disagree. Tool rule `T5` reports a `README.md` section for a port the
  manifest does not have.
