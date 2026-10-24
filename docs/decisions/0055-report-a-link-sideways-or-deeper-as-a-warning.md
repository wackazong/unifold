---
status: accepted
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Report a link sideways or deeper as a warning

## Context and Problem Statement

Rule `L2` is an error, and it reports two different faults:

1. A link that breaks outside the clone: an absolute path, or a relative link that leaves the project.
2. A link in a direction that [documents.md](../references/documents.md) forbids: sideways to a sibling, deeper than a direct child, into the `docs/` of a child, or upward from a file other than `docs/explanation/context.md`.

The first fault breaks a reader's link. The second breaks a design rule: it keeps a child understandable alone ([0003](0003-allow-upward-links-only-in-context.md)), and the link still works. Existing READMEs link to sibling packages as a matter of course ("see `../core`"). Converting such a repository gives a list of errors that are design advice. [0031](0031-reduce-the-rule-set-and-turn-review-rules-into-a-checklist.md) chose its rule set so that advice does not look like law.

## Considered Options

- Keep `L2` as one error
- Make `L2` a warning as a whole
- Keep `L2` as an error for links that break, and report the direction of a link with a new rule as a warning

## Decision Outcome

Chosen option: "split the rule", because the severity should say what a finding is: a link that breaks is an error, and a link that goes the wrong way is a design question for a person.

- `L2`, error: a relative link stays inside the project, and no link is an absolute path.
- `L11`, warn: a link follows the direction rules of documents.md. It does not go sideways, deeper than a direct child or into the `docs/` of a child, and it goes upward only from `docs/explanation/context.md`. A link to a file that the unit's manifest names as `contract` or `verified-by` stays allowed.
- `L11` keeps the fix text of `L2`: what the unit wants from a sibling is a need in its manifest, and what it takes from above is an item in `context.md`.
- [spec.md](../references/spec.md) section 5 lists the link that breaks as an error and the link in a forbidden direction as a warning.
- A project that wants the old severity runs `check --strict`.
- With `conformance: map` ([0054](0054-make-two-claims-of-conformance-the-map-and-the-full-standard.md)), neither rule applies.
- The id `L11` is new, because ids are never reused.

### Consequences

- Good: a conversion gives errors only for links that break. The direction findings become a list of work, not a red build.
- Good: the severity says what the finding is.
- Bad: projects that do not run `--strict` keep links sideways, and a child is less often understandable alone.
- Bad: `--strict` also fails on every other warning. There is no way to raise one rule alone.
- Bad: one more rule id.
