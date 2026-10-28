# cli

The `slugline` command: it prints its arguments as one slug, or one slug for each line of standard input. It is the thin shell around the library for people who work in a terminal or a script.

## Why

A command is the cheapest way to try the library and to use it from a shell pipeline. The crate holds only argument parsing and input handling, so that every rule about what a slug looks like stays in one place, the library it depends on. The command, not the library, needs the transliteration plug-in: it is the one place that knows which letters its users type.

