---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# One standard, without levels

## Context and Problem Statement

[0017](0017-define-a-core-that-can-be-adopted-alone.md) split the standard into the levels `core` and `full`, and
[0023](0023-set-the-level-per-subtree-and-keep-core-free-of-prose-rules.md)
let a manifest set the level for its subtree. Every page then had to say twice what holds: a table of rules carried a level column, the tool kept two code paths for `AGENTS.md`, the examples needed a column for their level, and a reader of the README had to learn the split before the first map. In use, the question "which level is this unit at" never had an interesting answer: a unit either had a `README.md` worth reading or it had none yet.

## Considered Options

- Keep two levels, set per subtree
- Keep two levels, set once in the root
- One standard: every unit has a manifest and a `README.md`, and the document conventions hold for whatever a unit writes

## Decision Outcome

Chosen option: "one standard", because the level was a second thing to explain for a benefit that the rules already give: a unit whose `docs/` is empty is checked for nothing but its `README.md`, so a map-only project costs one short file per unit more than before.

- The key `level` leaves the manifest; a manifest that still has it is reported as an unknown key.
- Every unit has a `README.md` (`S3`). `AGENTS.md` is generated for every unit; the root's carries the unifold block. The block is no longer inserted into a hand-written root `AGENTS.md`.
- The rule tables lose their level column. The conformance claim is "follows unifold 0.1", without a suffix.
- Decision 0023 is superseded; 0017 stays superseded.

### Consequences

- Good: one thing to learn, one code path, one claim.
- Good: a package `README.md` that a registry publishes is now part of the map; its links are checked.
- Bad: a repository that only wants the map has to write a short `README.md` for every unit before `check` is green.
- Bad: a published `README.md` with links to siblings is reported until the links move into needs and context items.
