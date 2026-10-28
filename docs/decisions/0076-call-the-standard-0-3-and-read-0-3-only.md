---
status: proposed
date: 2026-10-27
---

# Call the standard 0.3 and read 0.3 only

## Context and Problem Statement

The decisions 0065 to 0075 change the manifest: `summary` becomes `responsibility`, `verified-by` goes, `kind` is required on a composite, and `secret`, `not`, `parts` and `scenarios` arrive. A 0.2 manifest does not mean the same thing any more.

## Considered Options

- Call it 0.3 and read 0.2 with its old meaning, as [0049](0049-call-the-standard-0-2.md) did for 0.1
- Call it 0.3, read 0.3 only, and add a migration command
- Call it 0.3 and read 0.3 only; the two examples are rewritten by hand

## Decision Outcome

Chosen option: "0.3 only, no migration", because nobody runs 0.2 in production, a migration tool that rewrites YAML drops comments, and two meanings of a manifest in one tool is the cost 0049 paid once already. Multi-version support is a decision for the first version after adoption.

- The root manifest says `unifold: "0.3"`; the package of the tool is 0.3.0; the schema is served at `/0.3/`.
- Any other version is an error whose fix text lists what changed.

### Consequences

- Good: one meaning of a manifest in the tool.
- Bad: a 0.2 project is rewritten by hand before it checks again.
