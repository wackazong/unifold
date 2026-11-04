---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Context items link the source; no link goes sideways

## Context and Problem Statement

Hierarchical documentation lets children inherit silently from parents, which makes a child impossible to understand alone, and a file that links to a sibling couples two units that the wiring keeps apart. How does a unit take over what applies from above, and which links are allowed?

## Decision

- `docs/explanation/context.md` lists what a unit takes over from the units above: each item is a `###` heading that links to the smallest part of its source (a section, or a table row), followed by what it means for this unit, in the author's words. It cites only what matters here.
- No link goes sideways: the target of a link lies in the unit, in a unit above it or in a unit below it. What a unit wants from a sibling is a need. Links up and down are otherwise free; a nested project and anything outside the project are linked by full URL.
- When a source changes, `unifold impact FILE` lists every link to it, the context items marked; the reviewer reads them again. Nothing stamps or hashes a restatement.

## Consequences

- Good: a child can be understood from its own folder, and the one rule for links fits one sentence.
- Bad: nothing warns when a cited source changes; review does that.
