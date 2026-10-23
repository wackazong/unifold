---
status: superseded by 0047
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Compare the wiring with dependencies observed in code

## Context and Problem Statement

Every reviewer named the same largest gap: nothing connects the documents to the code. A project can pass every check and describe software that differs. The standard must stay independent of programming languages.

## Considered Options

- Leave it out of scope
- Parse code in the tool, per language
- Define a small exchange format for observed dependencies; the project produces it with whatever its language offers, the tool compares

## Decision Outcome

Chosen option: "an exchange format", because every build system or import scanner can list which file depends on which, and the comparison itself needs no knowledge of a language.

`check --deps FILE` reads a JSON list of `{"from", "to"}` paths. `D1` reports a dependency between two units that no wiring line allows. `D2` reports a wiring line of kind `library` for which no dependency was seen.

### Consequences

- Good: the wiring becomes an enforceable description of the architecture.
- Good: no language is built into the tool.
- Bad: each project has to write or find its own extractor. None is supplied yet.
- Bad: the check is as coarse as units: it cannot tell which port a dependency uses, and it sees nothing of calls over a network.
