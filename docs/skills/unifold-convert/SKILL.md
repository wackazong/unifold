---
name: unifold-convert
description: Convert an existing repository to unifold, or bring a part of one into the map. Find the units in the folder layout and the build files, write one unifold.yaml per unit with capabilities, needs and wiring, and check the result against the code. Use it when a repository has no unifold.yaml yet, when `unifold check` passes but most folders are not units, or when it reports dependencies on code that has no manifest.
license: MIT OR Apache-2.0
---

# Convert a repository to unifold

The result is a map that a person can accept: a few well-chosen units, wired by the unit above, and a clean `check`. Each unit has a `unifold.yaml` that says what the folder provides and what it needs. No script writes this map. A build file knows packages and their dependencies. It does not know which folders are parts of the architecture, what a part provides, or what it needs from others. You read the repository and decide; the tool checks what you decided against the code.

`unifold` below means the tool of the skill `unifold`: `uv run docs/skills/unifold/scripts/unifold.py` once the skills are installed, or `python3` with PyYAML in place of `uv run`. The standard is one page: <https://unifold.md/spec>. How to work in a converted project: the skill `unifold`.

## 0. Before you start

- If the root has no `unifold.yaml`, run `unifold init --agents` (or `unifold init`). It writes the root manifest and installs the skills. It writes a `README.md` from the template if there is none.
- Run `unifold deps`. It prints the dependencies between folders that the tool reads from Cargo, npm, Go and Python build files and imports. This list is evidence; it is not the map.
- Read the root `README.md`, the build files at the root, and the first level of folders. Do not read code yet.

## 1. Find the parts

A folder is a unit when two of these hold; one is not enough:

- other parts use it through an interface that should stay stable;
- it is built, tested or released on its own;
- it has an owner or decisions of its own;
- a reader needs it as a box in a diagram.

1. List the candidates: workspace packages, services with their own deployment, feature or module folders, firmware components, a deployment folder. A unit holds code that is built, run or deployed. A shared schema or protocol definition is not a unit; it is the contract of the connections that carry it. Write down for each candidate what it is, in one line.
2. Strike what is not a part: build output, test fixtures, vendored code, example and benchmark folders. Strike a package that exists only so that the build works. Folders of a framework layer (`models/`, `views/`) are not units; the feature they belong to is.
3. Group what belongs together. A folder whose children are units is a unit itself, and its manifest holds the wiring between them. Keep the existing layout; unifold describes folders, it does not move code.
4. Decide the depth. Start with one or two levels. Fewer units, well chosen, beat many: every unit costs attention when its surroundings change. Most folders stay plain.

Before you write manifests for a large repository, tell the person which folders you chose and which you left out, and why.

## 2. Write the manifests

Write each manifest from the template [unifold.template.yaml](../unifold/assets/unifold.template.yaml), from the point of view of that unit:

1. `summary`: what the unit is, in one line. The README and the package description help; write `TODO` only when you cannot say it.
2. `capabilities`: what the unit provides to others. Name each after what it provides, not after the package or the technology: `matcher`, not `grep-regex`. Declare one capability per thing that others depend on separately; a package with one public interface has one. Add `verified-by` where tests check it; leave it out rather than point at something that does not fit. The `contract` comes with the wiring, below.
3. `needs`: what the unit needs from outside, in its own words, never who provides it: `clock`, `cart-store`, `api-definition`. Do not declare the language runtime, the standard library, registry packages or logging. Declare one need per thing; two packages that give the same thing are one need.
4. `status: planned` where the code does not exist yet; `kind` where it says something (`service`, `library`, `cli`, `adapter`); `owner` where known.
5. A need of the project itself is a need of the root: a database, a cloud API, a cluster. What it provides to the outside is a capability of the root.
6. Every unit needs a `README.md`. Keep one that exists. Where there is none, write a short one from the template ([README.template.md](../unifold/assets/README.template.md)): the heading, one paragraph on what the unit is for, and a `## Why` of a few lines.

Then the wiring, in the manifest of the nearest unit above both sides: `child.need: other-child.capability`, one line per need and child. A need that no sibling meets becomes a need of the parent with the same name; it passes up without a line. Where several providers exist, write named alternatives; the first is the default. Patterns: <https://unifold.md/wiring>.

Then the contracts. Every connection carries something in some form. Both of its sides name the document that defines it. The document lies in `docs/references/` of the unit that holds the wiring, or of a unit above it, never in a sibling. A need that is passed up names the same document at every level.

Where a schema, a `.proto` or an OpenAPI file already defines the interface and lies where both sides may name it, name it. Where only a sibling holds it, move it up. Where nothing exists, write a short reference with the form and an example.

## 3. Check against the code

```sh
unifold check --fix
```

- `D1`, a dependency in code without a connection. A need or a wiring line is missing, or the folder that holds the code has no manifest yet. Add the need, or give the folder a manifest with a capability. Do not touch the code.
- `D2`, a connection without a dependency in code. The need may be wrong, or no extractor sees the dependency: a call between services, a file read at run time. Write such dependencies into a list with their evidence and pass it with `check --deps FILE`. The format is in <https://unifold.md/tool>.
- `W2`, a need without a provider. Wire it, pass it up, or declare it at the root as a need of the project. Do not mark it `optional`.
- `W3`, a capability nobody uses. Either someone does and the wiring is missing, or it is not a capability; remove it in that case.
- `W11`, a side of a connection without a contract, or two sides that name different documents. Write or move the document and point both sides at it.

Repeat until `check` reports no error. Then run `unifold tree` and `unifold show` for each unit. Read the result as a stranger would: does every box and every arrow mean something?

## 4. Report

Tell the person:

- the units you chose and the candidates you left out, with the reason;
- every capability and need whose name or summary is a guess;
- the dependencies on code that has no manifest yet: the work that remains;
- the dependencies you passed with `--deps`, with the evidence for each;
- the warnings that remain and the summaries that are still `TODO`;
- that the map is a proposal. A person accepts it by reading it, not by running the check.

The `README.md` files you wrote are drafts. Complete them with the skill `unifold` once the map is accepted.

## What not to do

- Do not write one unit per folder, or one capability per package, and call it done. A map that restates the build files adds nothing.
- Do not name a need after its provider. The provider may change; the need stays.
- Do not weaken a manifest to make `check` pass: no `optional`, no deleted need, no removed capability unless it was wrong.
- Do not move code. If the layout does not match the architecture, describe the layout and say so in the report.
- Do not write decisions or rewrite an existing `README.md` in this step: the map comes first, the documents second.
