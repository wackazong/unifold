# unicode

A transliteration plug-in: it replaces Latin letters that have diacritics, and ligatures such as `æ`, by ASCII letters, so that a slug of `Crème brûlée` keeps its letters instead of losing them.

## Why

Character tables are large and a matter of taste, so they live outside the library that makes slugs, behind the trait that library defines. This crate is one such table, for Latin script. Another script is another plug-in, not a change here, and a user who wants no transliteration leaves this crate out.

## Capabilities

### `transliteration`

`transliterate('é')` returns `"e"`, `'ß'` returns `"ss"`, `'æ'` returns `"ae"`. A character that is not a Latin letter with a diacritic or a ligature is returned unchanged. The table covers Latin-1 Supplement and Latin Extended-A.

Contract: [transliteration](../../docs/references/transliteration.md). Tests:
[tests/latin.rs](tests/latin.rs).

## Needs

### `plugin-api`

The trait a transliteration plug-in implements: one method from a character to its ASCII replacement.

## Out of scope

- Scripts other than Latin: Cyrillic, Greek or CJK need a plug-in of their own.
