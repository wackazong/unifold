---
status: proposed
date: 2026-10-21
---
# Convert a repository with a skill instead of drafting manifests from build files

## Context and Problem Statement

[0025](0025-compare-with-code-by-default-and-draft-manifests-from-build-files.md)
let `unifold init` draft a `unifold.yaml` for every package of a Cargo,
npm, Go or Python workspace: one capability per package, one need per
dependency, and the wiring between them. The draft restated the build
files. It could not tell whether a package is a part of the architecture
or a detail of the build, what a capability offers, what a need expects,
or whether a folder without a build file is a unit. Every trial ended with
a person or an agent rewriting most of it, and the draft had taught the
reader to think in packages. The extractors behind it carried guesses that
nothing else used: the kind of a package, its description, a list of build
files the tool does not read. Coding agents, meanwhile, can read a
repository and answer the questions that a build file cannot.

## Considered Options

- Keep the script and improve its heuristics
- Keep the script for the ecosystems it knows and add a skill for the rest
- Remove the script; a skill tells an agent, or a person, how to convert a
  repository, and `init` writes the root manifest only

## Decision Outcome

Chosen option: "remove the script and provide a skill", because the units
of a repository are a judgement about its architecture, and a judgement is
better made by someone who reads the code than guessed from a build file.

- `unifold init` writes the root manifest if there is none (`unifold`,
  `name`, `summary: TODO`), runs `generate`, and with `--agents` installs
  the skills. It reads no code.
- The skill `unifold-convert`, in `docs/skills/unifold-convert/`, is the
  procedure: find the parts in the layout and the build files, choose the
  units, write their manifests and wiring from the point of view of each
  unit, run `check` and let the comparison with the code correct the map,
  then report what was guessed.
- `init --agents` installs both skills. The comparison with code of 0025
  stays; the extractors keep only what `check` and `deps` use.
- The overlay examples for ripgrep and Online Boutique are withdrawn until
  the standard has settled. They return as results of the skill.

This amends 0025: its comparison with code stays, its drafts go.

### Consequences

- Good: a map starts from the architecture, not from the build files, and
  names roles instead of packages from the first line.
- Good: the tool loses about three hundred lines and four guesses that no
  test could pin down.
- Good: the procedure improves with the agents that run it, without a
  release of the tool.
- Bad: converting a repository needs a person or an agent with time to
  read it. There is no result after two commands.
- Bad: two agents convert the same repository differently. The comparison
  with code catches a missed dependency, not a poor choice of units.
- Bad: a project without an agent has a page of instructions where it had
  a command.
