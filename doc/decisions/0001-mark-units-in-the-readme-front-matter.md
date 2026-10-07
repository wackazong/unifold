---
status: proposed
date: 2026-10-06
---
# Mark units by a manifest, not by the folder name

## Context and Problem Statement

Only some folders are units. Readers and tools must be able to tell which.
The marker should be visible, cheap to add and remove, and must not disturb
other tools that work on the same folders.

## Considered Options

- A suffix in the folder name, such as `storage.unit`
- YAML front matter with the key `unit` in the folder's `README.md`
- A separate file `unit.yaml`
- Front matter or `unit.yaml`, whichever suits the unit

## Decision Outcome

Chosen option: "front matter or `unit.yaml`", because front matter keeps the
declaration next to the text that explains it, and a separate file keeps a
published `README.md` clean.

The folder-name suffix was rejected for these reasons:

- Folder names belong to the code. In many ecosystems they are module,
  package or import names and may not contain a dot.
- Some dotted suffixes already have a meaning, for example `.app`.
- Being a unit is optional and changes over time. Renaming a folder breaks
  imports, build paths, links and the file history.

Front matter alone was rejected after a reviewer rendered a manifest the way
a package registry does: the registry showed it as a rule and a heading above
the title. The root `README.md` is also the front page of a project and
should start with its title.

### Consequences

- Good: any folder can become a unit, or stop being one, by editing a file.
- Good: with `unit.yaml`, an agent that resolves wiring reads a small YAML
  file instead of a whole `README.md`, and editors can apply the JSON Schema.
- Bad: two places to look. The tool accepts both; a unit must not use both.
- Bad: units cannot be seen in a plain directory listing. `youmedoc tree`
  lists them.
