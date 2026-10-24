---
status: rejected
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Let a wired need take the contract of its provider

## Context and Problem Statement

[spec.md](../references/spec.md) section 3, rule 8, says that both sides of every connection name a contract, and the same one. Section 2 says that a path in `contract` lies in the unit, an ancestor or a descendant, never in a sibling. Together they mean that the document of a connection between two siblings lies in the references of their parent, or higher.

The example of section 2 cannot be used as it stands. It gives `billing` the capability `invoices` with `contract: openapi.yaml`, a file inside `billing`. A sibling that needs `invoices` cannot name that file:

```text
error M7 gateway/unifold.yaml:3: need 'invoices': 'contract' lies in the sibling unit 'billing': ../billing/openapi.yaml
```

Contracts that code is generated from, or that are generated from code, usually lie with the provider: an OpenAPI file, a protobuf file, a Rust trait, a C header. To connect such a capability, a project moves the file into the parent, which breaks the tooling that expects it beside the code, or copies it, and a copy drifts. A small project pays a document per connection even where the provider already has one: slugline has four contract files in its root for three children.

[0038](0038-make-a-contract-the-document-of-a-connection.md) gave two reasons. A connection is compared with code, and no code depends on a prose folder; [0047](0047-remove-the-comparison-with-code.md) removed that comparison. And a need that names a file of its provider names the provider. That reason still holds.

## Considered Options

- Keep rule 8 and the path rule
- Allow a `contract` path into a sibling
- Let a need that is connected leave out `contract`; the connection then has the contract of its provider, resolved through the wiring
- Let a capability list several contracts, and let a need name one of them

## Decision Outcome

Chosen option: "let a connected need leave out `contract`", because the contract stays with the code that defines it, and the need still does not name its provider: the unit that holds the wiring, which sees both children, resolves it.

- `contract` on a need is optional when the need is connected. A need without `contract` takes the contract of what provides for it: a capability of a sibling, or a need of the parent, which may in turn have taken one. The chain ends at a capability, or at a need that nothing in the project meets.
- A capability of a unit that a child implements (`public-api: gateway.public-api`) may also leave out `contract`, and takes the child's. A parent that only passes a capability through then keeps no second reference to it, as [wiring.md](../explanation/wiring.md) already asks.
- Every connection still has exactly one contract. Rule 8 becomes: "Every connection has a contract. Where both sides name one, they name the same document. A side that names none takes the contract of the side that provides." A need of the root that nothing in the project meets MUST name a contract, because nothing provides one.
- A need with alternatives and no `contract` requires that every alternative names the same document. Otherwise the need has no single contract, and `W11` reports it.
- The path rule does not change. A need never writes a path into its provider.
- `show`, `capability`, the JSON of [tool-json.md](../references/tool-json.md) and the context diagram print the contract that a need takes, marked as taken from the provider.
- The link rule of [documents.md](../references/documents.md) does not change. A file of the user cannot link to a contract that it takes from a sibling, because that link would name the sibling. `unifold show` prints the path.
- The option of several contracts per capability is not taken now. It changes what "the same contract" means and deserves a decision of its own, once a project needs it.

This amends 0038: "every side of a connection names a contract" no longer stands; "both sides name the same document" stands where both name one; "never a sibling" stands. The change needs a new version of the standard ([0049](0049-call-the-standard-0-2.md)): a checker for 0.2 reports a need without a contract.

### Consequences

- Good: the example of section 2 works, and a contract stays where the code generators expect it.
- Good: a connection no longer costs a document when the provider has one.
- Good: a need still does not name its provider.
- Bad: a need without `contract` states its expectation only in its summary and its `README.md`. Its terms are the provider's terms, which is weaker than a port that the user defines.
- Bad: when the provider changes its contract, the users that take it are not told by any finding. `unifold impact` lists them.
- Bad: a reader of the user's folder alone cannot open the contract without running `unifold show`.
