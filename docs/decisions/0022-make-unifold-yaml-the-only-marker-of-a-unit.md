---
status: proposed
date: 2026-10-07
---
# Make unifold.yaml the only marker of a unit

## Context and Problem Statement

[0001](0001-mark-units-in-the-readme-front-matter.md) and
[0020](0020-keep-the-manifest-in-unit-yaml-by-default.md) allowed the
manifest in two places: as front matter of `README.md` or as a file
`unit.yaml`. The manifest also had a key `unit` that had to repeat the
folder name. Review round 3 found that two places double every parser and
every explanation, that the name `unit.yaml` identifies nothing and cannot
be searched for, and that the repeated name is pure redundancy with a rule
of its own. Folder names with dots, usual in .NET and Java, could not be
units, and two folders with the same name below one parent were an error.

## Considered Options

- Keep both places and the `unit` key
- `unit.yaml` only
- A file named after the standard, `unifold.yaml`, as the only marker; the
  folder name is the unit's name; the root may set `name`

## Decision Outcome

Chosen option: "`unifold.yaml` as the only marker", because one file name
is the whole test for "is this folder a unit", and the name tells a reader
who has never heard of the standard what to search for.

- The key `unit` and the front-matter form are removed.
- The only required key is `summary`. The root also has `unifold`.
- A wiring reference is split at its last dot, so folder names may contain
  dots. Where two children have the same folder name, the reference uses
  the path relative to the parent.

### Consequences

- Good: a unit at level `core` is one file of a few lines.
- Good: adoption can be counted by searching code hosts for the file name.
- Good: `README.md` is never touched by the standard at level `core`.
- Bad: renaming a folder renames the unit and breaks the wiring lines that
  name it. The checker reports them; nothing repairs them.
- Bad: the declaration and its explanation are always in two files.
- Bad: the file is added to every package folder and is published with
  the package unless the build tool is told to exclude it.
