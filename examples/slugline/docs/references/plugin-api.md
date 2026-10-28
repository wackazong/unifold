# plugin-api

Contract of `core.plugin-api`: the trait a transliteration plug-in implements. The call that uses a plug-in, `slugify-with`, is a part of [slugify](slugify.md). Notation: wit.
Sources: the tests of `core`

## Parts

### transliterate

Kind: type

```wit
resource transliterate {
  transliterate: func(c: char) -> option<string>;
}
```

| Rule | Meaning |
|---|---|
| input | `c` is a character outside ASCII; the plug-in is never asked about an ASCII character |
| answer | ASCII text that is treated like typed text: empty, one letter or several letters, and it goes through the slug rules of [slugify](slugify.md) |
| `none` | "I do not know this character": the character is dropped |
| purity | an implementation has no side effects and gives the same answer for the same character |

## Fake

The real implementation: a plug-in is a table, and a consumer's test passes a table of its own with the answers it needs.
