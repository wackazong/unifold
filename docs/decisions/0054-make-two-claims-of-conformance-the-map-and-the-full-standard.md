---
status: rejected
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Make two claims of conformance: the map, and the full standard

## Context and Problem Statement

The standard has two parts. [spec.md](../references/spec.md) is normative for manifests, wiring and generated files: short, and every rule is checked. [documents.md](../references/documents.md) and [writing.md](../references/writing.md) are normative for the documents of a unit: a `README.md` in every unit with fixed sections, the Diátaxis folders, the arc42 file names, the direction of links, context items with stamps, and line limits. Section 4 of the spec ties the second part to the first, so a project conforms to both or to neither.

The second part is where an existing repository fails first. A repository of 300 packages needs 300 `README.md` files with a `## Why` before its check is green (`S3`). Its READMEs link to sibling packages (`L2`). Its `docs/` folder holds a site built with mkdocs or Docusaurus, which `S12` reports. Such a project wants the map now and the documents later, or never, and today it cannot say that it follows unifold at all.

[0040](0040-one-standard-without-levels.md) merged the levels `core` and `full`, because in use the question "which level is this unit at" never had an interesting answer. That use was the two examples of this repository, both written for the standard. The question has an answer as soon as the repository existed before the standard.

## Considered Options

- Keep one claim (0040)
- Levels per subtree again ([0023](0023-set-the-level-per-subtree-and-keep-core-free-of-prose-rules.md))
- Two claims for the whole project, chosen once in the root: the map, or the full standard
- Keep one claim, and make every rule about documents a warning

## Decision Outcome

Chosen option: "two claims, chosen in the root", because the line between the checkable core and the document conventions already exists in the chapters, and a project should be able to stand on the first side of it.

- The root key `conformance` is `full` (the default) or `map`.
- With `map`, `check` applies the rules of sections 2, 3, 5 and 6 of the spec: `S1`, the rules `M` and `W`, `G1`, and the rules of [0050](0050-compare-the-wiring-with-observed-dependencies-that-the-project-supplies.md). It does not apply `S3`, `S7`, `S9`, `S12`, or the rules `L` and `T`. A unit needs no `README.md`.
- The generated files are the same in both. Where a unit has no `README.md`, its `AGENTS.md` says so and points at `unifold show`.
- The claims are "This repository follows unifold 0.3 (map)" and "This repository follows unifold 0.3". Section 8 of the spec says both. Section 4 says that the document conventions hold with `conformance: full`.
- There is no level per subtree, and no level column in the rule table. [rules.md](../references/rules.md) says once which rules `map` leaves out.
- `init` writes no `conformance` key. The skill `unifold-convert` asks the person which claim the project makes, and recommends `map` when the repository has its own documentation.

This amends 0040: "every unit has a `README.md`" holds with `conformance: full` only; the key `level` stays removed, and the rule tables keep one column.

### Consequences

- Good: an existing repository can adopt the map and claim it within a day. The documents become a second step that it may take later.
- Good: the claim says which half of the standard a project follows, so a reader knows what to expect in its folders.
- Bad: two claims to explain, in a standard that wants to be explained in one minute.
- Bad: a project with `map` has no front page per unit, which 0040 called the reason to open a folder. Agents fall back to `unifold show`.
- Bad: a project may stay at `map` for good, so the document conventions get fewer users and fewer trials.
