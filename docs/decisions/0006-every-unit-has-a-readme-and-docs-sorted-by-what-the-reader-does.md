---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Every unit has a README with a why, and docs sorted by what the reader does

## Context and Problem Statement

What a unit provides and needs is in the manifest and the contracts; what cannot be derived is why it exists and why it is cut this way. Readers come to a folder to learn, to do a task, to look something up or to understand. Where does each kind of written knowledge go, so that a person and an agent find it without a search?

## Decision

- Every unit has a `README.md`: a `#` title, one paragraph that says what the unit is for and for whom, and `## Why`, at most 250 words: what the unit hides because it is hard to get right or likely to change, what it leaves to others, the forces, the main trade-off, what must stay true. Any further section is the unit's choice. A README does not describe how the unit works inside and does not list its connections.
- Everything else lives in `docs/`, sorted by what the reader is doing, after Diátaxis: `tutorials/` (learn), `skills/` (do, in the Agent Skills format), `references/` (look up: the contracts, `glossary.md`, `constants.md`), `explanation/` (understand) and `decisions/`.
- The explanation files have fixed names and exist only when they have content: `context.md`, `requirements.md`, `reasoning.md`, `invariants.md`, `runtime.md`, `deployment.md`, `risks.md`. Their form is free.
- A reference states facts and gives no reasons; where a decision settled a fact, it may link the decision. Every document but a decision describes the unit as it is now; the state of the work is only `status` in the manifest and the proposed decisions.

## Consequences

- Good: the same files in the same places in every unit, for people and agents alike; nothing is written twice for a second audience.
- Good: the checker reads the title, the paragraph, the `## Why` and the placeholders of a README.
- Bad: a project with an existing wiki or docs site moves its pages into the tree, or keeps two places.
