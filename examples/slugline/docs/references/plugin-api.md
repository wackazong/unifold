# plugin-api

The contract of `plugin-api`: the trait a transliteration plug-in implements, and the call that uses one.

## Trait

```rust
pub trait Transliterate {
    fn transliterate(&self, c: char) -> Option<&str>;
}
```

- `c` is a character outside ASCII. The plug-in is never asked about an ASCII character.
- The answer is ASCII text that is treated like typed text: it may be empty, one letter, or several letters, and goes through the slug rules of [slugify](slugify.md) like any other input.
- `None` means "I do not know this character"; the character is dropped.
- An implementation has no side effects and gives the same answer for the same character.

## Call

`slugify_with(input, &options, &plugin)` makes a slug like `slugify` and asks `plugin` for every character outside ASCII.

## Examples

| Input | Plug-in answers | Slug |
|---|---|---|
| `Crème brûlée` | `è` → `e`, `û` → `u`, `é` → `e` | `creme-brulee` |
| `Straße` | `ß` → `ss` | `strasse` |
| `naïve` | `ï` → `None` | `nave` |
| `a→b` | `→` → `` (empty) | `ab` |
