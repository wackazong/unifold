---
status: proposed
date: 2026-10-27
---

# Give a contract a body with parts and a fake

## Context and Problem Statement

[0038](0038-make-a-contract-the-document-of-a-connection.md) made the contract the document of a connection and asked for examples; its body was free. A consumer that is built against a fake of its provider needs more: the parts of the contract by name, a signature per part, preconditions, results, errors, examples that are tests, and the behaviour of the fake. Without that, each consumer invents a fake and the parts meet for the first time at integration.

## Considered Options

- Keep the body free and leave it to review
- A fixed body, checked by the tool for its headings and lines, with a `parts` list in the manifests

## Decision Outcome

Chosen option: "a fixed body", because the pieces a consumer needs are the same in every contract, and a checker can see whether they are there without reading what they say.

- `## Parts` holds one `###` heading per part, with `Kind:` command, query, event or type, a fenced code block as the signature, and for a command or query `Pre:`, `Result:`, `Errors:` and an `Examples:` table.
- The notation of the signatures is named once; WIT is the default, any other is allowed.
- A type is defined once within the subtree of the unit that holds the contract.
- `## Fake` says what stands in for the contract in the tests of its consumers: a replay of the examples, a simplified behaviour with faults, or, for a logic provider, the real implementation.
- A need or capability may list `parts` under `contract`; a name that is no part is an error, because a need that names a part no contract has is an inconsistent map. Everything about the body is a warning.
- A long contract becomes a folder with one file per part.
- Every name of a constant in a code span of a hand-written document is a row of the nearest `docs/references/constants.md`, where such a table exists; its name pattern is declared in the table.

### Consequences

- Good: two people write the same tests from one part; a fake is defined once, where both sides see it.
- Good: a missing example or fake is found by the tool.
- Bad: the checker now reads headings and lines inside a reference, and the invariants say so.
- Bad: contracts grow; the folder form is needed sooner.
