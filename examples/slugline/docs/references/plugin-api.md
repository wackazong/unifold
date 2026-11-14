# plugin-api

Contract of `unicode.plugin-api`, which `core` needs: the trait a transliteration plug-in implements, so that `core` can ask it about each character outside ASCII. A program passes the plug-in to `slugify-with` of [slugify](slugify.md); `unicode` provides one for Latin letters, and a program may write its own. Notation: wit.
Sources: the tests of `core` and `unicode`, the Unicode blocks Latin-1 Supplement and Latin Extended-A
Binding: in-process
Version: 1

## Use

A plug-in implements the trait once, and `slugify-with` asks it about each character outside ASCII. The trait has no state: an implementation answers every question alone, in any order.

## Qualities

| Aspect | Guarantee |
|---|---|
| concurrency | an implementation has no side effects and gives the same answer for the same character, so `core` may call it at any time, also at the same time |

## Parts

### transliterate

Kind: operation

```wit
resource transliterate {
  transliterate: func(c: char) -> option<string>;
}
```

Pre: `c` is a character outside ASCII; the plug-in is never asked about an ASCII character.
Result: ASCII text, or `none`. The text is treated like typed text: it may be empty, one letter or several letters, and it goes through the slug rules of [slugify](slugify.md). `none` means "I do not know this character", and the character is dropped. The plug-in of this project, `unicode`, maps every letter of the Unicode blocks Latin-1 Supplement and Latin Extended-A to its base letter or letters, in lower case; ligatures map to two letters: `æ` to `ae`, `œ` to `oe`, `ĳ` to `ij`, `ß` to `ss`, `þ` to `th`; any other character gets `none`. A plug-in of a program gives its own answers; the examples are those of `unicode`.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| acute accent | `transliterate('é')` | `e` |
| stroke, upper case | `transliterate('Ø')` | `o` |
| stroke | `transliterate('ł')` | `l` |
| ligature, upper case | `transliterate('Æ')` | `ae` |
| sharp s | `transliterate('ß')` | `ss` |
| an arrow | `transliterate('→')` | `none` |
| Cyrillic | `transliterate('я')` | `none` |

## Fake

The real implementation: a plug-in is a table, and a consumer's test passes a table of its own with the answers it needs.
