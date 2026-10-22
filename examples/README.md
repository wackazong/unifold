# Examples

Two projects that use [unifold](https://unifold.md). Each is a project of
its own, with its own root `unifold.yaml`, and is checked on its own. Start
with slugline.

| Example | What it is | What it shows | Level |
|---|---|---|---|
| [slugline](slugline/README.md) | A small Cargo workspace with code and tests: 3 crates, 4 units | The whole of level `core` in four manifests; dependencies read from `Cargo.toml`; one unit, `core`, at level `full` with a README that has a `## Why`, a generated `AGENTS.md`, a decision, an invariants file and a context item with a stamp; what `check` prints when the map is wrong | `core`, one unit `full` |
| [plantwatch](plantwatch/README.md) | The design of a product with firmware, a phone app and cloud services, written before any code: 23 units, all `planned` | Every document convention of level `full`: interfaces, the why in every README, explanation files (reasoning, invariants, runtime, deployment, risks, requirements), 47 decisions, 200 context items with stamps, glossaries, skills, a tutorial for an end user; needs passed up by name; alternatives. Much more than a unit should cost | `full` |

## Run them

`unifold` below is the reference tool. Until the package is published, run
it from this repository:

```sh
alias unifold="python3 $PWD/../docs/skills/unifold/scripts/unifold.py"   # in this folder
```

It needs Python 3.9 or newer with PyYAML.

```sh
(cd slugline && cargo test --workspace && unifold check --strict)
(cd plantwatch && unifold check --strict)
```

Each example has an explorer page, `unifold.html`, written by
`unifold site`. `unifold show PATH` and `unifold tree` work in every
example.

## Planned

Maps of existing open-source repositories, kept as overlays of manifests
without the code, will come back once the standard has settled: one for a
Rust workspace such as ripgrep, and one for a set of services in several
languages such as Online Boutique, with the calls between services given
to `check` as a list. Both are results of the skill `unifold-convert`.
