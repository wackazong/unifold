---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Reduce the rule set and turn review rules into a checklist

## Context and Problem Statement

The draft had 49 tool rules and 15 numbered review rules, in three lists that did not agree, spread over 15 chapters of about 2 250 lines. Reviewers read it as a 64-rule audit. Several rules gave false alarms on ordinary READMEs, several checked Markdown style that other linters cover, and normative sentences without a rule ID stood beside the rules. The line limit of [0006](0006-limit-every-markdown-file-to-200-lines.md) was an error even for the front page of an existing project.

## Considered Options

- Keep the rules and improve the messages
- Cut to about ten rules and drop the document conventions
- One normative page for level `core`; about 25 tool rules listed in one table; review rules become a checklist of ten questions in the guide; the line limit stays as a warning at level `full`

## Decision Outcome

Chosen option: "one page, about 25 rules, a checklist", because the part that a tool can check should be short enough to read, and advice should not look like law.

- `spec.md` holds everything normative for level `core` in at most 200 lines. The guide chapters explain and do not add rules for `core`.
- Severities are the words `error`, `warn` and `info`.
- Prose does not cite rule IDs. The table of rules is the one place.
- The line limit is a warning, for hand-written files at level `full`, and `max-lines` in the root manifest changes it.
- Rules on README titles, names in code font, heading order, and the copy of the standard are removed.

This amends 0006 and [0014](0014-build-the-design-principles-into-the-rules.md): the design principles remain as a guide chapter and are no longer tied to rule IDs.

### Consequences

- Good: the standard can be read in a few minutes.
- Bad: mentions of siblings and ancestors in prose are no longer found by the tool at all; only links are.
- Bad: a checklist without numbers cannot be cited in a review finding.
- Bad: projects that want the removed style rules need another linter.
