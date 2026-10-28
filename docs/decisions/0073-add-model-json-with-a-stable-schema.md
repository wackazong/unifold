---
status: proposed
date: 2026-10-27
---

# Add a model command with a stable schema

## Context and Problem Statement

[0057](0057-publish-the-resolved-map-as-a-model-with-a-schema.md) proposed a resolved model with a schema and was rejected: no tool depended on it. Now one does. The build process maike plans its steps from the final providers, reads scenarios with their hops resolved to connections, and finds its open questions among the decisions. It must not implement section 3 of the standard again.

## Considered Options

- Let the process tool read the JSON of `show`, unit by unit
- A command `model` that prints the resolved project with a documented, versioned schema

## Decision Outcome

Chosen option: "a model command", because a process tool needs the whole project at once, and a schema that changes only with a decision lets it pin one version.

- `unifold model --json` prints every unit with path, kind, status, responsibility, secret, not; capabilities and needs with contract, parts and the parts the contract defines; every wiring line; the final provider of every need and the final users of every capability; for every need of the root the units that reach it; every scenario with every hop resolved to a connection; every decision with status and whether it has an empty `## Answer`.
- Keys that start with `x-` are passed through under `x`.
- The schema is in `tool-json.md` and changes only with a decision; a key is never removed within 0.3.

This supersedes 0057.

### Consequences

- Good: a process tool reads one document and nothing else.
- Bad: every key is a promise, as 0057 already said.
