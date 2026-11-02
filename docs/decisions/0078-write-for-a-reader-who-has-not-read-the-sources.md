---
status: accepted
date: 2026-11-02
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Write for a reader who has not read the sources, and warn about a decision number without a link

## Context and Problem Statement

[0042](0042-take-the-writing-rules-of-ste-and-not-its-dictionary.md) took the sentence rules of ASD-STE100, Simplified Technical English. A sentence has at most 25 words and makes one statement, and a paragraph has at most six sentences. Each of these rules is an upper limit. It keeps a sentence short, but not complete.

A project that coding agents wrote with [maike](https://github.com/wackazong/maike) shows what that allows. Its 265 hand-written documents hold about 74,000 words, at 13 words per sentence. The serial-line example, which people find easy to read, has 15. Yet a person can hardly read the project's documents:

| Per 1,000 words | The project | serial-line |
|---|---|---|
| Two words joined by a slash, such as "bond/key" | 35 | 0.3 |
| A decision named by its bare number, such as "Accepted 0025 extends 0022" | 17 | 0.3 |

The documents also say 378 times that something is pending, unresolved, unanswered or blocked. They use noun phrases that no glossary defines, such as "native reservation participation". The `## Why` of the root `README.md` lists decisions in the order they were accepted.

The agents had the writing rules only through a link to the site, a cost that [0028](0028-reference-the-standard-instead-of-copying-it.md) names. The rules also name no reader, so nothing says for whom a sentence must be complete. What do the rules need, so that an agent writes for a person?

## Considered Options

- Lower limits next to the upper ones, such as a least number of words per sentence
- Rules that name the reader and the patterns that leave a sentence incomplete, in writing.md and in the skill, and no check
- The same rules, and a warning for the one pattern that a tool recognises without judging a sentence: a number that names a decision and is not part of a link

## Decision Outcome

Chosen option: "the rules and the one warning", because the project kept every limit, so only rules that name the patterns can change what an agent writes. A check also reaches the agent that read no rule.

This amends [0042](0042-take-the-writing-rules-of-ste-and-not-its-dictionary.md): its rules stay, and [writing.md](../references/writing.md) gains the section "Plain language". It follows [ISO 24495-1](https://www.iso.org/standard/78907.html), the international standard for plain language: a reader finds what they need, understands it and can use it.

- Every document is written for one reader: a person who knows the domain but has read neither the sources nor the files of other units.
- A sentence has a subject, a verb and the articles that English needs.
- Two words are joined by "and" or "or", never by a slash.
- An abbreviation is spelled out at its first use in a file, or it is a row of the glossary.
- At most three nouns stand in a row.
- A parenthesis holds an example, an abbreviation or a citation, never a second statement.
- A decision is cited for what it decides, and its number is a link. A decision that no link may reach, such as one of a child, is written with its unit: `transport/0002`.
- The state of the work is written once, where it belongs: in a proposed decision or in `status`.
- `## Why` gives reasons and lists no decisions. The review checklist asks whether the reader can follow each paragraph.

The skill states these rules as instructions in a section of its own, as it states the other rules that an agent applies, and links the chapter. The README template asks for reasons in whole sentences.

The reference tool gets a new warning, `T7`. It reports a four-digit number in a hand-written document that is the number of a decision of the unit or of an ancestor, unless the number is part of a link or follows the name of a unit and a slash. Code spans, fenced blocks and comments are not read. A link whose text is the number alone passes, because the sentence around it says what the decision decides. A number that names no decision passes, such as a port or a count.

This amends [invariants.md](../explanation/invariants.md) and section 5 of [spec.md](../references/spec.md): a checker also reads the numbers of decisions. It still judges no sentence. It compares a number with the names of decision files, as it compares a name in a code span with a constants table.

An accepted decision may now gain a link around the number of another decision, as it may gain a link to a file that moved. The link changes nothing that the decision says. A decision that amends another says "This amends" and links it.

### Consequences

- Good: a document says what it means where it says it. A reader opens a link to check a claim, not to understand it.
- Good: an agent finds the rules in the skill, and the check reports a bare number even when the agent read nothing.
- Good: the check reports no port, count or year, unless a decision has that number.
- Bad: plain text is longer than condensed text, often by half or more, and reaches the line limit sooner.
- Bad: slashes, fragments, undefined abbreviations and stacks of nouns are left to a reviewer, who needs time to read for them.
- Bad: the check misses a number that is glued to a word, such as "Accepted0018", and a decision of a child whose number the unit does not have.
- Bad: the plantwatch example changed in 15 files, and a project that cites decisions by number gets a list of warnings.
