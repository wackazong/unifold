---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Let an accepted decision gain links to the documents it changes

## Context and Problem Statement

[0080](0080-describe-the-current-state-and-name-no-decision-in-a-reference.md) turns the direction of a link around. A reference no longer links the decision that settled one of its facts; the decision links the reference instead, and `unifold cited-by` finds the decision from the reference.

A decision that was accepted before often lacks that link, because the reference linked it. [0046](0046-let-a-decision-amend-part-of-an-accepted-one.md) allows only two edits of an accepted decision: its status, and a link to a file that moved. [0078](0078-write-for-a-reader-who-has-not-read-the-sources.md) adds a link around the number of another decision. None of these edits adds a link to a document that the decision changes.

In plantwatch, a reference cited a decision in 35 pairs of a reference and a decision. In 11 of these pairs, the decision also linked the reference. When the references dropped the citations, the other 24 pairs lost the only link between reason and fact. May an accepted decision gain such a link?

## Considered Options

- Keep the edits of 0046 and 0078, and leave the old decisions without the link
- Let an accepted decision gain a link to a document that it changes
- Let an accepted decision gain any text that does not change what it decides

## Decision Outcome

Chosen option: "a link to a document that it changes", because a link changes nothing that the decision decides, and it restores the way from a fact to its reason. Any other text would need a judgement about whether it changes the decision.

This amends [0046](0046-let-a-decision-amend-part-of-an-accepted-one.md):

- An accepted decision may gain a link to a document that it changes. The link goes around words of the decision that name the document, or into a sentence under `## More Information`, such as "The contract `sql-db` states the result".
- A decision links a document only where a link may go, as [documents.md](../references/documents.md) says. A decision of a unit does not link into the documents of a unit below it. That unit takes the decision into its `docs/explanation/context.md`, and its documents state the result.

[writing.md](../references/writing.md) and the skill state both rules. In plantwatch, 20 decisions gain 22 links. Two decisions of the root shaped references of `device`, and they reach `device` through its `context.md`.

### Consequences

- Good: in the examples, `unifold cited-by` finds the reason for each fact from which a reference dropped a citation.
- Good: a project can repair its old decisions after it removes the citations from its references.
- Bad: a context item that cites a whole decision file gets a stale stamp when the decision gains a link. In plantwatch, 29 items had to be stamped again.
- Bad: nothing checks that an edit of an accepted decision adds only links. A reviewer reads the diff.
