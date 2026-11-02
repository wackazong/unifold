---
status: accepted
date: 2026-11-02
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Describe what a unit does and needs, not the state of the work

## Context and Problem Statement

[0078](0078-write-for-a-reader-who-has-not-read-the-sources.md) writes the state of the work once, in a proposed decision or in `status`. Its rule names three words that a sentence about the product does not carry: "pending", "unresolved" and "not yet implemented". A document can still hold a roadmap in other words. The plantwatch example has a section "What version 1 leaves out", firmware that is "updated by hand in version 1", and says of two placeholders that "final values replace them before version 1.0 is released".

Such a sentence is true only until the work moves on, and nothing reports it when it turns false. It also tells the reader what someone intends, not what the unit does. What may a document say about the work that builds a unit?

## Considered Options

- Keep the rule of 0078 and its three words
- A rule that a document describes what a unit does and needs, never the state of its implementation or a roadmap, and no check
- The same rule, and a warning for words such as "planned", "for now" or "version 2.0"

## Decision Outcome

Chosen option: "the rule and no check", because the words of a roadmap are also the words of facts. A reading schema has records "of version 1.0", a contract has the error `failed for now`, and a central "retries later". A list of words would report each of them.

This amends [0078](0078-write-for-a-reader-who-has-not-read-the-sources.md): its rule on the state of the work is widened. The section "Plain language" of [writing.md](../references/writing.md) and the skill say:

- A document describes what a unit does and what it needs. It does not say how far the implementation is, or in which version or phase something comes.
- A sentence about the product does not carry "planned", "pending", "unresolved", "not yet implemented", "for now", "in version 2.0" or "the alpha version".
- The state of the work is written once, outside the prose: an open question is a proposed decision, and a unit without code has `status: planned`.
- A version of a format or a contract, such as "records of version 1.0 have 19 bytes", states a fact and stays.

Item 9 of the review checklist asks whether `status` is the only place that says how far the work is.

### Consequences

- Good: a document stays true while the code is written, and the reader learns what a unit does, not what someone intends.
- Good: the state of the work stays where the tools show it: `show` and `capability` mark planned units and proposed decisions.
- Bad: a reviewer finds a roadmap only by reading for it. No check reports it.
- Bad: plantwatch calls its product "version 1" in several files, and its root `README.md` says that no product code exists. These passages break the rule until they are rewritten.
