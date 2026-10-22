---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Take the writing rules of ASD-STE100 and not its dictionary

## Context and Problem Statement

ASD-STE100, Simplified Technical English, is a controlled language for maintenance documents: about 50 writing rules and a dictionary of about 900 approved words. Each word has one meaning. The question was whether to rewrite the whole repository in it.

The documents here are of two kinds. The skills and the tutorial are procedures, which is what STE was made for. The spec, the reference chapters, the explanation files and the decisions argue and define, which STE was not made for. Its dictionary forbids "should" and "may", which [BCP 14](https://www.rfc-editor.org/info/bcp14) gives the spec, and "provide", "need" and "capability", which are the terms of the standard. No checker can be shipped: the tools are commercial and the dictionary is copyrighted. [0031](0031-reduce-the-rule-set-and-turn-review-rules-into-a-checklist.md) keeps prose style out of the tool, and an accepted decision is not edited.

## Considered Options

- Rewrite every hand-written file in ASD-STE100, with the terms of the standard declared as technical names
- Take the sentence, paragraph and instruction rules of STE without its dictionary, and add a prose lint to this repository
- Take the same rules without a lint; reviewers check them, like the rest of the Markdown style

## Decision Outcome

Chosen option: "the rules without the dictionary and without a lint", because the rules are what makes a procedure easy to follow. The dictionary is what makes an argument hard to write, and a lint would be a style rule that the standard itself refuses to carry.

- [writing.md](../references/writing.md) gains four rules. A sentence has at most 25 words, 20 in a step. A paragraph has at most six sentences. A step is an instruction. A defined term has no synonym.
- The two skills and the tutorial follow the rules. The other files follow them when they are next edited.

### Consequences

- Good: a step says one thing, and an agent or a reader can act on it without parsing a clause.
- Good: the templates stay plain English, so adopters need to learn nothing.
- Bad: nothing enforces the caps. A reviewer counts, or nobody does.
- Bad: long sentences in the explanation files remain until someone edits them.
