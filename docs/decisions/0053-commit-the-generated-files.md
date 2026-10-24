---
status: accepted
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Commit the generated files

## Context and Problem Statement

[spec.md](../references/spec.md) contradicted itself. Section 6 said that generated files SHOULD be committed. Section 5 made a missing generated file an error. A project that does not commit them fails every check in a fresh clone, so in effect the SHOULD was a MUST. And a project that ignored `docs/diagrams/` in `.gitignore` passed the check on the machine that had generated them, while every clone failed.

Committing has a cost that grows with the project. One changed summary of a capability changes the component diagram of the parent, the context diagram of every sibling that is connected to it, and the architecture diagram of the ancestors up to three levels above. Two branches that both touch the map conflict in files that nobody wrote. The 22 units of plantwatch carry 1 487 lines of diagrams.

Committing also has value. A code host shows Mermaid in a review, and a reader of a clone sees the diagrams without running anything ([0005](0005-generate-diagrams-as-mermaid-with-link-tables.md)). `AGENTS.md` is read by agents in a fresh clone before any command runs.

## Considered Options

- Keep committing, and change the SHOULD to a MUST
- A root key with which a project builds the diagrams and decision indexes instead of committing them; `AGENTS.md` is always committed
- Write no generated file into the tree; `unifold site` alone shows the diagrams

## Decision Outcome

Chosen option: "keep committing, and make it a MUST", because the map is read where the code is read: in a clone, on the code host and in a review, without a build step, and one mode is simpler to explain and to test than two.

- Section 6 says: generated files MUST be committed, and kept current with every change to what they show.
- A checker cannot see a commit. It sees what is present, current and ignored. Section 5 adds a generated file that version control ignores to the errors, and `G1` reports it: "generated file is ignored by git; generated files are committed".
- A conflict in a generated file is resolved by running `unifold generate` after the conflicts in the manifests are resolved, never by hand.
- [documents.md](../references/documents.md) keeps its advice to mark generated files for the code host, for example with `linguist-generated`, so that a review folds them.

### Consequences

- Good: the spec says what the check enforces.
- Good: a clone, a code host and a review show the diagrams without running anything.
- Good: a project that ignores its diagrams learns it on the first check, not in the first clone.
- Bad: a change to the wiring touches generated files in several units, and branches that both touch the map conflict in them.
- Bad: the repository carries the diagrams, 1 487 lines in plantwatch.
