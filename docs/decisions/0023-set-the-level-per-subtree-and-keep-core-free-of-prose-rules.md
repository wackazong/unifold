---
status: superseded by 0040
date: 2026-10-07
---

# Set the level per subtree and keep core free of prose rules

## Context and Problem Statement

[0017](0017-define-a-core-that-can-be-adopted-alone.md) introduced the levels `core` and `full`, set once in the root manifest, with `full` as the default. Two trials on real repositories tried to bring one part to `full` and could not: switching the root gave 29 and 62 errors across units that nobody had touched. At `core`, rules still read `README.md` files (title, names in code font, length) and gave false alarms on ordinary package READMEs. The claims "checked" and "reviewed" formed a matrix of which one half could not be verified.

## Considered Options

- Drop levels; switch conventions on by the presence of files
- Keep the root-wide level
- `level` in any manifest, inherited by the subtree, default `core`; at `core` no rule reads prose

## Decision Outcome

Chosen option: "level per subtree, default `core`", because a team can then document the one part it cares about and keep a green check, and because an explicit key is easier to explain and to check than "the rules apply if a file happens to exist".

- `core`: only the manifest is required. Checked: manifests, wiring, generated files, the comparison with code, and that named paths exist.
- `full`: also `README.md` and `AGENTS.md`, and the document conventions for the files of that unit.
- One conformance claim remains: no error from a conforming checker.

### Consequences

- Good: the default asks for nothing but YAML.
- Good: `full` can start in one folder.
- Bad: a project can now have two dialects side by side; a reader must look at the manifests to know which conventions hold in a folder.
- Bad: a unit at `full` may cite decisions of ancestors at `core`, whose form nobody checks.
- Bad: the review of meaning is no longer part of any claim. It was never verifiable, but it was visible.
