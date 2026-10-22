# cli

The `slugline` command: it prints its arguments as one slug, or one slug for each line of standard input. It is the thin shell around the library for people who work in a terminal or a script.

## Why

A command is the cheapest way to try the library and to use it from a shell pipeline. The crate holds only argument parsing and input handling, so that every rule about what a slug looks like stays in one place, the library it depends on. The command, not the library, needs the transliteration plug-in: it is the one place that knows which letters its users type.

## Capabilities

### `slugline-command`

`slugline "Crème brûlée"` prints `creme-brulee`. Without arguments it reads standard input and prints one slug per line, in order. Exit code 0 when a slug was printed for every input, 1 when input or output failed, 2 for an option that is unknown or has no valid value.

Contract: [slugline-command](../docs/references/slugline-command.md). Tests: [tests/cli.rs](tests/cli.rs).

## Needs

### `slugify`

A function that turns one string into one slug, with or without a plug-in for letters outside ASCII.

### `transliteration`

A plug-in that replaces Latin letters with diacritics by ASCII letters, so that `é` becomes `e` instead of being dropped.

## Out of scope

- Options beyond those of the contract: no configuration file, no locale.
