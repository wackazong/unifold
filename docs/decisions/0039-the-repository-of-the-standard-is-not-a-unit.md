---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# The repository of the standard is not a unit

## Context and Problem Statement

This repository had a root `unifold.yaml` with `kind: specification` and a capability named `specification`, so that the standard could say it obeys itself. Decision 0038 says that a specification is never a unit: a unit holds code that is built, run or deployed. The repository holds the standard, two skills and the reference tool, but what it is, is the specification.

## Considered Options

- Keep the manifest and call the repository a unit because it ships a tool
- Drop the manifest; the examples are the projects that obey the standard

## Decision Outcome

Chosen option: "drop the manifest", because the standard should not keep an exception for itself that it refuses to every other specification.

- The root `unifold.yaml` is deleted. `AGENTS.md` and `docs/decisions/index.md` are hand-written; nothing here is generated.
- The documents of this repository follow the document conventions by choice, so that the chapters are an example of the sorting they ask for.
- Every rule is tried on the examples in `examples/`, each a project of its own, before a project has to follow it.

### Consequences

- Good: one rule, no exception for its author.
- Bad: the decision index of this repository is kept by hand.
- Bad: "the standard obeys itself" is no longer a claim the checker confirms; the examples carry that claim.
