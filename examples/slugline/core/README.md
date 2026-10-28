# core

Turns text into a URL slug and defines the interface of a transliteration plug-in.

## Why

Everything that decides what a slug looks like is in this crate, so the [format](docs/explanation/context.md) can break in one place only. Character tables are large and a matter of taste: they stay outside, behind a trait ([decision 0001](docs/decisions/0001-a-plug-in-is-passed-with-each-call.md)).

