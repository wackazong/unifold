---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Remove commands, settings, rules and keys that carry little

## Context and Problem Statement

The standard promises to be explainable in one minute and adoptable in five ([requirements](../explanation/requirements.md)). Since 0.1 it has grown to 13 commands, 50 rules and six keys of the root manifest. Every command has a JSON shape and test cases, every setting is a branch in the generator and the checker, and every rule needs a text, a test case and a fix. Some of them do what another one already does, some are read by nothing, and some judge prose by its digits, which the invariants then have to list as exceptions. Which of them can go without losing what the map gives?

## Considered Options

- Keep everything, and document it better
- Remove what repeats another command, what nothing reads, and the rules that guess from prose
- Remove more, such as the explorer or the states of a contract, in the same step

## Decision Outcome

Chosen option: "remove what repeats, what nothing reads, and the rules that guess from prose", because each removal below leaves a reader and a reviewer with the same information, and each takes away code, rules or tests. The larger cuts need decisions of their own.

**Commands.**

- `generate` goes. `check --fix` writes every generated file, the skill stubs included, and then checks. The marker of a generated file says `run unifold check --fix`.
- `skills sync` goes for the same reason. `skills` still lists the skills of the project.
- `cited-by FILE` becomes `impact FILE`. On a unit or a capability, `impact` lists what depends on it; on a file, also one that is deleted already, it lists the context items and links that cite the file.

**Settings of the root manifest.**

- `max-lines` goes. The line limit is 200 for every project, as [0006](0006-limit-every-markdown-file-to-200-lines.md) argues.
- `diagram-links` goes. Boxes in a generated diagram do not link; the tables below each diagram do, and the explorer makes every box clickable.
- `diagrams: all` goes. A unit without children gets no diagram; `unifold show` prints the final provider of each of its needs. `diagrams` keeps `parents`, the default, and `none`.

**Rules that read prose.**

- `T6` goes. `constants.md` stays a reference with a `Name | Value` table, and its front matter has no `name-pattern`. Whether a document names a value that the table does not hold is a review question.
- `T7` goes. Whether a decision is cited for what it decides, with a link, is a review question, as [0078](0078-write-for-a-reader-who-has-not-read-the-sources.md) asks.
- `T8` keeps its simple form: a reference has no link into a `docs/decisions/` folder. A decision number in the text of a reference is a review question.

**Keys of a manifest.**

- `kind` on a capability or a need goes, and with it `W4`. It had the name of a unit's `kind` and another meaning, and the contract already says what the connection carries. A project that wants it writes `x-kind`.
- `owner` goes. Nothing checked it or generated anything from it. A project that wants it writes `x-owner`.
- `kind` on a unit is optional everywhere. The rules of `logic` and `adapter` apply where a unit states the kind and say nothing where it does not.

0.4 is not published yet, so this changes 0.4 and does not raise the version. A map of 0.4 that uses `kind` on a capability or a need, `owner`, `max-lines` or `diagram-links` renames the key to `x-...` or deletes it; the fix of `M2` says so.

This amends [0005](0005-generate-diagrams-as-mermaid-with-link-tables.md) in the links of a box and in `diagrams: all`, [0066](0066-three-well-known-kinds-with-rules.md) in where a unit must state a kind, [0078](0078-write-for-a-reader-who-has-not-read-the-sources.md) in the warning about a decision number, and [0080](0080-describe-the-current-state-and-name-no-decision-in-a-reference.md) in what the warning about a reference reads.

### Consequences

- Good: two commands and one subcommand fewer to learn, document and test; one command writes every generated file.
- Good: three settings fewer, so every project has the same line limit and the same diagrams.
- Good: no finding depends on a digit or a name pattern in a sentence. The checker reads links, headings, front matter, length and the tables of a contract.
- Good: `kind` has one meaning, and a first manifest of a unit with children needs one key fewer.
- Bad: a reference that names a decision by its number, and a document that names a value the constants table lacks, are found only in review.
- Bad: a leaf unit has no generated context diagram; a reader runs `unifold show` or opens the explorer.
- Bad: a project that relied on `owner` or the kind of a capability moves it to an `x-` key and loses it from `show` and the model.
