---
status: accepted
date: 2026-10-23
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Remove the comparison with code

## Context and Problem Statement

`check` compared the wiring with dependencies that it extracted from build files and imports, and with a list given with `--deps` ([0019](0019-compare-the-wiring-with-dependencies-observed-in-code.md), [0025](0025-compare-with-code-by-default-and-draft-manifests-from-build-files.md)). Cargo and npm gave a dependency per package, Go and Python per folder of imports. A unit is a folder of any shape, so the comparison covered only the units that happen to be packages or import folders. A module inside a crate, a folder of Java, C or Swift, a service called over the network got no check unless somebody wrote a list. The guarantee read as general and was partial, and the extractors were about 970 lines of code for four ecosystems in a tool that is otherwise free of any language.

## Considered Options

- Keep the extractors and report which units they cover
- Compare only with a list that the project supplies
- Read the imports of every file in more languages
- Remove the comparison

## Decision Outcome

Chosen option: "remove the comparison", because a check that holds for every unit alike is worth more than one that holds for some and is silent about the rest.

- The checker reads `unifold.yaml` files and Markdown documents, never code. Rules `D1` to `D3`, the command `deps` and the options `--deps` and `--no-deps` go; their ids are not reused.
- Keeping the code and the map in step is part of each change and of its review. The skill `unifold-convert` has the agent read build files and imports, and compare them with the map it writes.
- This supersedes 0019 and 0025. It amends [0034](0034-convert-a-repository-with-a-skill-instead-of-drafting-manifests.md): the skill, not the tool, compares the map with the code. It amends [0038](0038-make-a-contract-the-document-of-a-connection.md): its "dependencies are compared with code" no longer stands, and code of an ancestor that lies in no unit is no longer reported. It amends [0041](0041-what-git-ignores-is-outside-the-project.md): nothing is searched for dependencies any more.

### Consequences

- Good: the same guarantee for every unit, in any language.
- Good: the tool loses about 970 lines and its only knowledge of build systems.
- Bad: code that uses another unit without a need goes unnoticed until review, and a wiring line that no code needs any more stays.
- Bad: "checked against the code" is no longer a promise of unifold.
- Bad: rule `W3` can no longer see that code of a parent uses a child; [0048](0048-write-every-connection-out-and-let-a-unit-wire-its-own-need.md) gives the parent a way to say so.
