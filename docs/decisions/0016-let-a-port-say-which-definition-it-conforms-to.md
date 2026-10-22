---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Let a port say which definition it conforms to, and check the form of context items

## Context and Problem Statement

Bringing the example in line with the revised rules showed two gaps.

A sensor device and its emulator both provide a port that implements one protocol. The protocol is defined by a third unit and reaches both through a need. `contract` must be a path inside the unit, so neither port could point at its definition, and nothing recorded that the two alternatives implement the same thing.

The new form of `docs/context.md` (a linked heading, `Says`, `Here`) was defined in prose only. Three agents wrote it in slightly different ways.

## Considered Options

- Leave both to review
- Allow `contract` to point at a sibling's file
- A key `conforms-to` that names a need of the same unit, and a tool rule for the form of context items

## Decision Outcome

Chosen option: "`conforms-to` and a tool rule", because the port then points at its definition without naming a sibling, and the form of a context item is cheap to check.

- `conforms-to: <need>` on a provided port (`M9` checks that the need exists).
- `L9`: every item of `docs/context.md` has a link in its heading, a paragraph that starts with `Says` and one that starts with `Here`.
- The generated context file shows the contract of each need next to the contract of its provider, and for each provided port the contracts of the needs it serves.

### Consequences

- Good: substitutable alternatives are visible in the manifests.
- Good: the comparison that review rule `C13` asks for can be made from one generated page.
- Bad: one more manifest key.
- Bad: the tool does not yet check that alternatives of one need conform to the same definition.
