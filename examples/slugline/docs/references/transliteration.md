# transliteration

Contract of `unicode.transliteration`: a plug-in that replaces Latin letters with diacritics, and ligatures, by ASCII letters. It implements the trait of [plugin-api](plugin-api.md). Notation: wit.
Sources: the Unicode blocks Latin-1 Supplement and Latin Extended-A
Binding: in-process

## Use

A consumer takes the plug-in with `latin` and passes it to `slugify-with` of [slugify](slugify.md), which asks it about one character at a time with `transliterate` of [plugin-api](plugin-api.md). The connection has no state: `latin` may be called at any time.

## Qualities

| Aspect | Guarantee |
|---|---|
| concurrency | the plug-in is a table with no side effects; it may be used at any time, also at the same time |

## Parts

### latin

Kind: operation

```wit
latin: func() -> transliterate;
```

Pre: none.
Result: the plug-in for Latin script, a `transliterate` of [plugin-api](plugin-api.md) whose answers are those of the examples of [plugin-api](plugin-api.md#transliterate). Every call returns the same table.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| the plug-in | `latin()` | a plug-in with the answers of `transliterate` |

## Fake

The real implementation: a table with no side effects, and a consumer that wants other answers passes a table of its own.
