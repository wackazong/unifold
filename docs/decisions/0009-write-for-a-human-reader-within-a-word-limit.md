---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Write for a human reader, one term for one thing, within a word limit

## Context and Problem Statement

The documents are written by agents and read by people and agents. Long files are skimmed by people and crowd an agent's context; a text that uses two words for one thing, or one word for two things, cannot be exact. A list of style rules that no tool checks is itself a burden. What does the standard say about how to write?

## Decision

- Write every document in language that a human reader understands easily. That is the one rule of style.
- One term for one thing: the terms of the standard, or of the unit's glossary, never a synonym. A unit *provides* and *needs*; the parent *connects*.
- A hand-written document has at most 1,500 words outside its front matter, and `## Why` at most 250; a word is a string between spaces that contains a letter or a digit. A document that grows beyond is split: a reference into a folder, the long why into `reasoning.md`, a procedure into a skill. One line per paragraph; nobody wraps prose by hand.
- The review checklist asks six questions that no checker can judge, and no more.

## Consequences

- Good: every document can be read in one sitting and loaded whole by an agent; the writing rules fit on a card.
- Bad: whether a text is clear is left to review.
