---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Decisions use MADR; agents propose, people accept

## Context and Problem Statement

Reasons that are not written down are lost, and the same mistake is made twice. Coding agents write much of the text today, but they must not decide for a project. How are decisions recorded, and who may make them?

## Decision

- A decision is a file `docs/decisions/NNNN-short-title.md` in the lowest unit whose insides it fully covers, in the MADR format, with a four-digit number unique in the unit, a `date` and a `status`: `proposed`, `accepted`, `rejected`, `deprecated`, `superseded by NNNN` or `derived`.
- Agents propose; only a person who may decide for the unit sets `accepted` and names the `decision-makers`. A decision that a source makes, not a person, is `derived`: it names the passage in `derived-from` and restates it under `## Source says`, and it binds until a person accepts or supersedes it.
- Only accepted and derived decisions bind. An accepted decision is not edited, except for its status and for links to files that moved; to change it, write a new one and set the old one to `superseded by NNNN`.
- The change that a decision makes rewrites the documents it touches to the new state, in the same change. A unit below that depends on a decision takes it into its `context.md`.
- Every change to the standard itself is such a decision in this repository.

## Consequences

- Good: a reader finds the reason behind every fact of the map, and knows which reasons are in force.
- Good: no agent can change a decision of record without a person.
- Bad: replacing one point of a large decision means a new decision that states again what stays.
