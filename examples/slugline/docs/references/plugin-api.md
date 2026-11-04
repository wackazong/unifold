# plugin-api

Contract of `core.plugin-api`: the trait a transliteration plug-in implements. The call that uses a plug-in, `slugify-with`, is a part of [slugify](slugify.md). Notation: wit.
Sources: the tests of `core`
Binding: in-process
Version: 1

## Use

A plug-in implements the trait once, and `slugify-with` calls it for each character outside ASCII. The trait has no state: an implementation answers every question alone, in any order.

## Qualities

| Aspect | Guarantee |
|---|---|
| concurrency | an implementation has no side effects and gives the same answer for the same character, so `core` may call it at any time, also at the same time |

## Parts

### transliterate

Kind: callback

```wit
resource transliterate {
  transliterate: func(c: char) -> option<string>;
}
```

Pre: `c` is a character outside ASCII; the plug-in is never asked about an ASCII character.
Result: ASCII text, or `none`. The text is treated like typed text: it may be empty, one letter or several letters, and it goes through the slug rules of [slugify](slugify.md). `none` means "I do not know this character", and the character is dropped.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| one letter | `transliterate('É')` | `E` |
| several letters | `transliterate('ß')` | `ss` |
| text with a space | `transliterate('→')` | `" to "` |
| empty answer | `transliterate('™')` | `""` |
| unknown character | `transliterate('ï')` | `none` |

## Fake

The real implementation: a plug-in is a table, and a consumer's test passes a table of its own with the answers it needs.
