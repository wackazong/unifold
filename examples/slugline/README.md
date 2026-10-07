# slugline

Turns any string into a URL slug: `Hello World` becomes `hello-world`. A
library, a command, and a way to plug in transliteration.

This is the small example of the [youmedoc](https://youmedoc.example)
standard, at level `core`: three units, each with a `unit.yaml` and a
`README.md`, wired in [unit.yaml](unit.yaml). The source files are
placeholders. The map of the project is the
[component diagram](doc/diagrams/component.md).

## Provides

### `slugify`

A function that turns one string into one slug. The slug contains only
`a-z`, `0-9` and the separator, and is at most as long as the caller allows.

### `slug-cli`

The command `slugline`. It reads lines on standard input and writes one slug
per line on standard output.

## Checking the wiring against the code

`deps.json` lists which source file depends on which, as a build tool would
report it. `youmedoc check --deps deps.json` compares it with the wiring.
