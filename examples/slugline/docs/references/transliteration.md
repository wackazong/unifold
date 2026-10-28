# transliteration

Contract of `unicode.transliteration`: a plug-in that replaces Latin letters with diacritics, and ligatures, by ASCII letters. It implements the trait of [plugin-api](plugin-api.md). Notation: wit.
Sources: the Unicode blocks Latin-1 Supplement and Latin Extended-A

## Parts

### transliterate

Kind: query

```wit
transliterate: func(c: char) -> option<string>;
```

Pre: `c` is outside ASCII.
Result: every letter of the Unicode blocks Latin-1 Supplement and Latin Extended-A maps to its base letter or letters, in the case of the base letter; ligatures map to two letters: `æ` to `ae`, `œ` to `oe`, `ĳ` to `ij`, `ß` to `ss`, `þ` to `th`; any other character gets `none`.
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

The real implementation: a table with no side effects, and a consumer that wants other answers passes a table of its own.
