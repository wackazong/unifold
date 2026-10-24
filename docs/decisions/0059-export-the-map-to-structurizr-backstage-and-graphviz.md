---
status: rejected
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Export the map to Structurizr, Backstage and Graphviz

## Context and Problem Statement

The [reasoning](../explanation/reasoning.md) of the standard says, about the Backstage catalog, "keep both", and takes from C4 and Structurizr the generated diagrams without the central model. Teams that already run a catalog or a C4 workspace then keep two descriptions of the same parts. Somebody writes the second one by hand, and it drifts from the first: the problem that unifold exists to remove.

The generated diagrams are Mermaid pages for a code host. A large map, or a view across the whole tree, needs a layout engine that a reader runs on their own machine.

## Considered Options

- No exporters; others write them on the model of [0057](0057-publish-the-resolved-map-as-a-model-with-a-schema.md)
- A command `unifold export` in the reference tool for three formats, built on the model
- Exporters as a separate package

## Decision Outcome

Chosen option: "`unifold export` in the reference tool", because a team adopts a map more readily when it feeds the tools the team already runs, and three exporters on one model are small enough to keep in one file.

- `unifold export FORMAT [PATH] [-o FILE]` writes to standard output by default. `FORMAT` is `structurizr`, `backstage` or `dot`.
- An export is not a generated file of section 6 of [spec.md](../references/spec.md). The standard does not check it and does not ask for it to be committed. The project decides where it goes.
- The kinds of [0058](0058-define-well-known-kinds.md) decide the mapping. Without them, every unit is a component.

### Structurizr

The [Structurizr DSL](https://docs.structurizr.com/dsl/language) has three fixed levels, and the tree of units has any depth.

- A unit of kind `system` becomes a software system. The root becomes one, whatever its kind.
- A unit of kind `service`, `app`, `firmware`, `tool` or `test` becomes a container of the nearest software system above it.
- Every other unit becomes a component of the nearest container above it. A component below a component is flattened into that container, and its name carries its path.
- A need of the root that the project does not meet becomes an external software system.
- A final connection becomes a relationship from the user to the provider. Its description is the summary of the need, and its technology is the kind. A connection with alternatives uses the default; the others carry the tag `alternative`.

### Backstage

The [descriptor format](https://backstage.io/docs/features/software-catalog/descriptor-format) of the catalog is one YAML document per entity.

- Every unit becomes an entity of kind `Component`. `spec.type` is the kind of the unit. `spec.lifecycle` is `experimental` for `planned`, `production` for `active` and `deprecated` for `deprecated`. `spec.subcomponentOf` is the parent.
- `spec.owner` is the inherited `owner`. Backstage requires an owner, so a unit without one gets `unknown`, and the export prints how many units have none.
- Every capability with a contract becomes an entity of kind `API`, with the contract file as its definition. `providesApis` and `consumesApis` come from the final connections.
- A need of the root that the project does not meet becomes an entity of kind `Resource`.
- Names are the project name and the path of the unit, joined with `-`.

### Graphviz

The export is a [DOT](https://graphviz.org/doc/info/lang.html) graph. Every unit with children is a cluster, and every leaf is a node. An edge goes from a user to its final provider. `--depth N` cuts the tree at a depth.

### Where it is written

- [tool.md](../references/tool.md) gets the command and the three mapping tables.
- `tests/` compares the exports of slugline and plantwatch with stored files.
- An exporter knows a file format, not a programming language, so the reason of [0047](0047-remove-the-comparison-with-code.md) for keeping knowledge out of the tool does not apply.

### Consequences

- Good: a team keeps its catalog or its C4 workspace, derived from the manifests and not written by hand.
- Good: the mapping shows where a project's units do not fit the levels of C4, which is useful review in itself.
- Bad: the tool follows three foreign formats, and each can change under it.
- Bad: the mapping to three levels loses depth, and the Backstage export is only as good as the `owner` keys.
- Bad: the tool grows by a few hundred lines.
