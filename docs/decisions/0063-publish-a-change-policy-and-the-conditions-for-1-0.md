---
status: rejected
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Publish a change policy and the conditions for 1.0

## Context and Problem Statement

The decisions of this repository are dated from 2026-10-06 to 2026-10-23. In that time 49 decisions were written and ten of them were superseded. Version 0.2 followed 0.1 within days ([0049](0049-call-the-standard-0-2.md)), and one person accepted every decision. The package says "Development Status :: 3 - Alpha". That is normal for a standard that is still being shaped, but a team that considers adopting it needs to know what a version promises: whether a manifest that is valid today stays valid, and how long the tool reads it with its meaning.

0049 answered this for one change: a manifest must not change its meaning while its version string stays the same, and the tool reads 0.1 with the meaning of 0.1. There is no general rule, and nothing says when the standard is stable.

## Considered Options

- Keep deciding case by case, as 0049 did
- A change policy now, and 1.0 on a date
- A change policy now, and 1.0 when stated conditions are met

## Decision Outcome

Chosen option: "a policy now, and 1.0 on conditions", because a date promises stability that nobody can measure, and conditions say what has to be true first.

### What breaks

A change is breaking when a manifest that was valid becomes invalid or changes its meaning, when a project that conformed gets a new error, when a generated file moves or disappears, or when a field of a published format changes its meaning: the manifest schema, the model of [0057](0057-publish-the-resolved-map-as-a-model-with-a-schema.md) or the observation format of [0050](0050-compare-the-wiring-with-observed-dependencies-that-the-project-supplies.md).

A change is not breaking when it adds an optional key, a warning or an info finding, turns an error into a warning, or accepts manifests that were rejected before. A change to the content of generated files is not breaking, but it is announced, because `check --fix` must run once after the update.

### Versions

- A version of the standard collects the decisions accepted since the previous one. A new version comes at least 30 days after the previous one, except to correct an error in the standard.
- Before 1.0, a version with a breaking change raises the minor number: 0.2, 0.3. The reference tool reads every version from 0.2 on with the meaning of that version.
- From 1.0, no 1.x version breaks. A 2.0 is announced at least 6 months ahead, and the tool reads 1.x for at least 12 months after 2.0.
- The schemas of every version stay served at their path, as [invariants.md](../explanation/invariants.md) already says.
- The package of the tool has a version of its own. It names the versions of the standard that it reads.

### Proposals

- A decision that changes the standard stays `proposed` for at least 14 days, with a public discussion linked from the decision, before a person accepts it.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) names the people who may accept. Before 1.0 there are at least two of them, and a change to [spec.md](../references/spec.md) needs the acceptance of two.

### Conditions for 1.0

All of these hold:

1. The trials of [0062](0062-try-the-standard-on-repositories-that-are-not-ours.md) are done and published, and either their threshold was met or the standard was changed in answer to them.
2. At least three projects that the maintainers do not run say that they follow unifold, and have done so for 60 days.
3. An implementation of the checker by someone else passes `tests/conformance.py`.
4. No breaking change for 90 days.
5. Every proposed decision up to this one is accepted or rejected.

### Where it is written

The policy and the conditions are a new reference, `docs/references/versions.md`. CONTRIBUTING.md links to it. The site shows the current version and the conditions that are still open.

### Consequences

- Good: an adopter knows what a version promises and how long it is read.
- Good: 1.0 means something that can be checked.
- Bad: the standard changes more slowly while it is still cheapest to change.
- Bad: conditions 2 and 3 depend on other people, and 1.0 may never come.
- Bad: more process for a project with one maintainer, and the second maintainer has to be found first.
