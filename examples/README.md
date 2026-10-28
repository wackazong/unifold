# Examples

Three projects that use [unifold](https://unifold.md), for anyone who wants to see the standard applied before reading it. Each is a project of its own, with its own root `unifold.yaml`, and is checked on its own. Start with slugline.

| Example | What it is | What it shows |
|---|---|---|
| [slugline](slugline/README.md) | A small Cargo workspace with code and tests: 3 crates, 4 units | The whole map in four manifests; a short README per unit, and in `core` a decision, an invariants file and a context item with a stamp; the generated `AGENTS.md`; what `check` prints when the map is wrong |
| [serial-line](serial-line/README.md) | The design of a small program that opens a session over a serial line: 6 units, all `planned` | The three well-known kinds, a composite, a secret and a `not` per unit, six contracts with parts, examples and fakes, scenarios across levels with generated sequence diagrams, decisions of status derived and proposed, a constants table. The example of the build method [maike](https://github.com/wackazong/maike) |
| [plantwatch](plantwatch/README.md) | The design of a product with firmware, a phone app and cloud services, written before any code: 22 units, all `planned` | Every document convention: interfaces, the why in every README, explanation files (reasoning, invariants, runtime, deployment, risks, requirements), 48 decisions, 205 context items with stamps, 27 contracts with parts and fakes, 9 scenarios across levels, glossaries, skills, a tutorial for an end user; needs passed up line by line; alternatives. Much more than a unit should cost |

## Why

A standard is understood from an example faster than from its text, and every rule here is tried on these projects before a project outside has to follow it. Three examples, not one, because the questions differ: slugline has code, so it shows a map beside a real build and stays small enough to read in ten minutes; serial-line is a design small enough to read in twenty minutes and shows contracts, scenarios and kinds as a build process uses them; plantwatch has no code, so it shows what the documents of a large design look like when every convention is used, which is more than most units should carry. The repository of the standard itself is not a unit, so the examples are the only projects here that `check` can confirm.

## Why not more

- A map of an existing open-source repository. Two such maps are planned for when the standard is stable, as overlays of manifests without the code: a Rust workspace such as ripgrep, and a set of services in several languages such as Online Boutique, whose calls between services are needs. The skill `unifold-convert` writes both.
- Running code for plantwatch. It is a design; its units are `planned`.

## Commands

`unifold` below is the reference tool, `uvx unifold`. To check the examples with the tool of this repository instead, which may be newer:

```sh
alias unifold="python3 $PWD/../docs/skills/unifold/scripts/unifold.py"   # in this folder
```

It needs Python 3.9 or newer with PyYAML.

```sh
(cd slugline && cargo test --workspace && unifold check --strict)
(cd serial-line && unifold check --strict)
(cd plantwatch && unifold check --strict)
```

Each example has an explorer page, `unifold.html`, written by `unifold site`. `unifold show PATH` and `unifold tree` work in every example.

## Read next

1. [slugline](slugline/README.md), then its tutorials: the three commands, and what `check` prints when the map is broken.
2. [serial-line](serial-line/README.md): one contract, one scenario and its generated diagram, one derived decision.
3. [plantwatch](plantwatch/README.md), the front page of a product, and one leaf unit of it, such as the alert rules.
