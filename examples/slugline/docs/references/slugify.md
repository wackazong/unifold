# slugify

The contract of `slugify`: a function that turns one string into one slug. What a slug is, is in [slug.md](slug.md).

## Call

`slugify(input, &options)` returns a `String`. `Options` has `separator`, one character, default `-`, and `max_len`, an optional number of characters.

## Rules

- Letters and digits of ASCII are kept, in lower case. An apostrophe is dropped. Any other ASCII character ends a word.
- A character outside ASCII is dropped, unless a plug-in replaces it ([plugin-api](plugin-api.md)).
- Exactly one separator stands between two words; none at the start or the end, also after a cut at `max_len`.
- The result has at most `max_len` characters.

## Examples

| Input | Options | Slug |
|---|---|---|
| `Hello, World!` | default | `hello-world` |
| `two   words` | default | `two-words` |
| `Rock 'n' Roll` | default | `rock-n-roll` |
| `Hello, World!` | `separator: _` | `hello_world` |
| `Hello, World!` | `max_len: 6` | `hello` |
| `Crème brûlée` | default | `crme-brle` |
| `hello-world` | default | `hello-world` |
