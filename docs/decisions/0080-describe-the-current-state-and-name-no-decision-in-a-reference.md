---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Describe the current state in every document but a decision, and name no decision in a reference

## Context and Problem Statement

[0078](0078-write-for-a-reader-who-has-not-read-the-sources.md) and [0079](0079-describe-what-a-unit-does-not-the-state-of-the-work.md) write every document for a reader who has not read the sources, and keep the state of the work out of the prose. One habit stayed: every document cites a decision for what it decides, a contract included.

A project that coding agents build with [maike](https://github.com/wackazong/maike) shows where that habit leads. Its sources hold about 10,500 words. After five build steps, its `docs/references/` holds 155 files with about 95,000 words. These files mention a decision 1,978 times, about 21 times per 1,000 words, and 135 of the 155 files mention one. T7 reports 1,193 of these mentions. The others are links, or numbers glued to a word, such as "Accepted0090 binds".

The mentions come from the way the contracts change. An accepted decision is not edited, so every change is a new decision. The contract keeps its text and gains a sentence about the new decision, such as "0118 adds the completion event". Another sentence says what is still open: "native realization remains gated". So a contract grows with every decision and reads as its own history. To learn what holds now, the reader opens each decision.

Beside the contracts, the folder holds notes about the work, such as `skeleton-readiness.md`, `reconciliation.md` and `board-test-coverage.md`. Nothing says that a reference holds only facts about the product.

What may a document other than a decision say about the past and the future, and what may a reference hold?

## Considered Options

- Keep the rules of 0078: a reference cites a decision for what it decides, with a link
- Every document but a decision describes the current state, and a reference names no decision, with no check
- The same rules, and a warning `T8` for every decision that a reference names

## Decision Outcome

Chosen option: "the same rules, and a warning", because a reference has no use for a decision that a check must allow. T7 lets a linked number pass, because an explanation cites a decision for its reasons. T8 need not, so it also reports a link and a number glued to a word.

[documents.md](../references/documents.md), [writing.md](../references/writing.md), [contracts.md](../references/contracts.md) and the skill say:

- Every document but a decision describes the unit as it is now: what it does, what it needs, how it works and why. The history is in the decisions and in version control. Plans and the progress of the work belong to the people and the process that do the work. Inside the documents, the state of the work is only `status` and the proposed decisions, as 0079 says.
- A change rewrites every document it touches to the new state. The document does not say what changed, when, or which decision changed it.
- A reference is only a reference: facts as they are now, complete, with examples. Most references are contracts or parts of a contract. Beside them, a unit keeps `glossary.md`, `constants.md` and the few references that several contracts or the code of the unit share, such as a convention. A note about a step of the work, a review or a test run is not a reference. Neither is a description of how a unit works inside, which is an explanation of that unit.
- A reference names no decision, also not in the `Sources:` line of a contract or in the `Source` column of the constants.
- A decision links the documents it changes. `unifold cited-by FILE` lists these links, so the reader of a contract still finds its reasons.

This amends [0078](0078-write-for-a-reader-who-has-not-read-the-sources.md): a document cites a decision for what it decides only outside the references, and T7 reads no reference. It also amends [0079](0079-describe-what-a-unit-does-not-the-state-of-the-work.md): the history, like the state of the work, stays out of every document but a decision.

The reference tool gets the warning `T8`. It reads the Markdown files in `docs/references/`. It reports a link into a `docs/decisions/` folder, a four-digit number of a decision of the unit or of an ancestor, also glued to a word, and a number of a decision of another unit after the unit's name and a slash, as in `transport/0002`. It does not read numbers in code spans, fenced blocks and comments. A number after `0x` or `U+` is a value and passes.

### Consequences

- Good: a contract says what holds now. A change rewrites it instead of adding a sentence, so it does not grow with every decision.
- Good: a superseded decision leaves no stale citation in a reference.
- Good: the check finds the glued numbers that T7 misses, in the files where they cost the reader most.
- Bad: the reader of a reference sees no reason beside a fact. They find it with `unifold cited-by` or in the index of the decisions.
- Bad: nothing checks that a decision links the documents it changes, or that a document leaves out its history. A reviewer reads for both.
- Bad: a value outside a code span that equals the number of a decision is reported. Such a value belongs in a code span or in `constants.md`.
- Bad: plantwatch and serial-line change in 28 references, and 36 context items that cite them get a new stamp. A project that cites decisions in its references gets a warning for each citation.
