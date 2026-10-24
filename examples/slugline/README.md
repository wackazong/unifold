# slugline

Turns text into a URL slug: `Crème brûlée` becomes `creme-brulee`. A Rust library and a command, in a small Cargo workspace of three crates, for anyone who needs stable, readable identifiers from free text. It is also the small showcase of [unifold](https://unifold.md): four units with code and tests, and a map of them in four manifests.

## Why

A slug has to be the same forever once it is in a URL, so the rules that make one are concentrated in one crate and tested as a contract, while the part that is a matter of taste, which letters replace `é` or `ß`, is a plug-in behind a trait. The command is a thin shell over the library. As an example of unifold, the workspace is cut so that every kind of connection appears once; the [component diagram](docs/diagrams/component.md) shows them. Each child has a short `README.md`, and `core` also has a decision, invariants and a context item, so a reader can see the smallest unit and a complete one side by side.

## Out of scope

- Unique slugs: nothing here knows which slugs exist already.
- Scripts other than Latin. A Cyrillic or Greek table is another plug-in.
- A configuration file or locale for the command.

## Commands

```sh
cargo test --workspace
alias unifold='python3 ../../docs/skills/unifold/scripts/unifold.py'
unifold check
```

## Read next

1. [Three commands](docs/tutorials/three-commands.md): what `check`, `show` and `capability` print for this project.
2. [Break the map](docs/tutorials/break-the-map.md): what `check` says when a wiring line is missing or the two sides of a connection name different contracts.
3. The generated [component diagram](docs/diagrams/component.md), or `unifold.html` in a browser.
4. [core](core/README.md), the child with a decision, invariants and a context item.
