---
status: proposed
date: 2026-10-25
---

# Read version 0.2 only

## Context and Problem Statement

[0049](0049-call-the-standard-0-2.md) called the standard 0.2 and had the tool read a project that says `unifold: "0.1"` with the meaning of 0.1, because 0.1 had been published days before. Version 0.1.0 of the tool was on PyPI for one day, on 2026-10-23, before 0049 was accepted, and no project outside this repository is known to say `"0.1"`. The second meaning of a wiring line costs a branch in the tool, a case in the conformance tests, a bullet in section 8 of [spec.md](../references/spec.md), the key `via` in the JSON of `show` and `capability`, and a second copy of the schema on the site.

## Considered Options

- Keep reading 0.1 with its old meaning
- Read 0.2 only, and report `"0.1"` with the fix to write `"0.2"`

## Decision Outcome

Chosen option: "read 0.2 only", because the compatibility protects nobody and every reader of the standard and the tool pays for it.

- The tool supports `"0.2"` only. A root manifest that says `"0.1"` gets `S1` with the fix to write `"0.2"`, as any unsupported version does.
- Section 8 of spec.md loses its last bullet. The schema allows `"0.2"` only, and the site serves the schema at `/0.2/` only.
- `show` and `capability` no longer print `via`; every connection is an explicit line.
- The rule of 0049 stands: a manifest must not change its meaning while its version string stays the same. From here on, a published version is read with its meaning.

This supersedes 0049.

### Consequences

- Good: one meaning of a wiring line in the tool, the tests and the standard.
- Bad: a project that says `"0.1"` has to write `"0.2"` and add a line for every need it passed up by name. None is known.
