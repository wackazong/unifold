---
status: proposed
date: 2026-10-06
---
# Mark units in the README front matter, not in the folder name

## Context and Problem Statement

Only some folders are units. Readers and tools must be able to tell which.
The marker should be visible, cheap to add and remove, and must not disturb
other tools that work on the same folders.

## Considered Options

- A suffix in the folder name, such as `storage.unit`
- A separate marker file, such as `unit.yaml`
- YAML front matter with the key `unit` in the folder's `README.md`

## Decision Outcome

Chosen option: "front matter in `README.md`", because it needs no extra file,
keeps the declaration next to the text that explains it, and leaves folder
names alone.

The folder-name suffix was rejected for these reasons:

- Folder names belong to the code. In many ecosystems they are module,
  package or import names (Python, Go, Java, Rust modules) and may not
  contain a dot. A suffix would break builds or be impossible.
- Some dotted suffixes already have a meaning, for example `.app` and
  `.xcodeproj`.
- Being a unit is optional and changes over time. Renaming a folder to make
  it a unit breaks imports, build paths, links and the file history.
- It contradicts the principle that the folder tree is the code layout.

### Consequences

- Good: any folder can become a unit, or stop being one, by editing a file.
- Good: code hosting platforms show the `README.md` when a folder is opened,
  so the interface is the first thing a reader sees.
- Bad: units cannot be seen in a plain directory listing. `youmedoc tree`
  lists them.
- Bad: package registries that publish the `README.md` show the front matter.
