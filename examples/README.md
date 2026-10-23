# Examples

Two projects that use [unifold](https://unifold.md), for anyone who wants to see the standard applied before reading it. Each is a project of its own, with its own root `unifold.yaml`, and is checked on its own. Start with slugline.

| Example | What it is | What it shows |
|---|---|---|
| [slugline](slugline/README.md) | A small Cargo workspace with code and tests: 3 crates, 4 units | The whole map in four manifests; dependencies read from `Cargo.toml`; a short README per unit, and in `core` a decision, an invariants file and a context item with a stamp; the generated `AGENTS.md`; what `check` prints when the map is wrong |
| [plantwatch](plantwatch/README.md) | The design of a product with firmware, a phone app and cloud services, written before any code: 22 units, all `planned` | Every document convention: interfaces, the why in every README, explanation files (reasoning, invariants, runtime, deployment, risks, requirements), 48 decisions, 195 context items with stamps, glossaries, skills, a tutorial for an end user; needs passed up by name; alternatives. Much more than a unit should cost |

## Why

A standard is understood from an example faster than from its text, and every rule here is tried on these two projects before a project outside has to follow it. Two examples, not one, because the questions differ: slugline has code, so it shows the comparison of the map with real dependencies and stays small enough to read in ten minutes; plantwatch has no code, so it shows what the documents of a large design look like when every convention is used, which is more than most units should carry. The repository of the standard itself is not a unit, so the examples are the only projects here that `check` can confirm.

## Out of scope

- A map of an existing open-source repository. Two such maps are planned for when the standard is stable, as overlays of manifests without the code: a Rust workspace such as ripgrep, and a set of services in several languages such as Online Boutique, with the calls between services given to `check` as a list. The skill `unifold-convert` writes both.
- Running code for plantwatch. It is a design; its units are `planned`.

## Commands

`unifold` below is the reference tool, `uvx unifold`. To check the examples with the tool of this repository instead, which may be newer:

```sh
alias unifold="python3 $PWD/../docs/skills/unifold/scripts/unifold.py"   # in this folder
```

It needs Python 3.9 or newer with PyYAML.

```sh
(cd slugline && cargo test --workspace && unifold check --strict)
(cd plantwatch && unifold check --strict)
```

Each example has an explorer page, `unifold.html`, written by `unifold site`. `unifold show PATH` and `unifold tree` work in every example.

## Read next

1. [slugline](slugline/README.md), then its tutorials: the three commands, and what `check` prints when the map is broken.
2. [plantwatch](plantwatch/README.md), the front page of a product, and one leaf unit of it, such as the alert rules.
