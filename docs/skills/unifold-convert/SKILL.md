---
name: unifold-convert
description: Convert an existing repository to unifold, or bring a part of one into the map. Find the units in the folder layout and the build files, write one unifold.yaml per unit with capabilities, needs and wiring, and check the result against the code. Use it when a repository has no unifold.yaml yet, when `unifold check` passes but most folders are not units, or when a need is wired to a plain folder.
license: MIT OR Apache-2.0
---
# Convert a repository to unifold

The result is a map that a person can accept: a few well-chosen units,
each with a `unifold.yaml` that says what the folder offers and what it
expects, wired by the unit above, and a `check` that reports no error. No
script writes this map. A build file knows packages and their
dependencies, not which folders are parts of the architecture, what a part
offers, or what it expects from others. You read the repository and
decide; the tool checks what you decided against the code.

`unifold` below means the tool: `uvx unifold`, or
`python3 docs/skills/unifold/scripts/unifold.py` once the skills are
installed. The standard is one page: <https://unifold.md/spec>. How to
work in a converted project: the skill `unifold`.

## 0. Before you start

- If the root has no `unifold.yaml`, run `unifold init --agents` (or
  `unifold init`). It writes the root manifest and installs the skills.
- Run `unifold deps`. It prints the dependencies between folders that the
  tool reads from Cargo, npm, Go and Python build files and imports. This
  list is evidence; it is not the map.
- Read the root `README.md`, the build files at the root, and the first
  level of folders. Do not read code yet.

## 1. Find the parts

A unit is a folder that other parts use through an interface that should
stay stable, that is built, tested or released on its own, that has an
owner or decisions of its own, or that a reader needs as a box in a
diagram. Two of these make a unit; one does not.

1. List the candidates: packages of a workspace, services with their own
   deployment, feature or module folders, firmware components, shared
   schemas and protocol definitions, a deployment folder. Write down for
   each what it is, in one line.
2. Strike what is not a part: build output, test fixtures, vendored code,
   example and benchmark folders, a package that exists only so that the
   build works. Folders of a framework layer (`models/`, `views/`) are not
   units; the feature they belong to is.
3. Group what belongs together: a folder whose children are units is a
   unit itself, and its manifest holds the wiring between them. Keep the
   existing layout; unifold describes folders, it does not move code.
4. Decide the depth. Start with one or two levels. Fewer units, well
   chosen, beat many: every unit costs attention when its surroundings
   change. Most folders stay plain.

Before you write manifests for a large repository, tell the person which
folders you chose and which you left out, and why.

## 2. Write the manifests

Write each manifest from the template
[unifold.template.yaml](../unifold/assets/unifold.template.yaml), from the
point of view of that unit:

1. `summary`: what the unit is, in one line. The README and the package
   description help; write `TODO` only when you cannot say it.
2. `capabilities`: what the unit offers to others, named after what it
   offers, not after the package or the technology: `matcher`, not
   `grep-regex`. One capability per thing that others depend on
   separately; a package with one public interface has one. Add a
   `contract` where a file defines the interface (a trait, a schema, a
   `.proto`, an OpenAPI file) and `verified-by` where tests check it. Leave
   both out rather than point at something that does not fit.
3. `needs`: what the unit expects from outside, in its own words, never
   who provides it: `clock`, `cart-store`, `api-definition`. Do not declare
   the language runtime, the standard library, registry packages or
   logging. One need per thing expected; two packages that give the same
   thing are one need.
4. `status: planned` where the code does not exist yet; `kind` where it
   says something (`service`, `library`, `cli`, `adapter`); `owner` where
   known.
5. What the project needs from outside the repository (a database, a
   cloud API, a cluster) is a need of the root; what it offers to the
   outside is a capability of the root.

Then the wiring, in the manifest of the nearest unit above both sides:
`child.need: other-child.capability`, one line per need and child. A need
that no sibling meets becomes a need of the parent with the same name; it
passes up without a line. A need met by code of the parent that is not a
unit is wired to `./folder`; these lines are the list of work that
remains. Where several providers exist, write named alternatives; the
first is the default. Patterns: <https://unifold.md/wiring>.

## 3. Check against the code

```sh
unifold check --fix
```

- `D1`, a dependency in code without a connection: a need or a wiring line
  is missing, or the folder that holds the code should be a unit. Add the
  need; do not touch the code.
- `D2`, a connection without a dependency in code: the need may be wrong,
  or the dependency is one that no extractor sees, such as a call between
  services or a file read at run time. Write such dependencies into a list
  with their evidence and pass it with `check --deps FILE`; the format is
  in <https://unifold.md/tool>.
- `W2`, a need without a provider: wire it, pass it up, or declare it at
  the root as a need of the project. Do not mark it `optional`.
- `W3`, a capability nobody uses: either someone does and the wiring is
  missing, or it is not a capability. Remove it in that case.
- `W8`, a need met by a plain folder: fine for now; it names a unit to be.

Repeat until `check` reports no error. Then run `unifold tree` and
`unifold show` for each unit and read the result as a stranger would: does
every box and every arrow mean something?

## 4. Report

Tell the person:

- the units you chose and the candidates you left out, with the reason;
- every capability and need whose name or summary is a guess;
- the needs wired to `./folder`, as the list of work that remains;
- the dependencies you passed with `--deps`, with the evidence for each;
- warnings that remain, and summaries that are still `TODO`;
- that the map is a proposal: a person accepts it by reading it, not by
  running the check.

If the project should also carry written knowledge, set `level: full` on
the root or on one unit and follow the skill `unifold`
(<https://unifold.md/documents>).

## What not to do

- Do not write one unit per folder, or one capability per package, and
  call it done. A map that restates the build files adds nothing.
- Do not name a need after its provider. The provider may change; the
  need stays.
- Do not weaken a manifest to make `check` pass: no `optional`, no deleted
  need, no removed capability unless it was wrong.
- Do not move code. If the layout does not match the architecture,
  describe the layout and say so in the report.
- Do not write `README.md` or decisions in this step. Level
  `core` is the map; level `full` is a second step.
