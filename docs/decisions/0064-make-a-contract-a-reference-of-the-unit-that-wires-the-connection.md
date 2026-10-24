---
status: accepted
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Make a contract a reference of the unit that wires the connection

## Context and Problem Statement

[0038](0038-make-a-contract-the-document-of-a-connection.md) made the contract the document of a connection, and both sides name it. It left the form of that document open: `contract` could be a URL, or any path in the unit, an ancestor or a descendant. The example in section 2 of [spec.md](../references/spec.md) named `openapi.yaml` inside the providing unit, and the skill `unifold-convert` told agents to name an existing OpenAPI or `.proto` file. 0038 also let a chain that no sibling uses keep its contract in the implementing child. Plantwatch did that twice: `app-ui` in `mobile` and `test-report` in `test-rig`.

A contract was read in three ways: as a kind such as `http` or `json`, as a schema file beside the code, and as a document of the connection. Only the last one is what 0038 meant. A schema file lies with one side, so the other side has to name its provider to reach it, and it cannot hold the examples and the guarantees that a reader of the connection needs. A URL is checked for its form only.

## Considered Options

- Keep 0038, and say in the explanation what a contract is
- Make the form a recommendation: SHOULD be a reference of the unit that wires the connection
- Make it a rule: `contract` is a Markdown file in `docs/references/` of the unit or of an ancestor

## Decision Outcome

Chosen option: "make it a rule", because a contract is the one document both sides of a connection share, and its place follows from the wiring: the unit that wires the connection sees both sides.

- `contract` is a path, relative to the manifest, to a Markdown file that exists in `docs/references/` of the unit or of an ancestor. A URL, a file elsewhere in the unit, and a file in a descendant are errors of `M7`.
- With rule 8, both sides name the same file, so the contract of a connection between siblings lies in their parent or higher, and a capability that a parent passes through has its contract in the parent or higher. A capability of the root, or a need of the root from outside, has its contract in the root.
- A kind such as `http` is not a contract. A schema file such as `openapi.yaml` or a `.proto` is not a contract either; it stays with the code that uses it. A definition from outside the project gets a reference that links it by its URL.
- `verified-by` does not change: a URL, or a path in the unit, an ancestor or a descendant.
- The JSON Schema of the manifest gives `contract` a pattern: a relative path that ends in `.md`, with an optional fragment.
- Plantwatch moves `app-ui.md` and `test-report.md` into its own `docs/references/`.

This amends 0038: "a chain that no sibling uses may keep it in the implementing child" no longer stands, and a contract is never a URL. The rest of 0038 stands. The change applies to version 0.2: it was published one day before, and no project outside this repository is known to use the old form.

### Consequences

- Good: every contract can be found in the same place, and a reader of a connection opens one Markdown file with the form, the guarantees and examples.
- Good: no side names a file of its provider, not even through a schema beside the code.
- Bad: where a schema file defines the interface, the reference restates the form, and the two can drift. Review keeps them in step.
- Bad: a child that is copied elsewhere loses its contract, which 0038 already accepted for connections between siblings.
- Bad: a 0.2 project that named a URL or a file in a child gets errors without a change of version.
