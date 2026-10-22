# slugline

Turns text into a URL slug: `Crème brûlée` becomes `creme-brulee`. A Rust library and a command, in a small Cargo workspace of three crates, for anyone who needs stable, readable identifiers from free text. It is also the small showcase of [unifold](https://unifold.md): four units with code and tests, a map that `check` compares with the `Cargo.toml` files.

## Why

A slug has to be the same forever once it is in a URL, so the rules that make one are concentrated in one crate and tested as a contract, while the part that is a matter of taste, which letters replace `é` or `ß`, is a plug-in behind a trait. The command is a thin shell over the library. As an example of unifold, the workspace is cut so that every kind of connection appears once: a capability of a child implements one of the root, a need is provided by a sibling, and a plug-in needs the trait that the library defines. Each unit has a short `README.md`; only `core` carries documents beyond it, so a reader can see the smallest unit and a complete one side by side.

## Capabilities

### `slugify`

`slugify("Hello, World!", &Options::default())` returns `hello-world`. Only `a-z`, `0-9` and the separator remain; no separator at the start, the end or twice in a row; at most `max_len` characters; a slug is its own slug. Contract:
[slugify](docs/references/slugify.md).

### `plugin-api`

The trait a transliteration plug-in implements, and a `slugify_with` that asks the plug-in about every character outside ASCII. Contract:
[plugin-api](docs/references/plugin-api.md).

### `slugline-command`

`slugline Crème brûlée` prints `creme-brulee`; without arguments it slugs each line of standard input. Exit code 0, 1 for an input or output failure, 2 for a bad option. Contract:
[slugline-command](docs/references/slugline-command.md).

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
2. [Break the map](docs/tutorials/break-the-map.md): what `check` says when a wiring line is missing or the code depends on something unwired.
3. The generated [component diagram](docs/diagrams/component.md), or `unifold.html` in a browser.
4. [core](core/README.md), the one unit with documents of its own.
