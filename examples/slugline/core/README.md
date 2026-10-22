# core

Turns text into a URL slug and defines the interface of a transliteration plug-in.

## Why

Everything that decides what a slug looks like is in this crate, so the [format](docs/explanation/context.md) can break in one place only. Character tables are large and a matter of taste: they stay outside, behind a trait
([decision 0001](docs/decisions/0001-a-plug-in-is-passed-with-each-call.md)).

## Capabilities

### `slugify`

`slugify("Hello, World!", &Options::default())` returns `hello-world`.

- Only `a-z`, `0-9` and `Options::separator` remain.
- No separator at the start or the end, never two in a row.
- At most `max_len` characters.
- Apostrophes and characters outside ASCII are dropped. Any other character ends a word.
- A slug is its own slug.

Contract: [slugify](../docs/references/slugify.md). Tests:
[tests/slugify.rs](tests/slugify.rs).

### `plugin-api`

`slugify_with(input, &options, &plugin)` asks a `Transliterate` plug-in:

- only about characters outside ASCII;
- an answer is treated like typed text, and may have several letters or none;
- `None` drops the character.

Contract: [plugin-api](../docs/references/plugin-api.md). Tests:
[tests/plugin.rs](tests/plugin.rs).

## Out of scope

- Character tables. Unique slugs.
