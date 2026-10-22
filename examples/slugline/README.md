# slugline

Turns text into a URL slug: `Crème brûlée` becomes `creme-brulee`. A small
Cargo workspace with three crates, and the showcase of
[unifold](https://unifold.md).

Each crate has a `unifold.yaml`; the [root manifest](unifold.yaml) wires
them. Only [core](core/README.md) is at level `full`, with documents. The
picture is generated: [component diagram](docs/diagrams/component.md), or
open `unifold.html`.

```sh
cargo test --workspace
alias unifold='python3 ../../docs/skills/unifold/scripts/unifold.py'
```

## Three commands

```console
$ unifold check
4 unit(s): 0 error(s), 0 warning(s), 0 info; 3 dependencies observed in code
```

The three dependencies are read from the `Cargo.toml` files.

```console
$ unifold show plugins/unicode
unit      unicode  (plugins/unicode)
summary   Transliterates Latin letters with diacritics to ASCII
status    active · library · level core
manifest  plugins/unicode/unifold.yaml
parent    slugline
children  none
provides
  transliteration (library): Replaces Latin letters that have diacritics, and ligatures, by ASCII letters  verified by plugins/unicode/tests/latin.rs  conforms to need plugin-api
      used by cli as need 'transliteration'
needs
  plugin-api (library): The trait a transliteration plug-in implements
      provided by core capability 'plugin-api'  contract core/src/lib.rs  verified by core/tests/plugin.rs
```

```console
$ unifold capability plugins/unicode plugin-api
--- plugins/unicode needs 'plugin-api' (library): The trait a transliteration plug-in implements

--- core provides 'plugin-api' (library): The trait a transliteration plug-in implements, and a slugify that uses one
    contract: core/src/lib.rs
    verified by: core/tests/plugin.rs
`slugify_with(input, &options, &plugin)` asks a `Transliterate` plug-in:

- only about characters outside ASCII;
- an answer is treated like typed text, and may have several letters or none;
- `None` drops the character.

Tests: [tests/plugin.rs](tests/plugin.rs).
```

## Break it

**Remove a wiring line.** Delete `cli.transliteration:
unicode.transliteration` from [unifold.yaml](unifold.yaml):

```console
$ unifold check
error G1 docs/diagrams/component.md: generated file is out of date
    fix: Run `unifold generate` (or `unifold check --fix`).
error D1 unifold.yaml:18: 'cli' depends on 'plugins/unicode', but no need of 'cli' is connected to 'unicode' (cargo: cli/Cargo.toml [dependencies] slugline-unicode)
    fix: Add a need to cli/unifold.yaml (for example `unicode`), and add `cli.unicode: unicode.transliteration` to the wiring here. Or remove the dependency from the code.
error W2 unifold.yaml:18: need 'cli.transliteration' has no provider
    fix: Add `cli.transliteration: unicode.transliteration` to the wiring.
warn W3 unifold.yaml:18: 'unicode.transliteration' is provided but nothing uses it
    fix: Wire the unit that should use it, or implement a capability of the parent with it (`capability: child.capability`), or remove the capability.
4 unit(s): 3 error(s), 1 warning(s), 0 info  [D1×1, G1×1, W2×1, W3×1]; 3 dependencies observed in code
```

**Add a dependency that no manifest declares.** Let `core` use the table
of the plug-in. Append to `core/Cargo.toml`:

```toml
[dependencies]
slugline-unicode = { path = "../plugins/unicode" }
```

```console
$ unifold check
error D1 unifold.yaml:18: 'core' depends on 'plugins/unicode', but no need of 'core' is connected to 'unicode' (cargo: core/Cargo.toml [dependencies] slugline-unicode)
    fix: Add a need to core/unifold.yaml (for example `unicode`), and add `core.unicode: unicode.transliteration` to the wiring here. Or remove the dependency from the code.
4 unit(s): 1 error(s), 0 warning(s), 0 info  [D1×1]; 4 dependencies observed in code
```

Cargo refuses this particular edit too, because it closes a cycle. unifold
reports every dependency that is not wired, also those Cargo accepts.
