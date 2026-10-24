---
status: rejected
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Make the repository of the standard a project, with the reference tool as its unit

## Context and Problem Statement

[0039](0039-the-repository-of-the-standard-is-not-a-unit.md) deleted the root manifest of this repository: what the repository is, is the specification, and a specification is never a unit ([0038](0038-make-a-contract-the-document-of-a-connection.md)). The repository also holds code that is built, run and deployed: the reference tool of about 3 600 lines, which is published on PyPI and run by a GitHub Action; a conformance suite of about 1 200 lines; and `site/build.py`, which builds and publishes `unifold.md`. A unit "SHOULD hold code that is built, run or deployed", and this repository does.

The standard has been tried only on examples written for it, and the [risks](../explanation/risks.md) name the lack of evidence from use as the first risk. A real Python project that is changed every day is the cheapest trial there is. It also has two cases that the examples avoid: a tool inside `docs/skills/` of the root, and a child, `site/`, that reads the documents of its parent, a direction that [wiring.md](../explanation/wiring.md) says is not modelled.

## Considered Options

- Keep 0039
- A root manifest: the repository is the unit of the reference tool, and the chapters of the standard are the contracts of its capabilities; `site/` is a child
- A nested project for the tool alone, below a repository that stays outside the map

## Decision Outcome

Chosen option: "a root manifest, with the chapters as contracts", because it keeps 0038 true, since the specification is still not a unit but the contract of one, and because the repository then tests the standard every day.

```yaml
# unifold.yaml
unifold: "0.3"
name: unifold
summary: The unifold standard, its reference tool and its skills
capabilities:
  unifold-command:
    kind: cli
    summary: Checks, generates, queries and exports the map of a project
    contract: docs/references/tool.md
    verified-by: tests/conformance.py
  manifest-schema:
    kind: file
    summary: The JSON Schema of unifold.yaml
    contract: docs/references/spec.md
  skills:
    kind: file
    summary: The skills unifold and unifold-convert, installed into other projects
    contract: docs/references/agents.md
  website:
    kind: ui
    summary: The site unifold.md
    contract: site/README.md
wiring:
  website: site.website
```

- The sketch is a starting point. The skill `unifold-convert` writes the real manifests, and a person reviews them.
- `site/` becomes a unit with the capability `website`. What it reads from the root is the first open question that the trial answers: a need of `site` met by a capability of the parent, which the standard does not allow today, or no need at all, because the chapters are input files and not an interface.
- `examples/` holds nested projects (section 7 of [spec.md](../references/spec.md)). They stay outside this project and are checked on their own.
- `AGENTS.md` and `docs/decisions/index.md` of the root become generated. The hand-written content of `AGENTS.md` moves to `README.md` and `docs/` first.
- CI runs `unifold check` on this repository beside `tests/conformance.py`.
- The documents of this repository follow the conventions because the check says so, not by choice.
- Goal 5 of the [requirements](../explanation/requirements.md) becomes: every rule is tried on the examples and on this repository before a project has to follow it.
- A change to the standard is first written so that this repository passes it. A change that would need an exception for this repository is a reason to change the proposal, not to add the exception.

This supersedes 0039.

### Consequences

- Good: the standard is used every day on a real repository by the people who change it.
- Good: friction shows here first: the generated `AGENTS.md`, the line limits, the link rules, the stamps.
- Good: the case of a child that reads files of its parent gets an answer from use, not from theory.
- Bad: every change to the standard also has to be applied to this repository before the check is green again.
- Bad: the standard may be bent to fit its own repository. The trials of [0062](0062-try-the-standard-on-repositories-that-are-not-ours.md) are the counterweight.
