---
status: rejected
date: 2026-10-23
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Let a decision amend part of an accepted one

## Context and Problem Statement

[writing.md](../references/writing.md) allowed one way to change an accepted decision: write a new one and set the old one to `superseded by NNNN`. The log of this repository does something else. Seven decisions change part of an older one and leave it accepted, because most of it still holds: [0025](0025-compare-with-code-by-default-and-draft-manifests-from-build-files.md), [0027](0027-ship-one-skill-and-generate-stubs-where-agents-look.md), [0029](0029-generate-diagrams-only-for-units-with-children.md), [0031](0031-reduce-the-rule-set-and-turn-review-rules-into-a-checklist.md), [0034](0034-convert-a-repository-with-a-skill-instead-of-drafting-manifests.md), [0036](0036-generate-agents-md-and-keep-knowledge-in-readme-and-docs.md) and [0038](0038-make-a-contract-the-document-of-a-connection.md). A review before the alpha found that the titles of five accepted decisions are no longer true as a whole, for example "Ship one skill" while two are shipped. Links in accepted decisions were also corrected when the chapters moved ([0045](0045-keep-the-reference-chapters-directly-in-docs-references.md)), which the rule did not allow either.

## Considered Options

- Set every amended decision to `superseded by NNNN`
- Rewrite the amended decisions so that they are true again
- Allow a new decision to amend part of an accepted one, and allow links to be corrected

## Decision Outcome

Chosen option: "allow amendment", because it is what the log already does, and because the other options either lose the parts that still bind or make an accepted text change under the people who accepted it.

- A new decision that changes part of an accepted one says "This amends NNNN:" and what changes. The rest of the old decision stays in force, and its status stays `accepted`.
- A decision that is replaced as a whole is set to `superseded by NNNN`.
- An accepted decision is not edited, except for its status and for links to files that moved.

### Consequences

- Good: the rule describes the log as it is, and no decision that still binds is marked as replaced.
- Good: the people who accepted a decision can still read what they accepted.
- Bad: the generated index does not show amendments. A reader of an amended decision finds the change only from the newer decision.
- Bad: an accepted title can be partly false. The newer decision is the one to read.
