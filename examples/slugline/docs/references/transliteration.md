# transliteration

Contract of `unicode.transliteration`: a plug-in that replaces Latin letters with diacritics, and ligatures, by ASCII letters. It implements the trait of [plugin-api](plugin-api.md). Notation: wit.
Sources: the Unicode blocks Latin-1 Supplement and Latin Extended-A
Binding: in-process

## Use

A consumer takes the plug-in with `latin` and passes it to `slugify-with` of [slugify](slugify.md), or asks it about one character at a time with `transliterate`. The connection has no state: any part may be called at any time.

## Qualities

| Aspect | Guarantee |
|---|---|
| concurrency | the plug-in is a table with no side effects; `transliterate` may be called at any time, also at the same time |

## Parts

### latin

Kind: query

```wit
latin: func() -> transliterate;
```

Pre: none.
Result: the plug-in for Latin script, a `transliterate` of [plugin-api](plugin-api.md) whose answers are those of the part `transliterate` below. Every call returns the same table.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| the plug-in | `latin()` | a plug-in with the answers of `transliterate` |

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
