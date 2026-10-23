# AGENTS.md: unifold

This repository holds the unifold standard. Read [README.md](README.md) first: it says what unifold is and why it is built this way. Everything else is in `docs/`. The repository is a specification, which is not a unit, so it has no `unifold.yaml`; the projects in `examples/` have maps.

## Documents

| Kind | Files |
|---|---|
| Learn | [first-map](docs/tutorials/first-map.md) |
| Look up | [spec](docs/references/spec.md), [documents](docs/references/documents.md), [writing](docs/references/writing.md), [rules](docs/references/rules.md), [tool](docs/references/tool.md), [tool-json](docs/references/tool-json.md), [agents](docs/references/agents.md) |
| Understand | [requirements](docs/explanation/requirements.md), [reasoning](docs/explanation/reasoning.md), [invariants](docs/explanation/invariants.md), [risks](docs/explanation/risks.md), [wiring](docs/explanation/wiring.md), [decisions](docs/decisions/index.md) |

## Skills

| Skill | Description |
|---|---|
| [unifold](docs/skills/unifold/SKILL.md) | Work in a repository that contains unifold.yaml files. Find out what a folder provides and needs and who is on the other side, change units, capabilities and wiring, record decisions, and check the result. Use it when a task touches the interface or the dependencies of a folder, the architecture, or the documents of a unit, and before you finish any change in such a repository. |
| [unifold-convert](docs/skills/unifold-convert/SKILL.md) | Convert an existing repository to unifold, or bring a part of one into the map. Find the units in the folder layout and the build files, write one unifold.yaml per unit with capabilities, needs and wiring, and check that the map is complete and matches what the code uses. Use it when a repository has no unifold.yaml yet, or when `unifold check` passes but most folders are not units. |

## unifold

The examples in `examples/` are [unifold](https://unifold.md) projects. A folder with a `unifold.yaml` is a unit: the file says what the unit provides and needs, and the unit above connects needs to providers. Read a map before you change an interface in an example; keep it true after.

- `python3 docs/skills/unifold/scripts/unifold.py show PATH`: a unit, its capabilities and needs, and who is on the other side
- `python3 docs/skills/unifold/scripts/unifold.py capability PATH NAME`: both ends of one connection, with contracts
- `python3 docs/skills/unifold/scripts/unifold.py check`: is the map consistent (`--fix` rewrites generated files)

How to read and write the map: the skill [unifold](docs/skills/unifold/SKILL.md). How to bring folders into the map: the skill [unifold-convert](docs/skills/unifold-convert/SKILL.md).
