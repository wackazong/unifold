---
status: accepted
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Let a README point at its contracts

## Context and Problem Statement

A need or capability can be described in four places: its summary in the manifest, its `###` section in `README.md`, its contract, and the `Says` lines of the units that cite it. [documents.md](../references/documents.md) says two things that pull apart: "A fact has one home; other files link to it", and "A reader MUST be able to use the unit, or to provide what it needs, after reading this file alone". The second rule makes a `README.md` restate its contracts.

The README of `alerts` in plantwatch does so. It states that an alert is visible within 30 seconds, as `cloud/docs/references/alerts-api.md` does. It states the limits of the push service, 60 and 120 characters, five data fields, a collapse identifier and a time to live of 24 hours, as `docs/references/push-service.md` of the root does. Nothing finds out when the two drift apart, and every README grows with each contract it repeats.

## Considered Options

- Keep both rules as they are
- Relax the README rule: the unit can be used after reading `README.md` and the contracts that its manifest names
- Keep the README rule, and let any section that restates a source carry a stamp ([0026](0026-stamp-every-restatement-with-a-hash-of-its-source.md))

## Decision Outcome

Chosen option: "relax the README rule", because it removes the restatement instead of watching it. A stamp would keep the README as long as it is and add a line to refresh with every change of a contract.

- documents.md says: "A reader MUST be able to use the unit, or to provide what it needs, after reading `README.md` and the contracts that its manifest names." The README says what the unit is for and why; the contract says how to use it.
- A `###` section for a capability or need says only what neither its summary nor its contract says: what this unit adds beyond the contract, its own limits, and what it does without an optional need. Where the summary and the contract say everything, there is no section, and where no section is left, there is no `## Capabilities` or `## Needs`.
- A section does not end with a link to the contract. The manifest names it, and `unifold show` prints it. A section may link to the contract where a sentence refers to a part of it.
- Stamps stay limited to the items of `context.md`.

### Consequences

- Good: a fact of a connection has one home, its contract. A README cannot contradict a contract that it does not restate.
- Good: READMEs get shorter. Most capabilities and needs of the examples need no section.
- Bad: `README.md` alone is no longer enough to use a unit. A reader of a copied folder also needs the contracts, which may lie in the parent.
- Bad: a reader on a code host sees no link from the README to a contract. The manifest beside it names the file.
