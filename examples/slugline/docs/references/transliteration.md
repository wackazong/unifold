# transliteration

The contract of `transliteration`: a plug-in that replaces Latin letters with diacritics, and ligatures, by ASCII letters. It implements the trait of
[plugin-api](plugin-api.md).

## Coverage

- Every letter of the Unicode blocks Latin-1 Supplement and Latin Extended-A maps to its base letter or letters, in the case of the base letter.
- Ligatures map to two letters: `æ` to `ae`, `œ` to `oe`, `ĳ` to `ij`, `ß` to `ss`, `þ` to `th`.
- Any other character gets `None`.

## Examples

| Character | Answer |
|---|---|
| `é` | `e` |
| `Ø` | `o` |
| `ł` | `l` |
| `Æ` | `ae` |
| `ß` | `ss` |
| `→` | `None` |
| `я` | `None` |
